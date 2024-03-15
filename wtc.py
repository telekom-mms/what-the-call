#!/usr/bin/env python3
# coding: utf-8
"""
This script shows the last notifications from multiple icinga instances
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import typing
from sys import exit, stdin
import time
import select
from datetime import datetime
from getpass import getpass, getuser
import configargparse
import subprocess
from re import compile, match
from colorama import Fore, Style, ansi
from rich.console import Console
from rich.table import Table, box

def regex_parse(arg_value):
    """
    checks if the argument is a regex and compiles it - required for input validation
    """
    try:
        contact_filter = compile(arg_value)
    except:
        raise configargparse.ArgumentTypeError("invalid regex")
    return contact_filter

def generate_url(
        instance: str,
        host: str,
        service: typing.Optional[str]=None):
    """
    generates the URL to the check in the webinterface
    """
    if service is None:
        url = f"{instance}/dashboard#!/monitoring/host/show?host={host}"
    else:
        url = f"{instance}/dashboard#!/monitoring/service/show?host={host}&service={service}"
    return url

def get_recovered(
        row,
        recovered_list
        ):
    """
    checks if a recovery for the service in the row is present in recovered_list
    """
    for r_row in recovered_list:
        if (
                r_row.get("host_display_name") == row.get("host_display_name") and
                r_row.get("service_display_name") == row.get("service_display_name") and
                int(r_row.get("service_last_state_change")) > int(row.get("notification_timestamp"))
            ):
            return True
    return False

def get_instance_notifications(instance: str):
    """
    load the notifications of the supplied icinga instance
    """
    response = requests.request(
        "GET",
        f"{instance}/monitoring/list/notifications?notification_timestamp>={args.lookback}",
        headers=headers,
        auth=icinga_auth
    )
    try:
        output = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        print(f"error decoding json from {instance}. Login error?")
        exit(1)

    # get recently recovered services
    recover_req = requests.request(
        "GET",
        f"{instance}/monitoring/list/services?service_state=0&limit=500&sort=service_last_state_change&dir=desc",
        headers=headers,
        auth=icinga_auth
    )
    try:
        recovered_list = json.loads(recover_req.text)
    except json.decoder.JSONDecodeError:
        print(f"error decoding recover json from {instance}. Login error?")
        exit(1)

    # add additional information to notification list output
    for row in output:
        url = generate_url(
            instance=instance,
            host = row.get("host_name"),
            service = row.get("service_description")
            )
        recovered = get_recovered(
            recovered_list=recovered_list,
            row=row
            )
        row.update({"url": url })
        row.update({"recovered": recovered })
    return output

def sort_by_ts(elem):
    """helper function to return the timestamp from the element dict for sorting"""
    return elem.get("notification_timestamp")

def data_of_instances(instances):
    """fetches data from multiple icinga instances"""
    returns = []
    for instance in instances:
        icinga_output = get_instance_notifications(
            instance=instance
        )
        returns.extend(icinga_output)
    returns.sort(key=sort_by_ts, reverse=True)
    return returns

def show_time(ts):
    """icinga returns timestamps as unix timestamp - this produces "readable" time for the output"""
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def state_string(state):
    """maps the state number (1-3) to colored text output"""
    states = {
        '0': '[green]OK',
        '1': '[yellow]WARNING',
        '2': '[red]CRITICAL',
        '3': '[cyan]UNKNOWN'
    }
    return states.get(state, state)

def recovered_string(recovered):
    """formatting helper to print out a bool as coloured text"""
    if recovered:
        return '[green]True'
    else:
        return '[red]False'

def text_output(notifications, limit: int):
    """generates text output from fetched notifications"""
    counter = 0
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Number", style="dim", width=5)
    table.add_column("Timestamp", width=20)
    table.add_column("State")
    table.add_column("Recovered")
    table.add_column("Hostname")
    table.add_column("Service")

    for r in notifications:
        timestamp = show_time(int(r.get("notification_timestamp")))
        hostname = r.get("host_name")
        service = r.get("service_display_name")
        state = state_string(r.get("notification_state"))
        recovered = recovered_string(r.get("recovered"))

        if filter_notification(r):
            if counter < limit:
                table.add_row(
                        f"{counter+1:02d}",
                        timestamp,
                        state,
                        recovered,
                        hostname,
                        service
                    )
                counter += 1

            else:
                break

    console.print(table)

def filter_notification(notification):
    if notification.get("notification_contact_name") != None:
        if args.filter.match(notification.get("notification_contact_name")):
            return True
    return False

def check_input(notifications):
    print('press enter to refresh or enter a entry number to open the check in the web browser (using xdg-open):')
    user_input = input('([0-9]|q)> ')

    if match('[0-9]+', user_input):
        counter = 0
        for r in notifications:
            if filter_notification(r):
                counter += 1
                if counter == int(user_input):
                    url = r.get('url')
                    break
        if not args.show_urls:
            subprocess.run(['xdg-open', url])
        else:
            print(url)
            print('copy or open url and press enter to refresh screen')
            input()
    if user_input == 'q':
        exit(0)

if __name__ == "__main__":

    p = configargparse.ArgParser(
    default_config_files=['~/.config/wtc.yml'],
    config_file_parser_class=configargparse.YAMLConfigFileParser,
    formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
    )

    p.add(
        "--instance",
        "-i",
        type=str,
        help="one or more icinga instances to monitor",
        action="append",
        required=True,
    )
    p.add(
        "--lookback",
        "-l",
        type=str,
        help="how long to look back for notifications",
        default="-1 days",
    )
    p.add(
        "--limit",
        type=int,
        help="number of the last entries to display",
        default=10,
    )
    p.add(
        "--filter",
        type=regex_parse,
        help="regex filter for notification contact name",
        default=".*",
    )
    p.add(
        "--user",
        "-u",
        type=str,
        help="Login User for Icinga",
        default=getuser(),
    )
    p.add(
        "--password",
        "-p",
        type=str,
        help="Login Password for Icinga",
        default=None,
    )
    p.add(
        "--show-urls",
        action="store_true",
        help="show URLs instead of using xdg-open to open in the default browser (useful for remote shells etc)",
        default=False,
    )
    p.add(
        "--watch",
        "-w",
        action="store_true",
        help="run the output in infinite loop, refreshing automatically",
        default=False,
    )
    p.add(
        "--watch-interval",
        help="interval for updates in watch mode in seconds",
        type=int,
        default=120,
    )
    p.add(
        "--onetime",
        "-o",
        help="only output calls once and exit afterwards",
        default=False
    )

    args = p.parse_args()

    console = Console()


    # ask for password if it isn't set from the commandline
    if args.password is None:
        password = getpass(f'enter password for {args.user}:')
    else:
        password = args.password

    icinga_auth = HTTPBasicAuth(args.user, password)

    headers = {
        "Accept": "application/json"
    }

    while True:
        try:
            notifs = data_of_instances(args.instance)
            print(ansi.clear_screen())
            text_output(
                notifications=notifs,
                limit=args.limit
            )
            if args.watch:
                time.sleep(args.watch_interval)
            elif args.onetime:
                exit(0)
            else:
                check_input(notifs)
        except KeyboardInterrupt:
            exit(0)

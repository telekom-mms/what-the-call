# what the call

this script helps you find out what the last call was about by checking notifications for multiple icinga instances.

You probably need to modify the list of `icinga_instances` and maybe the `notification_filter` setting in the script before usage.


## Usage

```
usage: wtc.py [-h] --instance INSTANCE [--lookback LOOKBACK] [--limit LIMIT] [--filter FILTER] [--user USER] [--password PASSWORD] [--show-urls] [--watch] [--watch-interval WATCH_INTERVAL] [--onetime ONETIME]

options:
  -h, --help            show this help message and exit
  --instance INSTANCE, -i INSTANCE
                        one or more icinga instances to monitor (default: None)
  --lookback LOOKBACK, -l LOOKBACK
                        how long to look back for notifications (default: -1 days)
  --limit LIMIT         number of the last entries to display (default: 10)
  --filter FILTER       regex filter for notification contact name (default: .*)
  --user USER, -u USER  Login User for Icinga (default: current user login name)
  --password PASSWORD, -p PASSWORD
                        Login Password for Icinga (default: None)
  --show-urls           show URLs instead of using xdg-open to open in the default browser (useful for remote shells etc) (default: False)
  --watch, -w           run the output in infinite loop, refreshing automatically (default: False)
  --watch-interval WATCH_INTERVAL
                        interval for updates in watch mode in seconds (default: 120)
  --onetime ONETIME, -o ONETIME
                        only output calls once and exit afterwards (default: False)

Args that start with '--' (eg. --instance) can also be set in a config file (~/.config/wtc.yml). The config file uses YAML syntax and must represent a YAML 'mapping' (for details, see
http://learn.getgrav.org/advanced/yaml). If an arg is specified in more than one place, then commandline values override config file values which override defaults.

```

as described in the help output you can configure these settings via a configuration file in `~/.config/wtc.yml` as well.

### Example Configuration File

```yaml
---
instance:
  - "https://icinga1.example.com"
  - "https://icinga2.example.com"

filter: '.+call.+'

```

## Example Output of the script

```plain
user@host ~ % python3 wtc.py
enter password for user:
  Numb…   Timestamp              State      Hostname                 Service
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  01      2023-05-24 09:09:23    CRITICAL   cust1-live-prx01         cust1_availability_haproxy_backends_live_prx
  02      2023-05-24 09:08:45    CRITICAL   cust1-live-prx02         cust1_availability_haproxy_backends_live_prx
  03      2023-05-24 03:07:28    WARNING    cust1-live-int01         cust1_availability_live_api_cust1-live-int01
  04      2023-05-24 03:07:18    WARNING    cust1-live-int02         cust1_availability_live_api_cust1-live-int02
  05      2023-05-24 03:05:40    CRITICAL   cust1-live-int02         cust1_mailrelay_rz1
  06      2023-05-24 03:05:34    CRITICAL   cust1-live-int01         cust1_mailrelay_rz1
  07      2023-05-24 03:04:50    UNKNOWN    hostp-lvirt-vc01.cust1   cust1_esx_host_datastore_cust1_test_fcc02
  08      2023-05-24 03:02:49    UNKNOWN    hostp-lvirt-vc01.cust2   cust2_esx_host_datastore_fcc02
  09      2023-05-24 03:01:07    UNKNOWN    hostp-lvirt-vc01.cust1   cust1_esx_host_datastore_cust1_live_fcc02
  10      2023-05-24 03:00:42    UNKNOWN    hostp-lvirt-vc01.cust2   cust2_esx_host_datastore_fcc01

press enter to refresh or enter a entry number to open the check in the web browser (using xdg-open):
([0-9]|q)>
```

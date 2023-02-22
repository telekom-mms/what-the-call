# what the call

this script helps you find out what the last call was about by checking notifications for multiple icinga instances.

You probably need to modify the list of `icinga_instances` and maybe the `notification_filter` setting in the script before usage.


## Usage

```
usage: wtc.py [-h] --instance INSTANCE [--lookback LOOKBACK] [--limit LIMIT] [--filter FILTER] [--user USER] [--password PASSWORD]
                               [--disable-urls] [--watch] [--watch-interval WATCH_INTERVAL]

options:
  -h, --help            show this help message and exit
  --instance INSTANCE, -i INSTANCE
                        one or more icinga instances to monitor (default: None)
  --lookback LOOKBACK, -l LOOKBACK
                        how long to look back for notifications (default: -1 days)
  --limit LIMIT         number of the last entries to display (default: 10)
  --filter FILTER       regex filter for notification contact name (default: .*)
  --user USER, -u USER  Login User for Icinga (default: cise)
  --password PASSWORD, -p PASSWORD
                        Login Password for Icinga (default: None)
  --disable-urls
  --watch               run the output in infinite loop, refreshing automatically (default: False)
  --watch-interval WATCH_INTERVAL
                        interval for updates in watch mode in seconds (default: 120)

Args that start with '--' (eg. --instance) can also be set in a config file (~/.config/wtc.yml). The config file uses YAML syntax and must represent
a YAML 'mapping' (for details, see http://learn.getgrav.org/advanced/yaml). If an arg is specified in more than one place, then commandline values override
config file values which override defaults.
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
01 | 2023-02-21 16:15:51 | WARN | cust1-live-web02 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-live-web02&service=cust1_disk
02 | 2023-02-21 16:14:54 | WARN | cust1-live-web01 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-live-web01&service=cust1_disk
03 | 2023-02-21 15:46:54 | WARN | cust1-live-web01 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-live-web01&service=cust1_disk
04 | 2023-02-21 15:46:45 | WARN | cust1-live-web02 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-live-web02&service=cust1_disk
05 | 2023-02-21 15:26:54 | WARN | cust1-live-web01 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-live-web01&service=cust1_disk
06 | 2023-02-21 15:25:23 | WARN | cust1-live-web02 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-live-web02&service=cust1_disk
07 | 2023-02-21 14:39:29 | CRIT | cust1-mgmt-sst01 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-mgmt-sst01&service=cust1_disk
08 | 2023-02-21 14:33:55 | CRIT | cust2-live-web03 | cust2_cronjob_foo
   `-https://icinga2.example.com/dashboard#!/monitoring/service/show?host=cust2-live-web03&service=cust2_cronjob_foo
09 | 2023-02-21 14:29:52 | WARN | cust1-mgmt-sst01 | cust1_disk
   `-https://icinga1.example.com/dashboard#!/monitoring/service/show?host=cust1-mgmt-sst01&service=cust1_disk
10 | 2023-02-21 13:14:27 | CRIT | cust2-live-web02 | cust2_cronjob_bar
   `-https://icinga2.example.com/dashboard#!/monitoring/service/show?host=cust2-live-web02&service=cust2_cronjob_bar
```

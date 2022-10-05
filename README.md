# NetWatch

Simple home network monitor.

My internet takes a dump at inconvenient times (like meetings) and I never know if it is the internet provider or my home router that has been running 24x7 for years.

So I created this litle tool to ping a bunch of targets (that you specify in a config file) and write the results to a CSV file that you can then open in Excel and graph easily.

usage: NetWatch.py [-h] -c CONFIG -o OUTPUT [-q]

Home Network Watcher

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file to use.
  -o OUTPUT, --output OUTPUT
                        file to write to
  -q, --quiet           will not print out status

You can specify any targets as you like in the config file, an example is provided (NetWatch.ini).

# nwAnalyzer
The 2nd part of the tool, allows you to run a quick analysis of the data in the CSV file. 

usage: nwAnalyzer.py [-h] -c CONFIG -i INPUT [-l LAST]

Analyzer for the Home Network Watcher

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file to use.
  -i INPUT, --input INPUT
                        The .CSV file to read data from.
  -l LAST, --last LAST  will run the report on the data from the last # of seconds specified you can specify an
                        optional suffix (with no space): s: seconds (default) m: minutes (example: 32m) h: hours
                        (example: 12h) d: days (example: 3d)

I monitor the items listed in the example NetWatch.ini file.  Using this I can figure out where a failure ocurred.  If I can access my internal targets but not an outside target then I know it was an internet failure.  If I can't access anything then likely problem is my router or something else internal.
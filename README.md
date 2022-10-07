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
The 2nd part of the tool, allows you to run a quick analysis of the data in the CSV
<pre>
usage: nwAnalyzer.py [-h] -c CONFIG -i INPUT [-l LAST]

Analyzer for the Home Network Watcher

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file to use.
  -i INPUT, --input INPUT
                        The .CSV file to read data from.
  -l LAST, --last LAST  will run the report on the data from the last # of seconds specified you can specify an
                        (example: 12h) d: days (example: 3d)
</pre>
I monitor the items listed in the example NetWatch.ini file.  Using this I can figure out where a failure ocurred.  If I can access my internal targets but not an outside target then I know it was an internet failure.  If I can't access anything then likely problem is my router or something else internal.

Example output:
<pre>
Google DNS Server IP: [99.64% uptime over 3 days, 3:31:22]
        Success 4528, Failures 16 [most recent - 2022-10-07 11:44:55]
        Average time: 5.75ms
        Max time: 28.58ms
        Min time: 4.85ms

Google: [99.64% uptime over 3 days, 3:31:22]
        Success 4528, Failures 16 [most recent - 2022-10-07 11:44:55]
        Average time: 5.81ms
        Max time: 10.33ms
        Min time: 4.78ms

Home Media Server: [99.86% uptime over 3 days, 3:31:22]
        Success 4538, Failures 6 [most recent - 2022-10-04 14:02:43]
        Average time: 0.85ms
        Max time: 22.64ms
        Min time: 0.14ms

Home Router: [99.88% uptime over 3 days, 3:31:22]
        Success 4539, Failures 5 [most recent - 2022-10-04 14:02:33]
        Average time: 0.97ms
        Max time: 250.22ms
        Min time: 0.2ms

Public IP Address Changes: [Current IP-->50.54.174.104
        50.38.37.157-->x.x.x.x  [2022-10-04 13:18:54]
        x.x.x.x-->50.54.174.104 [2022-10-04 13:19:32]
        50.54.174.104-->x.x.x.x [2022-10-04 14:01:44]
        x.x.x.x-->50.54.174.104 [2022-10-04 14:02:43]
        50.54.174.104-->x.x.x.x [2022-10-07 11:44:22]
        x.x.x.x-->50.54.174.104 [2022-10-07 11:44:55]
</pre>


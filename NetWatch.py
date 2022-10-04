"""
Copyright (c) 2022, Patrick Kutch
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""
import os
from datetime import datetime
import time
import urllib.request
import configparser
import argparse
import sys


__author__ = "Patrick Kutch"
__license__ = "BSD"
__version__ = "22.10.04"
__maintainer__ = "Patrick Kutch"
__email__ = "Patrick.Kutch@gmail.com"
__status__ = "Production"

defaultPingTimeoutTime = 1
defaultPingInterval = 60
defaultPingIntervalWhenFailure = 0
defaultFailureValue = -100


def getPublicIp():
    """Attempts get the public IP address of your network

    Returns:
    string: If successful, the public IP address, else 'x.x.x.x'
    """
    try:
        return urllib.request.urlopen("https://ident.me").read().decode("utf8")
    except:
        return "x.x.x.x"


def pingTarget_AvgMs(target: str, unableToPingVal: int, timeoutVal: int) -> int:
    """Attempts a ping a target

    Parameters:
    Target (str): The target IP/DNS naem to poing
    unableToPingVal (int): value to write to the CSV file if the ping fails for a target
    timeout (int): time (seconds) to wait for a ping response before failing

    Returns:
    int: average ping time for target if successful, else the unableToPing Val
    """
    try:
        response = ping(target, timeout=timeoutVal)
    except:
        return unableToPingVal

    if 0 == response.stats_packets_returned:
        return unableToPingVal

    return response.rtt_avg_ms


def doPingRun(Targets: dict, unableToPingVal: int, timeout: int) -> tuple:
    """Attempts a ping to all of the targets.

    Parameters:
    Targets (dict (from config file)): The targets specified in [TARGETS] section of confi file
    unableToPingVal (int): value to write to the CSV file if the ping fails for a target
    timeout (int): time (seconds) to wait for a ping response before failing

    Returns:
    tuple(bool,[avg_ping_ms]: bool=False if any failures, else True. List of average ping time for each target
    """
    retList = []
    packetLoss = False
    for target in Targets:
        desc = Targets[target]
        avgMs = pingTarget_AvgMs(target, unableToPingVal, timeout)
        retList.append((desc, avgMs))
        if int(unableToPingVal) == int(avgMs):
            packetLoss = True

    return (packetLoss, retList)


def writeData(dataList, fileName, externalIp) -> None:
    """Writes the collected data to the specified file, in CSV format

    Parameters:
    dataList (tuple[]): array of (human readable target,avg_ms ping time)
    fileName (str): the filename to write the data to
    externalIp (str): the public IP address of your system
    """

    now = datetime.now()  # current date and time

    if not os.path.exists(fileName):  # 1st time writing file, so put in column headers
        header = "Public IP, Date, Time"
        for target, _ in dataList:
            header += ", {}".format(target)

        header += "\n"
        with open(fileName, "wt+") as fp:
            fp.write(header)

    row = "{}, {}, {}".format(
        externalIp, now.strftime("%m/%d/%Y"), now.strftime("%H:%M:%S")
    )
    for _, pingTimeInMs in dataList:
        row += ", {}".format(pingTimeInMs)

    row += "\n"
    try:
        with open(fileName, "a") as fp:  # open in append mosde
            fp.write(row)

    except PermissionError as Ex:
        print(f"Unable to open {fileName} for writing")


def readConfig(configFile: str) -> configparser.ConfigParser:
    """Reads the config file

    Parameters:
    configFile (str): The configuration file name

    Returns:
    configparser.ConfigParser:configparser object
    """
    config = configparser.ConfigParser()
    config.read(configFile)

    return config


def VerifyConfig(config) -> bool:
    """Checks to see if the config file has all the correct pieces
        and uses default values when possible

    Parameters:
    config (configparser.ConfigParser()): The configuration object

    Returns:
    bool:True if valid, False if not

    """
    if not "TARGETS" in config:
        print("Specified configuration file does not contain [TARGETS] section")
        return False

    if len(config["TARGETS"]) < 1:
        print("No Targets listed in [TARGETS] section ov the configuration file")
        return False

    if not "SETTINGS" in config:
        print(
            "Specified configuration file does not contain [SETTINGS] section, using defaults"
        )
        config["Settings"] = {}

    if not "PingTimeoutTime" in config["SETTINGS"]:
        config["SETTINGS"]["PingTimeoutTime"] = str(defaultPingTimeoutTime)

    if not "PingInterval" in config["SETTINGS"]:
        config["SETTINGS"]["PingInterval"] = str(defaultPingInterval)

    if not "PingIntervalWhenFailure" in config["SETTINGS"]:
        config["SETTINGS"]["PingIntervalWhenFailure"] = str(
            defaultPingIntervalWhenFailure
        )

    if not "FailureValue" in config["SETTINGS"]:
        config["SETTINGS"]["FailureValue"] = str(defaultFailureValue)

    try:
        int(config["SETTINGS"]["PingInterval"])
    except ValueError:
        print("PingInterval must be a number")
        return False

    try:
        int(config["SETTINGS"]["PingIntervalWhenFailure"])
    except ValueError:
        print("PingIntervalWhenFailure must be a number")
        return False

    try:
        int(config["SETTINGS"]["FailureValue"])
    except ValueError:
        print("FailureValue must be a number")
        return False

    return True


def main():
    print(f"NetWatch v{__version__}")

    parser = argparse.ArgumentParser(description="Home Network Watcher")
    parser.add_argument(
        "-c", "--config", help="Configuration file to use.", type=str, required=True
    )
    parser.add_argument(
        "-o", "--output", help="file to write to", type=str, required=True
    )
    parser.add_argument(
        "-q", "--quiet", help="will not print out status", action="store_true"
    )

    args = parser.parse_args()
    if not os.path.exists(args.config):
        print("Specified configuration file {} does not exist".format(args.config))
        return

    config = readConfig(args.config)

    if not VerifyConfig(config):
        return

    print("Press CTRL+C to exit")

    loopNum = 1
    failCount = 0
    successCount = 0
    pingTimeoutTime = int(config["SETTINGS"]["PingTimeoutTime"])
    while True:
        startTime = time.time()

        packetLoss, dataList = doPingRun(
            config["TARGETS"],
            config["SETTINGS"]["FailureValue"],
            pingTimeoutTime,
        )
        currIP = getPublicIp()
        writeData(dataList, args.output, currIP)

        endTime = time.time()

        duration = endTime - startTime  # so we run on the desired interval

        if packetLoss:
            failCount += 1
            sleepTime = int(config["SETTINGS"]["PingIntervalWhenFailure"]) - duration

        else:
            sleepTime = int(config["SETTINGS"]["PingInterval"]) - duration
            successCount += 1

        if not args.quiet:
            print(
                "Ping #{} - Successes-{} Failures-{}".format(
                    loopNum, successCount, failCount
                ),
                end="\r",
            )

        if sleepTime < 0:  # in case the timeouts are longer than the interval specified
            sleepTime = 0

        time.sleep(sleepTime)

        loopNum += 1


if __name__ == "__main__":
    try:  # make sure pythonping is installed
        from pythonping import ping

        main()

    except ModuleNotFoundError as ex:
        print("ERROR: pythonping module must be installed.")

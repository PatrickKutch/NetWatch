"""
Copyright (c) 2022, Patrick Kutch
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""
import os
from datetime import datetime
from datetime import timedelta
import argparse
import NetWatch

__author__ = "Patrick Kutch"
__license__ = "BSD"
__version__ = "22.10.05"
__maintainer__ = "Patrick Kutch"
__email__ = "Patrick.Kutch@gmail.com"
__status__ = "Production"

# global var
config = None


def getDateTimeByRow(dataSet, rowNumber) -> datetime:
    """Retrieves date and time from a specified row.

    Parameters:
    dataSet (pandas ds): the data from the CSV fie
    rowNumber (int): which row to get the data from

    Returns:
    datetime: the datetime object represeting the date and time of the row
    """
    try:
        date = dataSet["Date"][rowNumber].strip()
        time = dataSet["Time"][rowNumber].strip()
    except:  # likely the row number is invalid, or Date and Time not in the file!
        return None

    dateTimeStr = date + time
    return datetime.strptime(dateTimeStr, "%m/%d/%Y%H:%M:%S")


def doReportForTarget(dataSet, target: str) -> None:
    """Prints a report for the specified target

    Parameters:
    dataSet (pandas ds): the data from the CSV fie
    target (str): which target column to do the report on
    """

    targDsAll = dataSet[target]
    totalPoints = len(targDsAll)
    # do not include the failures
    targDsValid = targDsAll[targDsAll != int(config["SETTINGS"]["FailureValue"])]
    totalValidPoints = len(targDsValid)

    # calculate time span for data collection
    startRow = targDsAll.index[
        0
    ]  # could modify config file to add/remove targets, so don't assume all are the same
    endRow = targDsAll.index[-1]
    startTime = getDateTimeByRow(dataSet, startRow)
    endTime = getDateTimeByRow(dataSet, endRow)
    timeSpan = endTime - startTime
    avg1 = (int(targDsAll.mean(axis=0) * 100)) / 100
    max1 = targDsValid.max()
    min1 = targDsValid.min()
    successRate = int(totalValidPoints / totalPoints * 10000) / 100

    print("{}: [{}% uptime over {}]".format(target, successRate, timeSpan))
    print(
        "\tSuccess {}, Failures {}".format(
            totalValidPoints, totalPoints - totalValidPoints
        )
    )

    print("\tAverage time: {}ms".format(avg1))
    print("\tMax time: {}ms".format(max1))
    print("\tMin time: {}ms".format(min1))

    print()


def trimDataSetByLast(dataSet, timePeriodStr: int):
    """Returns a subset of the data from the CSV file, the last # of seconds worth

    Parameters:
    dataSet (pandas ds): the data from the CSV fie
    timePeriod (str): how long to go 'back' to.  Can have 's'|'m'|'h' for seconds, minutes hours

    Returns:
    pandas ds: the last specified # of seconds of the input dataset
    """

    startTime = getDateTimeByRow(dataSet, 0)
    endTime = getDateTimeByRow(dataSet, dataSet.index[-1])
    try:
        timePeriod = int(timePeriodStr)

    except ValueError:  # user specifed units
        try:
            timePeriod = int(timePeriodStr[:-1])
        except ValueError:  # bad juju
            print("invalid -l/--last  time period specified: {}".format(timePeriodStr))
            return (False, None)

        unit = timePeriodStr[-1].lower()
        if unit == "s":  # seconds
            pass  # already calc based on seconds

        elif unit == "m":  # minutes
            timePeriod *= 60

        elif unit == "h":  # hours
            timePeriod *= 60 * 60

        elif unit == "d":  # days
            timePeriod *= 60 * 60 * 24

        else:
            print("invalid -l/--last  time period specified: {}".format(timePeriodStr))
            return (False, None)

    roughStartTime = endTime - timedelta(seconds=timePeriod)

    if roughStartTime > startTime:
        # specified time less than what is in file, so let's find and trim
        for index in range(dataSet.index[-1], 0, -1):
            if getDateTimeByRow(dataSet, index) < roughStartTime:
                dataSet = dataSet[index + 1 :]
                break  # found cut off point and trimmed

    return (True, dataSet)


def reportPublicIP(dataSet):
    """Prints a report of the recored public IP

    Parameters:
    dataSet (pandas ds): the data from the CSV fie
    """
    dataCol = dataSet["Public IP"]
    ipList = dataCol.unique()
    if len(ipList) > 1:
        prevIP = dataCol[0]
        print("Public IP Address Changes: [Current IP-->{}".format(ipList[-1]))
        for index, currIP in enumerate(dataSet["Public IP"]):
            if currIP != prevIP:
                print(
                    "\t{}-->{}\t[{}]".format(
                        prevIP, currIP, getDateTimeByRow(dataSet, index)
                    )
                )
                prevIP = currIP

    else:
        print("No Public IP Address Changes Detected: [Current IP-->{}".format(ipList))

    print()


def main():
    print(f"NetWatch Analyzer v{__version__}")

    parser = argparse.ArgumentParser(
        description="Analyzer for the Home Network Watcher"
    )
    parser.add_argument(
        "-c", "--config", help="Configuration file to use.", type=str, required=True
    )
    parser.add_argument(
        "-i",
        "--input",
        help="The .CSV file to read data from.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-l",
        "--last",
        help="""will run the report on the data from the last # of seconds specified
                you can specify an optional suffix (with no space):
                  s: seconds (default)
                  m: minutes (example: 32m)
                  h: hours (example: 12h)
                  d: days (example: 3d)""",
        type=str,
    )

    args = parser.parse_args()
    if not os.path.exists(args.config):
        print("Specified configuration file {} does not exist".format(args.config))
        return

    if not os.path.exists(args.input):
        print("Specified input (CSV)  file {} does not exist".format(args.input))
        return
    global config
    config = NetWatch.readConfig(args.config)

    if not NetWatch.VerifyConfig(config):
        return

    dataSet = pd.read_csv(args.input)

    if args.last:
        success, dataSet = trimDataSetByLast(dataSet, args.last)
        if False == success:
            return  # error ocurred, message already printed

    targets = dataSet.columns[3:]

    if targets.size < 1:
        print("No info found in input file {}".format(args.input))
        return

    for targ in targets:
        doReportForTarget(dataSet, targ)

    reportPublicIP(dataSet)


if __name__ == "__main__":
    try:  # make sure pythonping is installed
        import pandas as pd

        main()

    except ModuleNotFoundError as ex:
        print("ERROR: pandas module must be installed.")

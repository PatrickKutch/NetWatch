"""
Copyright (c) 2022, Patrick Kutch
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""
import os
from datetime import datetime
import argparse
import NetWatch

__author__ = "Patrick Kutch"
__license__ = "BSD"
__version__ = "22.10.05"
__maintainer__ = "Patrick Kutch"
__email__ = "Patrick.Kutch@gmail.com"
__status__ = "Production"

config = None


def getDateTimeByRow(dataSet, rowNumber) -> tuple:
    try:
        date = dataSet["Date"][rowNumber].strip()
        time = dataSet["Time"][rowNumber].strip()
    except:  # likely the row number is invalid, or Date and Time not in the file!
        return None

    dateTimeStr = date + time
    return datetime.strptime(dateTimeStr, "%m/%d/%Y%H:%M:%S")


def doReport(dataSet, target: str) -> None:
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


def main():
    print(f"NetWatch Analyzer v{__version__}")

    parser = argparse.ArgumentParser(description="Home Network Watcher")
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
        "-o", "--output", help="file to write to", type=str, required=True
    )

    parser.add_argument(
        "-l",
        "--last",
        help="will run the report on the data from the last # of seconds specified",
        type=int,
    )

    parser.add_argument(
        "-q", "--quiet", help="will not print out status", action="store_true"
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

    targets = dataSet.columns[3:]

    if targets.size < 1:
        print("No info found in input file {}".format(args.input))
        return

    for targ in targets:
        doReport(dataSet, targ)


if __name__ == "__main__":
    try:  # make sure pythonping is installed
        import pandas as pd

        main()

    except ModuleNotFoundError as ex:
        print("ERROR: pandas module must be installed.")

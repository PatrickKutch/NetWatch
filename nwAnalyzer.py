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
__version__ = "22.10.04"
__maintainer__ = "Patrick Kutch"
__email__ = "Patrick.Kutch@gmail.com"
__status__ = "Production"

config = None


def doReport(dataSet, target: str) -> None:
    targDsAll = dataSet[target]
    x = len(targDsAll)
    # do not include the failures
    targDsValid = targDsAll[targDsAll != int(config["SETTINGS"]["FailureValue"])]
    y = len(targDsValid)
    mean1 = targDsValid.mean()
    max1 = targDsValid.max()
    min1 = targDsValid.min()
    median1 = targDsValid.median()
    std1 = targDsValid.std()
    var1 = targDsValid.var()
    print(target)
    print("\tMean time: " + str(mean1))
    print("\tMax time: " + str(max1))
    print("\tMin time: " + str(min1))
    print("\tMedian time: " + str(median1))
    print("\tSuccess {}, Failures {}".format(y, x - y))
    #    print("\tStd of time: " + str(std1))
    #    print("\tVar of time: " + str(var1))

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
    # print(dataSet)
    # x = dataSet.columns
    # print(x)
    targets = dataSet.columns[3:]
    # print(targets)

    for targ in targets:
        doReport(dataSet, targ)


if __name__ == "__main__":
    try:  # make sure pythonping is installed
        import pandas as pd

        main()

    except ModuleNotFoundError as ex:
        print("ERROR: pandas module must be installed.")

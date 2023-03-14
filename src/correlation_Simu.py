#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: File to run correlation for the tanks benchmark
#################################################################################################################

import numpy as np
import pandas as pd

import correlation as corr
import ruleWriter as rw
import helper

def run_correlationSimu(path, thresholds, until=-1, prefix=""):

    processData = pd.read_csv(path).iloc[0:until,:]

    measurementCols, toDelete = helper.filterColumns(processData.columns)
    processData.drop(toDelete, axis=1, inplace=True)
    print(measurementCols)

    mergedData = processData
    print(mergedData.columns)
    mergedData.drop("time", axis=1, inplace=True)

    print("Dimensions merged: ", mergedData.shape)
    print("num na merge: ", np.sum(mergedData.isna()))

    results = corr.runSpearman(mergedData, thresholds)

    for t in results.keys():
        edges = results[t][0]
        rw.correlationTupleToRules(edges, measurementCols, "output/corrSimu"+prefix+str(t)+".txt")
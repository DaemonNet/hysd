import numpy as np
import pandas as pd
import os
import glob

from pandas.core.reshape.merge import merge


import granger
import ruleWriter as rw

def run_grangerAbsoluteSimu(path):    
    directories = [x[0] for x in os.walk(path)][1:]
    
    for entry in directories:
        print("generated path: ", entry)
        try:
            run(entry+"\\*.csv", entry)
        except Exception as e:
            print(e)
            print("Das wahr wohl nix")
            continue

def run(pathData, entry):
    outlist = []
    data = None
    measurementCols = []
    print("Loading data....")
    for file in glob.glob(pathData):
        print(file)
        if os.path.basename(file) == "COMPS.csv":
            continue

        processData = pd.read_csv(file) # Dataframe
        print("Resulting shape: ", processData.shape)
        
        for c in processData.columns:
            #if ("volumeFlowRate" and  "V_flow") or "level" in c:
            if "V_flow" and "level" in c:
                measurementCols.append(c)

        if data is None:
            data = dict()
        
            for c in processData.columns:
                data[c] = processData[c]
        else:
            for c in processData.columns:
                if c in data.keys():
                    data[c] = data[c].append(processData[c])
                else:
                    data[c] = processData[c]
    
    list_keys = list(data.keys())
    for k in list_keys:
        if k.startswith('$'):
            data.pop(k)
    print("measurementCols: ", measurementCols)
    mergedData = pd.DataFrame.from_dict(data)
    #mergedData = processData
    #mergedData.drop("time", axis=1, inplace=True)

    print("Dimensions merged: ", mergedData.shape)
    print("num na merge: ", np.sum(mergedData.isna()))

    granger.perform_adf_tests(mergedData, repetitions=10, pvalueTau=0.05)

    mergedData.loc[:, (mergedData != mergedData.iloc[0]).any()] 
    print("Post strange line: ", mergedData.shape)
    for column in mergedData.columns:
        sd = np.std(mergedData[column])
        if sd<0.001:
            #continue
            mergedData.drop(column, axis=1, inplace=True)
    #AIC test
    print("Pre AIC: ", mergedData.shape)
    granger.calculateAIC(mergedData, repetitions=4)

    
    COMPS_substitute = []

    for c in mergedData.columns:
        if c not in measurementCols:
            COMPS_substitute.append(c)

    result = granger.create_matrix(mergedData, variables = mergedData.columns)
    newpath = os.path.basename(entry).split("_")[1]

    for c in result.columns:
        if c in measurementCols:
            print("!",c)
    tau=0.05
    result[result<tau] = 0
    result[result>=tau] = 1
    fileRules = open("output/"+newpath, "w")
    for i in range(0,result.shape[0]):
        outstr=""
        label=str(result.iloc[i,:].name).split("_")[0]
        if label not in COMPS_substitute:
            for j in range(0,result.shape[1]):
                if result.iloc[i,j] > 0:
                    name = str(result.columns[j])
                    name = name.replace("_x","")
                    if name in COMPS_substitute:
                        if outstr=="":
                            outstr=name
                        else:
                            outstr += " AND " + name
            if outstr!="":
                outstr += " IMPLIES "
                if label in measurementCols:           
                    outstr += label
                    outlist.append(outstr)
    outlist=list(set(outlist))
    for item in outlist:
        fileRules.write(item+"\n")
    fileRules.close()
    print("done")
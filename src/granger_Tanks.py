#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: File to run Granger Causality on the tanks system benchmark
#################################################################################################################

import numpy as np
import pandas as pd
import os
import glob


import granger
import helper
import dataToDiagnosis as dtd
import ruleWriter as rw

#Iterate over all directories (all tank systems)
def run_TanksSimulations(path):
    directories = [x[0] for x in os.walk(path)][1:]
    for entry in directories:
        print("generated path: ", entry)
        run(entry+"\\*.csv", entry+"\\COMPS.csv", entry)

def run(pathData, pathMeta, entry):
    outlist = []
    print("Loading data....")
    #Iterate over all files within the directory
    for file in glob.glob(pathData):
        print(file)
        if os.path.basename(file) == "COMPS.csv":
            continue #Don't use the COMPS file, which is also csv

        
        processData = pd.read_csv(file) # Dataframe
        print("Resulting shape: ", processData.shape)

        measurementCols, dummy = helper.filterColumns(processData.columns)
        measurementCols.append("time")

        processData = processData[measurementCols]

        metadata = pd.read_csv(pathMeta, header=None)
        for column in metadata.columns:
            metadata[column] = metadata[column].str.strip()

        COMPONENTS = metadata.iloc[2,1:].to_numpy() #Read vom COMPS.csv
        

        FAULT_INDEX = int(metadata.iloc[0,1]) #Read vom COMPS.csv
        FAULTMODES = dict()
        for i in range(3,len(metadata)):
            FAULTMODES[metadata.iloc[i,0]] = metadata.iloc[i,1:] #Read vom COMPS.csv

        faultname = os.path.basename(file).split(".")[0]
        faultname = faultname.split("_")
        faultname = faultname[len(faultname)-1]
        INJECTED_FAULT = FAULTMODES[faultname].dropna().to_numpy()

        #print("FAULT_INDEX: ", FAULT_INDEX)
        #print("COMPONENTS: ", COMPONENTS)
        #print("INJECTED_FAULT: ", INJECTED_FAULT)

        


        #Create observations
        OBS = dtd.makeOBS(processData, processData.columns)

        #Create component matrix and set faulty columns/rows to 1
        COMPS = dtd.makeCOMPS(processData, COMPONENTS)
        for fault in INJECTED_FAULT:
            bin = processData["time"] > FAULT_INDEX
            COMPS[fault][bin]=1
            
        #Compatibility with TE code
        anomalylist = INJECTED_FAULT

        #print("COMPS: ", COMPS)
        OBS.drop("time", axis=1, inplace=True)

        COMPS = dtd.removeUseless(COMPS)    
            

        #Merge to one dataset
        mergedData= pd.concat([COMPS, OBS], axis=1)
        #print("mergedData: ", mergedData.columns)
        mergedData.astype(float)
        print("Pre ADF: ", mergedData.shape)
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
        print("OBS: ", OBS.shape)
        print("COMPS: ", COMPS.shape)
        granger.calculateAIC(mergedData, repetitions=7)

        result = granger.create_matrix(mergedData, variables = mergedData.columns)

        if len(os.path.basename(entry).split("_")) > 1:
            newpath = os.path.basename(entry).split("_")[1]
        else:
            newpath = os.path.basename(entry)

        rw.grangerMatrixToRules(result, COMPONENTS, "output/Granger"+newpath+".txt", tau=0.05, outlist=outlist, writeFile=False)
        print("Length of outlist: ", len(outlist))
    rw.writeFile("output/Granger"+newpath+".txt", outlist) #Write all rules into only one file. Intermediate rules are saved in outlist
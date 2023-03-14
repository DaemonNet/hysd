#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: Run Granger on the TE process. This takes a long time!
# Therefore intermediate files are saved after loading. Also, faults need to be explicitly specified in code. 
# This was done manually and laboriously
#################################################################################################################

import numpy as np
import pandas as pd
import pickle as pkl

import granger
import dataToDiagnosis as dtd
import ruleWriter as rw

def run_TESimulation(path, STORE=False):


    if STORE:
        #Get all files that we need
        print("Loading data....")
        alarmData = pd.read_excel(path+"/1/1_Original/ALARMS.xlsx", engine='openpyxl') # Dataframe
        for i in range(2,100):
            print("Integrating file: ", i)
            tempData = pd.read_excel(path+"/"+str(i)+"/1_Original/ALARMS.xlsx", engine='openpyxl')
            alarmData = alarmData.append(tempData, ignore_index=True)
        
        print("Resulting shape: ", alarmData.shape)
        print("Saving....")
        file = open("alarmData.pkl",'wb')
        pkl.dump(alarmData, file)
        file.close()
    else:
        file = open("alarmData.pkl",'rb')
        alarmData = pkl.load(file)
        file.close()

    if STORE:
        #Get all files that we need
        print("Loading data....")
        processData = pd.read_excel(path+"1/1_Original/SIMOUT.xlsx", engine='openpyxl') # Dataframe
        for i in range(2,100):
            print("Integrating file: ", i)
            tempData = pd.read_excel(path+"/"+str(i)+"/1_Original/SIMOUT.xlsx", engine='openpyxl')
            processData = processData.append(tempData, ignore_index=True)
        
        print("Resulting shape: ", alarmData.shape)
        print("Saving....")
        file = open("processData.pkl",'wb')
        pkl.dump(processData, file)
        file.close()
    else:
        file = open("processData.pkl",'rb')
        processData = pkl.load(file)
        file.close()

    COMPONENTS = ["vA","vD","vE","vC","condenser","separator","reactor","stripper","pump","vPurge","vProduct", "vVaporStripper"]
    INJECTED_FAULT = dict({1: [["vC"],["vC"],["vE"]],
                        2: [["condenser"],["vC"],["vE"]],
                        3: [["vC"],["vA"],["vE"]],
                        4: [["vC"],["vC"],["vE"]],
                        5: [["vC"],["condenser"],["vE"]],
                        6: [["vC"],["vA"],["vE"]],
                        7: [["condenser"],["vC"],["vE"]],
                        8: [["vC"],["vA"],["vE"]],
                        9: [["condenser"],["vA"],["vE"]],
                        10: [["vA"],["condenser"],["vE"]],
                        11: [["vC"],["vA"],["vA"]],
                        12: [["condenser"],["vC"],["vA"]],
                        13: [["vC"],["vC"],["vA"]],
                        14: [["vA"],["vC"],["vA"]],
                        15: [["vC"],["vA"],["vA"]],
                        16: [["vC"],["condenser"],["vA"]],
                        17: [["condenser"],["vC"],["vA"]],
                        18: [["vC"],["vA"],["vA"]],
                        19: [["vA"],["condenser"],["vA"]],
                        20: [["condenser"],["vA"],["vA"]],
                        21: [["vC"],["condenser"],["vC"]],
                        22: [["vC"],["vC"],["vC"]],
                        23: [["vC"],["vA"],["vC"]],
                        24: [["vA"],["vC"],["vC"]],
                        25: [["vC"],["vC"],["vC"]],
                        26: [["vC"],["condenser"],["vC"]],
                        27: [["condenser"],["vC"],["vC"]],
                        28: [["vC"],["vA"],["vC"]],
                        29: [["condenser"],["vA"],["vC"]],
                        30: [["vA"],["condenser"],["vC"]],
                        31: [["vC"],["vA"],["vPurge"]],
                        32: [["vA"],["vC"],["vPurge"]],
                        33: [["vC"],["vC"],["vPurge"]],
                        34: [["condenser"],["vC"],["vPurge"]],
                        35: [["vC"],["vC"],["vPurge"]],
                        36: [["vC"],["condenser"],["vPurge"]],
                        37: [["condenser"],["vC"],["vPurge"]],
                        38: [["vC"],["vA"],["vPurge"]],
                        39: [["vA"],["condenser"],["vPurge"]],
                        40: [["condenser"],["vA"],["vPurge"]],
                        41: [["vC"],["condenser"],["vA"]],
                        42: [["vC"],["vC"],["vA"]],
                        43: [["vC"],["vA"],["vA"]],
                        44: [["condenser"],["vC"],["vA"]],
                        45: [["vA"],["vC"],["vA"]],
                        46: [["vC"],["vA"],["vA"]],
                        47: [["condenser"],["vC"],["vA"]],
                        48: [["vA"],["vC"],["vA"]],
                        49: [["vC"],["condenser"],["vA"]],
                        50: [["condenser"],["vA"],["vA"]],
                        51: [["vC"],["vC"],["vA"]],
                        52: [["condenser"],["vC"],["vA"]],
                        53: [["vC"],["vA"],["vA"]],
                        54: [["vC"],["vC"],["vA"]],
                        55: [["vA"],["vC"],["vA"]],
                        56: [["vC"],["condenser"],["vA"]],
                        57: [["vA"],["vC"],["vA"]],
                        58: [["condenser"],["vC"],["vA"]],
                        59: [["vC"],["condenser"],["vA"]],
                        60: [["condenser"],["vA"],["vA"]],
                        61: [["condenser"],["vC"],["vE"]],
                        62: [["vC"],[["vC"],["condenser"]],["vE"]],
                        63: [[["vC"],["condenser"]],["vA"],["vE"]],
                        64: [["vC"],[["vC"],["condenser"]],["vE"]],
                        65: [[["vC"],["condenser"]],["vA"],["vE"]],
                        66: [["condenser"],["vC"],["vE"]],
                        67: [[["vC"],["condenser"]],["condenser"],["vE"]],
                        68: [["vC"],["vC"],["vE"]],
                        69: [["vPurge"],[["vC"],["condenser"]],["vE"]],
                        70: [["vA"],["vC"],["vE"]],
                        71: [[["vC"],["condenser"]],["vC"],["vA"]],
                        72: [["vA"],["vC"],["vA"]],
                        73: [["condenser"],[["vC"],["condenser"]],["vA"]],
                        74: [["vC"],["vC"],["vA"]],
                        75: [[["vC"],["condenser"]],[["vC"],["condenser"]],["vA"]],
                        76: [["vC"],["vC"],["vA"]],
                        77: [[["vC"],["condenser"]],["condenser"],["vA"]],
                        78: [["vA"],["vPurge"],["vA"]],
                        79: [["condenser"],[["vC"],["condenser"]],["vA"]],
                        80: [["vC"],["vA"],["vA"]],
                        81: [["vC"],[["vC"],["condenser"]],["vC"]],
                        82: [["vC"],[["vC"],["condenser"]],["vC"]],
                        83: [[["vC"],["condenser"]],["vC"],["vC"]],
                        84: [["vA"],["condenser"],["vC"]],
                        85: [[["vC"],["condenser"]],["vC"],["vC"]],
                        86: [["vC"],["vPurge"],["vC"]],
                        87: [[["vC"],["condenser"]],["vA"],["vC"]],
                        88: [["vA"],[["vC"],["condenser"]],["vC"]],
                        89: [[["vC"],["condenser"]],[["vC"],["condenser"]],["vC"]],
                        90: [["condenser"],["vC"],["vC"]],
                        91: [["vC"],["vC"],["vPurge"]],
                        92: [["vA"],[["vC"],["condenser"]],["vPurge"]],
                        93: [["vC"],["vC"],["vPurge"]],
                        94: [["vPurge"],[["vC"],["condenser"]],["vPurge"]],
                        95: [["condenser"],["vC"],["vPurge"]],
                        96: [["condenser"],[["vC"],["condenser"]],["vPurge"]],
                        97: [["vC"],["vC"],["vPurge"]],
                        98: [[["vC"],["condenser"]],["vC"],["vPurge"]],
                        99: [["vC"],[["vC"],["condenser"]],["vPurge"]],
                        100: [["vA"],["vC"],["vPurge"]]})
    columnsProcessData= ["FlowA","FlowD","FlowE","FlowC","FlowCRC","FlowReactorFeed","PressureReactor","LevelReactor","TempReactor","FlowPurge","TempSeparator","LevelSeparator","PressureSeparator","UnderflowSeparator","LevelStripper","PressureStripper","UnderflowStripper","TempStripper","FlowStripperSteam","CompressorWork","tempCoolingOutR","TempCoolingOutCond","ConcReactorA","ConcReactorB","ConcReactorC","ConcReactorD","ConcReactorE","ConcReactorF","ConcPurgeA","ConcPurgeB","ConcPurgeC","ConcPurgeD","ConcPurgeE","ConcPurgeF","ConcPurgeG","ConcPurgeH","ConcUnderflowStripD","ConcUnderflowStripE","ConcUnderflowStripF","ConcUnderflowStripG","ConcUnderflowStripH","TempFeedA","TempFeedD","TempFeedE","TempFeedC","WaterCoolingInletReactor","FlowCoolingInletReactor","TempCoolingInletCondenser","FlowCoolingInletCondenser","CondFeedA_A","CondFeedA_B","CondFeedA_C","CondFeedA_D","CondFeedA_E","CondFeedA_F","CondFeedD_A","CondFeedD_B","CondFeedD_C","CondFeedD_D","CondFeedD_E","CondFeedD_F","CondFeedE_A","CondFeedE_B","CondFeedE_C","CondFeedE_D","CondFeedE_E","CondFeedE_F","CondFeedC_A","CondFeedC_B","CondFeedC_C","CondFeedC_D","CondFeedC_E","CondFeedC_F"]
    processData.columns=columnsProcessData
    #print(alarmData.columns)
    #print(processData.columns)


    #Create observations
    OBS = dtd.makeOBS(processData, processData.columns)

    #Create component matrix
    COMPS = dtd.makeCOMPS(processData, COMPONENTS)

    #Flatten dict
    anomalylist = []
    for k,v in INJECTED_FAULT.items():
        for item in v:
            anomalylist.append(item)


    #Shorten the data
    OBS = OBS.iloc[1:100000,:]
    COMPS = COMPS.iloc[1:100000,:]

    #Mark where the fault was injected (the true fault injection) for supervised learning
    arc = False
    arc_counter = 0
    dead_counter = 0
    for i in range(0,COMPS.shape[0]):
        sumOfAlarms = np.sum(alarmData.iloc[i,:])
        print("i: ",i,"sumOfAlarms: ", sumOfAlarms, "     Perc: ", (float(i) / COMPS.shape[0])*100)
        if sumOfAlarms!=0:
            for item in anomalylist[arc_counter]:
                COMPS[item].iloc[i] = 1
            if not arc:
                arc_counter+=1
                arc=True            
        else:
            if dead_counter < 300:
                dead_counter+=1
            else:
                arc=False
                dead_counter = 0



            

    #print("COMPS: ", COMPS)

    COMPS = dtd.removeUseless(COMPS)    

    #Merge to one dataset
    mergedData= pd.concat([COMPS, OBS], axis=1)
    #print("mergedData: ", mergedData.columns)

    mergedData.astype(float)

    granger.perform_adf_tests(mergedData, repetitions=10, pvalueTau=0.05)
    mergedData.loc[:, (mergedData != mergedData.iloc[0]).any()] 
    for column in mergedData.columns:
        sd = np.std(mergedData[column])
        if sd<0.01:
            mergedData.drop(column, axis=1, inplace=True)
    #AIC test
    granger.calculateAIC(mergedData, repetitions=7)

    result = granger.create_matrix(mergedData, variables = mergedData.columns)
    rw.grangerMatrixToRules(result, COMPONENTS, "output/GrangerTennesseeEastman.txt", tau=0.05, outlist=[])
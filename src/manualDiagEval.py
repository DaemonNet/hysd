#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: Script to manually execute diagnosis on real data
#################################################################################################################
import pandas as pd
import numpy as np
from sklearn.datasets import load_svmlight_file
import helper
import glob
import os

import pickle as pkl
import dataToDiagnosis as dtd

import reiter

class ManualExecution():

    def __init__(self, logfile, outpath, algorithms=['reiter','sat']):
        self.algos = algorithms
        self.logfile = logfile
        self.outpath = outpath

    #Generate residuals through machine learning. True means a fault exists. So far
    # we use a simple threshold-based approach to generate the residuals.
    def _machineLearning(self, measurementCols, fault_index_start, processData, fault_index_end=-1, startIndex=50):
        residuals = dict()
        for col in measurementCols:
            if col=="time":
                continue
            
            actualProcessData = processData[col]
            mean_normal = np.mean(actualProcessData[startIndex:fault_index_start])
            sd_normal = np.std(actualProcessData[startIndex:fault_index_start])
            #confidence = 3.5*sd_normal
            confidence = 0.05*sd_normal

            mean_fault = np.mean(actualProcessData[fault_index_start:fault_index_end])
            

            residuals[col] = False
            if mean_normal > 0.001:
                if (mean_fault < mean_normal-confidence) or (mean_fault > mean_normal+confidence):
                    #print(col, " true  because mean_fault: ", mean_fault, " mean normal: ", mean_normal, " confidence: ", confidence, "\n")
                    residuals[col] = True
                #else:
                    #print(col, " FALSE, because mean_fault: ", mean_fault, " mean normal: ", mean_normal, " confidence: ", confidence, "\n")

        return residuals

    #The functions to run the tanks
    def tanks(self, prefix, modelPath, dataPath, metaPath, startIndex):
        metadata = pd.read_csv(metaPath, header=None)
        fault_index = int(metadata.iloc[0,1]) #get the index when faults occur
        faultModes = [metadata.iloc[i,0] for i in range(3,metadata.shape[0])]

        print('fault_index: ',fault_index)
        print('faultModes: ',faultModes)

        filecounter = 0
        for file in glob.glob(dataPath):
            print(file)
            if os.path.basename(file) == "COMPS.csv":
                continue
        
            processData = pd.read_csv(file) # Dataframe

            measurementCols, dummy = helper.filterColumns(processData.columns) #get m_flow and V_flow and so on
            measurementCols.append("time")
            processData = processData[measurementCols]

            fault_file = metadata.iloc[filecounter+3,0] #Get the filename
            fault_labels = list(metadata.iloc[filecounter+3,1:]) #Behind the filenames the fault modes are written
            fault_labels = [x for x in fault_labels if str(x) != 'nan'] #Remove nan (from unused columns in COMPS file)
            
            residuals = self._machineLearning(measurementCols, fault_index, processData, startIndex=startIndex) #Just thresholds               
                
            if 'reiter' in self.algos:
                print("Using Reiter's HS-Tree")
                perc = reiter.runReiter_realObs(self.outpath+prefix+fault_file+"_reiterReal.diag", modelPath, residuals, fault_labels)
                self.logfile.write(fault_file + " " + str(perc) + "\n")

            filecounter += 1
        self.logfile.flush()


    def JohnDeere(self, prefix, modelPath, dataPath):

        fault_index = {'tool':[850,960],'axis2':[1027,1250]}
        faultModes = fault_index.keys()

        print('fault_index: ',fault_index)
        print('faultModes: ',faultModes)
        print(dataPath)
    
        processData = pd.read_csv(dataPath) # Dataframe

        new_startIndex = 0
        for label, indices in fault_index.items():
            fault_index_start = indices[0]
            fault_index_end = indices[1]
            fault_file = label
            residuals = self._machineLearning(processData.columns, fault_index_start, processData, fault_index_end = fault_index_end, startIndex=new_startIndex) #Just thresholds               
            new_startIndex = fault_index_end+10 #Allow a couple of cycles to adjust. We choose.....10, because I like the ten
            if 'reiter' in self.algos:
                print("Using Reiter's HS-Tree")
                perc = reiter.runReiter_realObs(self.outpath+prefix+fault_file+"_reiterReal.diag", modelPath, residuals, [label])
                self.logfile.write(fault_file + " " + str(perc) + "\n")


        self.logfile.flush()

    def TE(self, prefix, modelPath, dataPath, startIndex):
        STORE = False
        path = dataPath
        percentage = 0
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

        #Get all files that we need
        print("Loading data....")
        processData = pd.read_excel(path+"1/1_Original/SIMOUT.xlsx", engine='openpyxl') # Dataframe
        for f in range(1,100):
            print("Integrating file: ", f)
            processData = pd.read_excel(path+"/"+str(f)+"/1_Original/SIMOUT.xlsx", engine='openpyxl')

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

            #Create observations
            OBS = dtd.makeOBS(processData, processData.columns)

            #Create component matrix
            COMPS = dtd.makeCOMPS(processData, COMPONENTS)

            #Flatten dict
            anomalylist = []
            for k,v in INJECTED_FAULT.items():
                for item in v:
                    anomalylist.append(item)

            #Mark where the fault was injected (the true fault injection) for supervised learning
            arc = False
            arc_counter = 0

            fault_start_index = 0
            fault_starter = False

            for i in range(0,COMPS.shape[0]):
                sumOfAlarms = np.sum(alarmData.iloc[i,:])
                print("i: ",i,"sumOfAlarms: ", sumOfAlarms, "     Perc: ", (float(i) / COMPS.shape[0])*100)
                
                if sumOfAlarms!=0:
                    if fault_starter == False:
                        fault_starter = True
                        fault_start_index = i
                    for item in anomalylist[arc_counter]:
                        COMPS[item].iloc[i] = 1

                    if not arc:
                        arc_counter+=1
                        arc=True            


            COMPS = dtd.removeUseless(COMPS)

            residuals = self._machineLearning(OBS.columns, fault_start_index, OBS, startIndex=startIndex) #Just thresholds               

            if 'reiter' in self.algos:
                print("Using Reiter's HS-Tree")
                perc = reiter.runReiter_realObs(self.outpath+prefix+str(f)+"_reiterReal.diag", modelPath, residuals, anomalylist[f], append=False)
                self.logfile.write(str(f)+" "+str(perc) + "\n")
                percentage += perc
        self.logfile.write("Overall perc: "+ str(float(percentage) / 100) + "\n")

    def injectionMolding(self):
        pass

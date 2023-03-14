#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: Utitily file to prepare data for Granger Causality. The terminology is modelled after
# diagnosis terminology
#################################################################################################################

import pandas as pd
import numpy as np

#Create the observations OBS, by making a matrix with OBS column names and data. Also throw out stationary data.
def makeOBS(pData, cols):
    OBS_ARR = pData.columns
    OBS_DATA = pData
    OBS=pd.DataFrame(columns=OBS_ARR, data=OBS_DATA)

    #Throw out columns with no information. Meaning without any standard deviation
    for column in pData.columns:
        sd = np.std(OBS[column])
        if sd==0:
            OBS.drop(column, axis=1, inplace=True)
    return OBS

#Create the component matrix COMPS. It is a matrix with component names and initialised zero.
def makeCOMPS(pData, COMPONENTS):
    COMPS_ARR = COMPONENTS
    COMPS_DATA = np.zeros((pData.shape[0],len(COMPS_ARR)))
    COMPS = pd.DataFrame(columns=COMPS_ARR, data=COMPS_DATA)
    return COMPS

#Remove columns for COMPS matrix whose standard deviation is zero
def removeUseless(COMPS):
    toDelete = []
    for column in COMPS.columns:
        sd = np.std(COMPS[column])
        if sd==0:
            toDelete.append(column)
    COMPS.drop(toDelete, axis=1, inplace=True)
    return COMPS
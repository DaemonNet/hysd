#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: File for helper functions
#################################################################################################################

#We know that OpenModelica generates many internal variables. To filter those and thus to only
#obtain "useful" variables we filter them.
def filterColumns(colnames:list):
    measurementCols = []
    toDelete = []
    for c in colnames:
        if "volumeFlowRate" and  "V_flow" in c:
            measurementCols.append(c)
        if "tank" and "level" in c:
            measurementCols.append(c)
        if "m_flow" in c:
            measurementCols.append(c)
        if "Unnamed" in c:
            toDelete.append(c)
        if "$" in c:
            toDelete.append(c)
    
    return measurementCols, toDelete
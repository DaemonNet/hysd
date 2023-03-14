#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: File to automatically execute diagnosis with simulated observations. Both functions
# iterate over all *.txt files and call the associated diagnosers with rules
#################################################################################################################

import glob
import reiter

class diagExecution():

    def runDiagnosisReiter_simulatedObs(logfile):
        for file in glob.glob("output/*.txt"):
            print("using file: ", file)
            average_fault_num, average_diag_size, size = reiter.runReiter_simulatedObs(file+"_reiterSimulated.diag", file, runs=100)
            logfile.write(file + " average_fault_num: "+ str(average_fault_num) + " average_diag_size: "+ str(average_diag_size)+" num rules: "+ str(size)+"\n")

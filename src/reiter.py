#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: Main file to run Reiter's HS tree
#################################################################################################################

import minihit
import utils
import os

#Own stuff
from SymptomGenerator import *
from HypothesesGenerator import *

def runReiter_simulatedObs(outfile, rulesfile, runs=100):
    file = open(outfile, "w")
    average_fault_num = 0
    average_diag_size = 0
    num_rules = 0
    for i in range (0,runs):

        rules_parsed = utils.parse_file(rulesfile, is_sympy=False)
        num_rules=len(rules_parsed)
        s = SymptomGenerator()
        values_dict = s.getFakeSymptoms(rules_parsed, returnStringKeys=False)

        observations_given = set([str(k) for k, v in values_dict.items()])
        observations_faulty = set([str(k) for k, v in values_dict.items() if v == False])
        
        file.write('----------------------------------\n')
        file.write('Observations given:'+ str(observations_given)+"\n")
        file.write('Observations not ok:'+ str(observations_faulty)+"\n")
        file.write('----------------------------------'+"\n")
        average_fault_num += len(observations_faulty)
        # solve
        hyp = HypothesesGenerator()
        hypotheses = hyp.generateConflicts2(rules_parsed, values_dict)
        #Diagnosis
        hstree = minihit.HsDag(hypotheses)
        elapsed_seconds = hstree.solve(prune=True, sort=False)

        mhs = list(hstree.generate_minimal_hitting_sets())
        if (len(observations_faulty) > 0) & (len(mhs) > 0):
            average_diag_size += len(mhs[0])            
            file.write("MHS: "+  str(mhs)+"\n")
        else:
            file.write("MHS: None\n")
            
    file.write("sum faults: "+ str(average_fault_num)+"\n")
    file.write("Average num faults: "+str(float(average_fault_num) / float(runs))+"\n")
    file.write("Average diag size: "+ str(float(average_diag_size) / float(runs))+"\n")
    file.close()
    return float(average_fault_num) / float(runs), float(average_diag_size) / float(runs), num_rules


def runReiter_realObs(outfile, rulesfile, obs, labels, append=False):
    if append:
        file = open(outfile, "a")
    else:
        file = open(outfile, "w")

    rules_parsed = utils.parse_file(rulesfile, is_sympy=False)
    renamed_obs = {}
    for ob_old, val in obs.items():
        ob = utils.replacer(ob_old)
        renamed_obs[ob] = val

    values_dict = renamed_obs

    observations_given = set([str(k) for k, v in values_dict.items()])
    observations_faulty = set([str(k) for k, v in values_dict.items() if v == False])
    
    file.write('----------------------------------\n')
    file.write('Observations given:'+ str(observations_given)+"\n")
    file.write('Observations not ok:'+ str(observations_faulty)+"\n")
    file.write('----------------------------------'+"\n")
    # solve
    hyp = HypothesesGenerator()
    hypotheses = hyp.generateConflicts2(rules_parsed, values_dict)
    #Diagnosis
    hstree = minihit.HsDag(hypotheses)
    elapsed_seconds = hstree.solve(prune=True, sort=False)

    mhs = list(hstree.generate_minimal_hitting_sets())
    if (len(observations_faulty) > 0) & (len(mhs) > 0):        
        file.write("MHS: "+  str(mhs)+"\n")
    else:
        file.write("MHS: None\n")

    counter = 0
    for label in labels:
        label = label.strip()
        file.write("Looking for label: "+label +"\n")
        if label in str(mhs):
            counter += 1
            file.write("label: "+label +" found\n")
    file.write("Found "+str(counter) + " of " + str(len(labels)) + " labels\n")
    file.close()        

    return counter / len(labels)
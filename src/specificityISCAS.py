#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: File to evaluate the specificity for ISCAS files
#################################################################################################################

import utils
import glob
import copy

def evaluateRulesISCAS(path, logfile):
    for file in glob.glob(path):
        logfile.write("File: "+ str(file)+ "\n")
        f = open(file, mode="r", encoding="utf8", errors='ignore')
        alllines = f.readlines()
        outfile = open("output/tempfile.log", "w")
        for line in alllines:
            print(line)
            line = line.replace("\x00", "")
           
            line = line.replace("!","")
            line = line.replace("(","")
            line = line.replace(")","")
            line = line.replace("&&","AND")

            line = line.replace("||","AND")
            line = line.replace("\n","")
            index = line.find(":")
            if line == "":
                    continue
            line = line[index+1:] #remove first part
            index = line.find("==")
            pre = line[:index].strip()
            post = line[index+3:]
            line = post + " IMPLIES " + pre
            outfile.write(line + "\n")
        f.close()
        outfile.close()
        rules_parsed = utils.parse_file("output/tempfile.log", is_sympy=False)
        set_R = []
        for rule in rules_parsed:
            set_R.append(list(rule.get_predicates_symbols()))
        symbols = set(__flatten(set_R))
        #logfile.write("    Available symbols: "+ str(symbols)+ "\n")
        logfile.write("    Length symbols: "+ str(len(symbols))+ "\n")
        

        #Trivial Estimation
        score = __trivialEstimation(set_R)
        logfile.write("    Trivial score: "+ str(score)+ "\n")

        #CheckDiag
        set_R.sort(key=len)
        ok = []
        for card in range(0,len(set_R[-1])):
            intermediateSet = []
            for s in set_R:
                if len(s) == 1:
                    ok.append(s[0])
                if len(s) == card:
                    intermediateSet.append(s)
            for cardSet in intermediateSet:
                ok.extend(__iterator(cardSet, intermediateSet[1:]))

        ok = set(ok)
        print("okay: ", ok)
        nok = []
        for symbol in symbols:
            if symbol in ok:
                continue
            nok.append(symbol)
                    
        nok = set(nok)

        logfile.write("    nok:" + str(nok) + "\n")
        logfile.write("    noklen:" + str(len(nok)) + "\n")
        if len(nok) > 0:
            logfile.write("    quotient:" + str(float(len(nok))/len(symbols))+ "\n")

def __trivialEstimation(setR):
    sum = 0.0
    for rule in setR:
        sum += len(rule)
    return sum/len(setR)


def __iterator(comps, allCardSets): 
    explained = []   
    for c in comps:
        withoutComps = copy.deepcopy(comps)
        withoutComps.remove(c)
        for s in allCardSets:
            if c in s:
                for wc in withoutComps:
                    if wc in s:
                        continue
                explained.append(c)
    return explained


def __flatten(seq):
    l = []
    for elt in seq:
        t = type(elt)
        if t is tuple or t is list:
            for elt2 in __flatten(elt):
                l.append(elt2)
        else:
            l.append(elt)
    return l
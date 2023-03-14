#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: Generates fake symptoms. True means a fault exists.
#################################################################################################################
import numpy as np

class SymptomGenerator():

    def getFakeSymptoms(self, rules, probability=0.5, returnStringKeys=False):
        allSymptoms = {}

        if hasattr(rules, 'values'):  # dict-like
            for v in rules.values():
                allSymptoms[v.implicant] = False
        else:  # list-like
             for rule in rules:  # dict-like
                implicant, = rule.get_implicant_symbols()
                allSymptoms[implicant] = False
        
        # set symtoms to True with given probability
        samples = np.random.binomial(1, probability, size=len(allSymptoms))
        indices, = np.where(samples)

        keys = tuple(allSymptoms.keys())
        for i in indices:
            allSymptoms[keys[i]] = True

        if returnStringKeys:
            return self.convertToStringKeys(allSymptoms)
        return allSymptoms

    def convertToStringKeys(self, symptom_dict):
        newdict = dict()
        for k,v in symptom_dict.items():
            newdict[str(k)] = v
        return newdict

    def getNoSymptoms(self, rules):
        allSymptoms = dict()
        for v in rules.values():
            allSymptoms[v.implicant] = False

        return allSymptoms

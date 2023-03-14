#################################################################################################################
# Author: Alexander Diedrich
# Date: 14.03.2023
# Description: Functions to perform correlations
#################################################################################################################

from scipy import stats

#We use Spearman rank correlation for time-series data. This functions iterates over all given thresholds
def runSpearman(data, taulist):
    results = dict()
    for t in taulist:
        results[t] = performSpearmanCorrelation(data,t)
    return results

#Do the correlation
def performSpearmanCorrelation(data, threshold):

    #Use correlation as-is
    spearman = stats.spearmanr(data)
    spearman_cor = spearman[0]
    print(spearman_cor)
    print(type(spearman_cor))

    #Associate the correlations to names within a dict
    name_lookup = dict(zip(range(0,spearman_cor.shape[0]), data.columns))

    edges = []
    weights = []
    directions = []

    thresholdP = threshold
    thresholdN = -threshold

    #Create a sorted list with edges (what is correlated to what else), weights (how high is the correlation), and directions (positive or negative correlation)
    for row in range(0,spearman_cor.shape[0]):
        for column in range(0,spearman_cor.shape[1]):
            if spearman_cor[row,column] > 0.99: 
                break #Remove self-correlation
            if spearman_cor[row,column] > thresholdP:
                edges.append((str(name_lookup[row]), str(name_lookup[column])))
                weights.append(spearman_cor[row,column])
                directions.append("+")
            elif spearman_cor[row,column] < thresholdN:
                edges.append((str(name_lookup[row]), str(name_lookup[column])))
                weights.append(spearman_cor[row,column])
                directions.append("-")

    #print("edges: ", edges)
    #print("weights: ", weights)
    #print("direction: ", directions)

    return edges, weights, directions



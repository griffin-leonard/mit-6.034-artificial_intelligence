# MIT 6.034 Lab 9: Boosting (Adaboost)
# Written by 6.034 staff

from math import log as ln
from utils import *


#### Part 1: Helper functions ##################################################

def initialize_weights(training_points):
    """Assigns every training point a weight equal to 1/N, where N is the number
    of training points.  Returns a dictionary mapping points to weights."""
    w = make_fraction(1,len(training_points))    
    weights = {point : w for point in training_points}
    return weights

def calculate_error_rates(point_to_weight, classifier_to_misclassified):
    """Given a dictionary mapping training points to their weights, and another
    dictionary mapping classifiers to the training points they misclassify,
    returns a dictionary mapping classifiers to their error rates."""
    error_rates = {}
    for classifier,misclassified in classifier_to_misclassified.items():
        error_rates[classifier] = sum([point_to_weight[p] for p in misclassified])
    return error_rates

def pick_best_classifier(classifier_to_error_rate, use_smallest_error=True):
    """Given a dictionary mapping classifiers to their error rates, returns the
    best* classifier, or raises NoGoodClassifiersError if best* classifier has
    error rate 1/2.  best* means 'smallest error rate' if use_smallest_error
    is True, otherwise 'error rate furthest from 1/2'."""
    if use_smallest_error:
        best = min(classifier_to_error_rate.keys(), key=lambda x: classifier_to_error_rate[x])
    else: 
        best = max(classifier_to_error_rate.keys(), key=lambda x: abs(classifier_to_error_rate[x] - make_fraction(1,2)))
    if classifier_to_error_rate[best] == make_fraction(1,2): raise NoGoodClassifiersError
    return best

def calculate_voting_power(error_rate):
    """Given a classifier's error rate (a number), returns the voting power
    (aka alpha, or coefficient) for that classifier."""
    if error_rate == 0: return INF
    if error_rate == 1: return -INF
    return 1/2*ln((1-error_rate)/error_rate)

def get_overall_misclassifications(H, training_points, classifier_to_misclassified):
    """Given an overall classifier H, a list of all training points, and a
    dictionary mapping classifiers to the training points they misclassify,
    returns a set containing the training points that H misclassifies.
    H is represented as a list of (classifier, voting_power) tuples."""
    misclassified = set()
    for point in training_points:
        classification = 0
        for classifier,power in H:
            if point in classifier_to_misclassified[classifier]: c = -1
            else: c = 1
            classification += power * c
        if classification <= 0: misclassified.add(point)
    return misclassified
        
def is_good_enough(H, training_points, classifier_to_misclassified, mistake_tolerance=0):
    """Given an overall classifier H, a list of all training points, a
    dictionary mapping classifiers to the training points they misclassify, and
    a mistake tolerance (the maximum number of allowed misclassifications),
    returns False if H misclassifies more points than the tolerance allows,
    otherwise True.  H is represented as a list of (classifier, voting_power)
    tuples."""
    if len(get_overall_misclassifications(H, training_points, classifier_to_misclassified)) > mistake_tolerance: return False
    return True

def update_weights(point_to_weight, misclassified_points, error_rate):
    """Given a dictionary mapping training points to their old weights, a list
    of training points misclassified by the current weak classifier, and the
    error rate of the current weak classifier, returns a dictionary mapping
    training points to their new weights.  This function is allowed (but not
    required) to modify the input dictionary point_to_weight."""
    for point,weight in point_to_weight.items():
        if point in misclassified_points:
            point_to_weight[point] *= make_fraction(1,2)*make_fraction(1,error_rate)
        else: point_to_weight[point] *= make_fraction(1,2)*make_fraction(1,1-error_rate)
    return point_to_weight

#### Part 2: Adaboost ##########################################################

def adaboost(training_points, classifier_to_misclassified,
             use_smallest_error=True, mistake_tolerance=0, max_rounds=INF):
    """Performs the Adaboost algorithm for up to max_rounds rounds.
    Returns the resulting overall classifier H, represented as a list of
    (classifier, voting_power) tuples."""
    i = 1
    H = []
    point_to_weight = initialize_weights(training_points) #Initialize all training points' weights.
    while i <= max_rounds:
        #Compute the error rate of each weak classifier.
        classifier_to_error_rate = calculate_error_rates(point_to_weight, classifier_to_misclassified)
        
        #Pick the "best" weak classifier h, by some definition of "best."
        try: h = pick_best_classifier(classifier_to_error_rate, use_smallest_error)
        except: return H #no good classifier remains
        
        #Use the error rate of h to compute the voting power for h and 
        #append h, along with its voting power, to the ensemble classifier H.
        H.append( (h, calculate_voting_power(classifier_to_error_rate[h])) )
        
        #Update weights in preparation for the next round.
        point_to_weight = update_weights(point_to_weight, classifier_to_misclassified[h], classifier_to_error_rate[h])
        
        #check if H is "good enough"
        if is_good_enough(H, training_points, classifier_to_misclassified, mistake_tolerance): return H
        i += 1
    return H #reached max number of iterations


#### SURVEY ####################################################################

NAME = 'Griffin Leonard'
COLLABORATORS = 'None'
HOW_MANY_HOURS_THIS_LAB_TOOK = 1.5
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None
SUGGESTIONS = None

# MIT 6.034 Lab 5: Bayesian Inference
# Written by 6.034 staff

from nets import *


#### Part 1: Warm-up; Ancestors, Descendents, and Non-descendents ##############

def get_ancestors(net, var):
    "Return a set containing the ancestors of var"
    ancestors = set()
    for parent in net.get_parents(var):
        ancestors.add(parent)
        ancestors |= get_ancestors(net, parent)
    return ancestors

def get_descendants(net, var):
    "Returns a set containing the descendants of var"
    descendants = set()
    for child in net.get_children(var):
        descendants.add(child)
        descendants |= get_descendants(net, child)
    return descendants

def get_nondescendants(net, var):
    "Returns a set containing the non-descendants of var"
    descendants = get_descendants(net, var)
    nonDesc = set(net.get_variables()).difference(descendants)
    nonDesc.remove(var)
    return nonDesc


#### Part 2: Computing Probability #############################################

def simplify_givens(net, var, givens):
    """
    If givens include every parent of var and no descendants, returns a
    simplified list of givens, keeping only parents.  Does not modify original
    givens.  Otherwise, if not all parents are given, or if a descendant is
    given, returns original givens.
    """
    descendants = get_descendants(net,var)
    parents = net.get_parents(var)
    givenVars = givens.keys()
    for desc in descendants:
        if desc in givenVars: return givens
    if not parents.issubset(givenVars): return givens
    givensC = givens.copy()
    for given in givens:
        if given not in parents: del givensC[given]
    return givensC
    
def probability_lookup(net, hypothesis, givens=None):
    "Looks up a probability in the Bayes net, or raises LookupError"
    if len(hypothesis) > 1: raise LookupError
    if givens != None: 
        key = next(iter(hypothesis.keys()))
        givens = simplify_givens(net,key,givens)
    try: return net.get_probability(hypothesis,givens)
    except: raise LookupError

def probability_joint(net, hypothesis):
    "Uses the chain rule to compute a joint probability"
    prob = None
    for var in hypothesis.keys():
        hypo = {var:hypothesis[var]}
        givens = {key:hypothesis[key] for key in net.get_parents(var)}
        if prob == None: prob = probability_lookup(net,hypo,givens)
        else: prob *= probability_lookup(net,hypo,givens)
    return prob
    
def probability_marginal(net, hypothesis):
    "Computes a marginal probability as a sum of joint probabilities"
    allVars = net.get_variables()
    sumover = net.combinations(allVars,hypothesis)
    probs = []
    for joint in sumover:
        probs.append(probability_joint(net,joint))
    return sum(probs)

def probability_conditional(net, hypothesis, givens=None):
    "Computes a conditional probability as a ratio of marginal probabilities"
    if givens == None: return probability_marginal(net,hypothesis)
    for var,val in hypothesis.items():
        if var in givens.keys():
            if givens[var] == val: return 1
            else: return 0
    return probability_marginal(net,dict(hypothesis,**givens))/probability_marginal(net,givens)
    
def probability(net, hypothesis, givens=None):
    "Calls previous functions to compute any probability"
    return probability_conditional(net, hypothesis, givens)


#### Part 3: Counting Parameters ###############################################

def number_of_parameters(net):
    """
    Computes the minimum number of parameters required for the Bayes net.
    """
    totParams = 0
    for var in net.get_variables():
        params = len(net.get_domain(var))-1
        for parent in net.get_parents(var):
            params *= len(net.get_domain(parent))
        totParams += params
    return totParams


#### Part 4: Independence ######################################################

def is_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    otherwise False. Uses numerical independence.
    """
    if givens == None:
        return approx_equal(probability(net,{var1:net.get_domain(var1)[0]}), \
                        probability(net,{var1:net.get_domain(var1)[0]},{var2:net.get_domain(var2)[0]}))
    return approx_equal(probability(net,{var1:net.get_domain(var1)[0]},givens), \
                    probability(net,{var1:net.get_domain(var1)[0]}, \
                                     dict({var2:net.get_domain(var2)[0]},**givens)))
    
def is_structurally_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    based on the structure of the Bayes net, otherwise False.
    Uses structural independence only (not numerical independence).
    """        
    #draw ancestral graph
    vars0 = [var1,var2]
    if givens != None: vars0 += list(givens.keys())
    vars1 = set(vars0.copy())
    for var in vars0: vars1.update(get_ancestors(net,var))
    subnet0 = net.subnet(list(vars1))
    subnet1 = net.subnet(list(vars1))
    
    #link parents
    for var in subnet0.get_variables():
        parents = subnet0.get_parents(var)
        for parent1 in parents:
            for parent2 in parents:
                if parent1 != parent2: 
                    subnet1 = subnet1.link(parent1,parent2)
    #disorient             
    subnet1 = subnet1.make_bidirectional()
    
    #delete givens
    if givens != None:
        for given in givens.keys():
            subnet1 = subnet1.remove_variable(given)
            
    #find path
    if subnet1.find_path(var1,var2) == None: return True
    return False


#### SURVEY ####################################################################

NAME = 'Griffin Leonard'
COLLABORATORS = 'None'
HOW_MANY_HOURS_THIS_LAB_TOOK = '4'
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None
SUGGESTIONS = None

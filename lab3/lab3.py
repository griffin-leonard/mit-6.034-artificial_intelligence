# MIT 6.034 Lab 3: Constraint Satisfaction Problems
# Written by 6.034 staff

from constraint_api import *
#from test_problems import get_pokemon_problem
from test_problems import *


#### Part 1: Warmup ############################################################

def has_empty_domains(csp) :
    """Returns True if the problem has one or more empty domains, otherwise False"""
    for domain in csp.domains.values():
        if len(domain) == 0: return True
    return False

def check_all_constraints(csp) :
    """Return False if the problem's assigned values violate some constraint,
    otherwise True"""
    for constraint in csp.constraints:
        if constraint.var1 in csp.assignments and constraint.var2 in csp.assignments and\
        not constraint.check(csp.assignments[constraint.var1],csp.assignments[constraint.var2]):
            return False
    return True


#### Part 2: Depth-First Constraint Solver #####################################

def solve_constraint_dfs(problem) :
    """
    Solves the problem using depth-first search.  Returns a tuple containing:
    1. the solution (a dictionary mapping variables to assigned values)
    2. the number of extensions made (the number of problems popped off the agenda).
    If no solution was found, return None as the first element of the tuple.
    """
    queue = [problem]
    extensions = 0
    while queue:
        csp = queue.pop(0)
        extensions += 1
        
        #proceed only if problem is solvable
        if not has_empty_domains(csp) and check_all_constraints(csp):
            
            #check if solution has been found
            if len(csp.unassigned_vars) == 0:
                return (csp.assignments,extensions)
            var = csp.pop_next_unassigned_var()
            domain = csp.get_domain(var)
            new_probs = []
            for val in domain:
                new_csp = csp.copy()
                new_csp.set_assignment(var, val)
                new_probs.append(new_csp)
            queue = new_probs + queue
    return (None,extensions)

# QUESTION 1: How many extensions does it take to solve the Pokemon problem
#    with DFS?

# Hint: Use get_pokemon_problem() to get a new copy of the Pokemon problem
#    each time you want to solve it with a different search method.

#print(solve_constraint_dfs(get_pokemon_problem()))  
ANSWER_1 = 20

#### Part 3: Forward Checking ##################################################

def eliminate_from_neighbors(csp, var) :
    """
    Eliminates incompatible values from var's neighbors' domains, modifying
    the original csp.  Returns an alphabetically sorted list of the neighboring
    variables whose domains were reduced, with each variable appearing at most
    once.  If no domains were reduced, returns empty list.
    If a domain is reduced to size 0, quits immediately and returns None.
    """    
    reduced_vars = []
    for neighbor in csp.get_neighbors(var):
        violated = []
        #try to reduce neighbor's domain
        for val in csp.get_domain(neighbor):
            if not check_constraints(csp,var,neighbor,val):
                violated.append(val)
        
        if violated:
            reduced_vars.append(neighbor)
        for val in violated:
            csp.eliminate(neighbor, val)
        if not csp.get_domain(neighbor):
            return None #terminate because a domain is empty
    return sorted(reduced_vars)

def check_constraints(csp,var,neighbor,val):
    ''' 
    Checks to see if a value in neighbor's domain (val) violates a constraint
    for all values in var's domain. Helper function for eliminate_from_neighbors.
    Returns:
        True if val satifies the constraints for at least one value
        False if val should be deleted from neighbor's domain
    '''
    constraints = csp.constraints_between(neighbor, var)
    for val2 in csp.get_domain(var):
        violated_constraint = False
        for constraint in constraints:
            if not constraint.check(val,val2):
                violated_constraint = True
        if not violated_constraint:
            return True
    return False
 
# Because names give us power over things (you're free to use this alias)
forward_check = eliminate_from_neighbors

def solve_constraint_forward_checking(problem) :
    """
    Solves the problem using depth-first search with forward checking.
    Same return type as solve_constraint_dfs.
    """
    queue = [problem]
    extensions = 0
    while queue:
        csp = queue.pop(0)
        extensions += 1
        
        #proceed only if problem is solvable
        if not has_empty_domains(csp) and check_all_constraints(csp):
            
            #check if solution has been found
            if len(csp.unassigned_vars) == 0:
                return (csp.assignments,extensions)
            var = csp.pop_next_unassigned_var()
            domain = csp.get_domain(var)
            new_probs = []
            for val in domain:
                new_csp = csp.copy()
                new_csp.set_assignment(var, val)
                eliminate_from_neighbors(new_csp,var)
                new_probs.append(new_csp)
            queue = new_probs + queue
    return (None,extensions)

# QUESTION 2: How many extensions does it take to solve the Pokemon problem
#    with DFS and forward checking?

#print(solve_constraint_forward_checking(get_pokemon_problem()))   
ANSWER_2 = 9


#### Part 4: Domain Reduction ##################################################

def domain_reduction(csp, queue=None) :
    """
    Uses constraints to reduce domains, propagating the domain reduction
    to all neighbors whose domains are reduced during the process.
    If queue is None, initializes propagation queue by adding all variables in
    their default order. 
    Returns a list of all variables that were dequeued, in the order they
    were removed from the queue.  Variables may appear in the list multiple times.
    If a domain is reduced to size 0, quits immediately and returns None.
    This function modifies the original csp.
    """
    if queue == None:
        queue = csp.get_all_variables()
    dequeued = []
    while queue:
        #dequeue and reduce domains
        var = queue.pop(0)
        dequeued.append(var)
        reduced_vars = eliminate_from_neighbors(csp,var)
        if reduced_vars == None: return None #terminate because a domain is empty
        
        #add variables whose domains were reduced back to the queue if necessary 
        for reduced in reduced_vars:
            if reduced not in queue:
                queue.append(reduced)
    return dequeued

#TESTS
#prob = triangle_problem_modified.copy()
#print(domain_reduction(prob,['B','A']))
#prob = CSP_singleton_differentiate.copy()
#print(domain_reduction(prob,['A']))
#prob = CSP_do_not_sort_queue.copy()
#print(domain_reduction(prob))


# QUESTION 3: How many extensions does it take to solve the Pokemon problem
#    with DFS (no forward checking) if you do domain reduction before solving it?
    
#prob = get_pokemon_problem()
#domain_reduction(prob)
#print(solve_constraint_dfs(prob))
ANSWER_3 = 6


def solve_constraint_propagate_reduced_domains(problem) :
    """
    Solves the problem using depth-first search with forward checking and
    propagation through all reduced domains.  Same return type as
    solve_constraint_dfs.
    """
    queue = [problem]
    extensions = 0
    while queue:
        csp = queue.pop(0)
        extensions += 1
        
        #proceed only if problem is solvable
        if not has_empty_domains(csp) and check_all_constraints(csp):
            
            #check if solution has been found
            if len(csp.unassigned_vars) == 0:
                return (csp.assignments,extensions)
            var = csp.pop_next_unassigned_var()
            domain = csp.get_domain(var)
            new_probs = []
            for val in domain:
                new_csp = csp.copy()
                new_csp.set_assignment(var, val)
                domain_reduction(new_csp,[var])
                new_probs.append(new_csp)
            queue = new_probs + queue
    return (None,extensions)

#TESTS
#print(solve_constraint_propagate_reduced_domains(CSP_no_prop.copy()))
#print(CSP_no_prop.copy())

# QUESTION 4: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through reduced domains?

#print(solve_constraint_propagate_reduced_domains(get_pokemon_problem()))   
ANSWER_4 = 7


#### Part 5A: Generic Domain Reduction #########################################

def propagate(enqueue_condition_fn, csp, queue=None) :
    """
    Uses constraints to reduce domains, modifying the original csp.
    Uses enqueue_condition_fn to determine whether to enqueue a variable whose
    domain has been reduced. Same return type as domain_reduction.
    """
    if queue == None:
        queue = csp.get_all_variables()

    dequeued = []
    while queue:
        #dequeue and reduce domains
        var = queue.pop(0)
        dequeued.append(var)
        reduced_vars = eliminate_from_neighbors(csp,var)
        if reduced_vars == None: return None #terminate because a domain is empty
        
        #add variables whose domains were reduced back to the queue if necessary 
        for reduced in reduced_vars:
            if enqueue_condition_fn(csp,reduced): #and reduced not in queue
                queue.append(reduced)
    return dequeued

#TESTS
#print(propagate(lambda p,v: len(p.get_domain(v))==1, CSP_singleton_differentiate.copy(), ['A']))
#print(propagate(lambda p,v: len(p.get_domain(v))==1, CSP_one_var_assigned_unconstrained.copy()))
#print(CSP_one_var_assigned_unconstrained.copy())


def condition_domain_reduction(csp, var) :
    """Returns True if var should be enqueued under the all-reduced-domains
    condition, otherwise False"""
    return True
    
def condition_singleton(csp, var) :
    """Returns True if var should be enqueued under the singleton-domains
    condition, otherwise False"""
    if len(csp.get_domain(var)) == 1:
        return True
    return False

def condition_forward_checking(csp, var) :
    """Returns True if var should be enqueued under the forward-checking
    condition, otherwise False"""
    return False


#### Part 5B: Generic Constraint Solver ########################################

def solve_constraint_generic(problem, enqueue_condition=None) :
    """
    Solves the problem, calling propagate with the specified enqueue
    condition (a function). If enqueue_condition is None, uses DFS only.
    Same return type as solve_constraint_dfs.
    """
    if enqueue_condition == None:
        return solve_constraint_dfs(problem)
        
    queue = [problem]
    extensions = 0
    while queue:
        csp = queue.pop(0)
        extensions += 1
        
        #proceed only if problem is solvable
        if not has_empty_domains(csp) and check_all_constraints(csp):
            
            #check if solution has been found
            if len(csp.unassigned_vars) == 0:
                return (csp.assignments,extensions)
            
            var = csp.pop_next_unassigned_var()
            domain = csp.get_domain(var)
            new_probs = []
            for val in domain:
                new_csp = csp.copy()
                new_csp = new_csp.set_assignment(var, val)
                propagate(enqueue_condition, new_csp, [var])
                new_probs.append(new_csp)
            queue = new_probs + queue
    return (None,extensions)

#TESTS
print(solve_constraint_generic(triangle_problem.copy(),lambda p,v: False))
#print(triangle_problem.copy())


# QUESTION 5: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through singleton domains? (Don't
#    use domain reduction before solving it.)

#print(solve_constraint_generic(get_pokemon_problem(),condition_singleton))  
ANSWER_5 = 8


#### Part 6: Defining Custom Constraints #######################################

def constraint_adjacent(m, n) :
    """Returns True if m and n are adjacent, otherwise False.
    Assume m and n are ints."""
    if abs(m-n) == 1:
        return True
    return False

def constraint_not_adjacent(m, n) :
    """Returns True if m and n are NOT adjacent, otherwise False.
    Assume m and n are ints."""
    if not abs(m-n) == 1:
        return True
    return False

def all_different(variables) :
    """Returns a list of constraints, with one difference constraint between
    each pair of variables."""
    n = len(variables)
    constraints = []
    for i,var in enumerate(variables):
        for var2 in variables[i+1:n]:
            constraints.append(Constraint(var,var2,constraint_different))
    return constraints


#### SURVEY ####################################################################

NAME = 'Griffin Leonard'
COLLABORATORS = 'None'
HOW_MANY_HOURS_THIS_LAB_TOOK = '16'
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None
SUGGESTIONS = None

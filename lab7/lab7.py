# MIT 6.034 Lab 7: Neural Nets
# Written by 6.034 Staff

from nn_problems import *
from math import e
INF = float('inf')


#### Part 1: Wiring a Neural Net ###############################################

nn_half = [1]

nn_angle = [2,1]

nn_cross = [2,2,1]

nn_stripe = [3,1]

nn_hexagon = [6,1]

nn_grid = [4,2,1]


#### Part 2: Coding Warmup #####################################################

# Threshold functions
def stairstep(x, threshold=0):
    "Computes stairstep(x) using the given threshold (T)"
    if x >= threshold: return 1
    return 0

def sigmoid(x, steepness=1, midpoint=0):
    "Computes sigmoid(x) using the given steepness (S) and midpoint (M)"
    return 1/(1+e**(-steepness*(x-midpoint)))

def ReLU(x):
    "Computes the threshold of an input using a rectified linear unit."
    return max(0,x)

# Accuracy function
def accuracy(desired_output, actual_output):
    "Computes accuracy. If output is binary, accuracy ranges from -0.5 to 0."
    return -.5*(desired_output-actual_output)**2


#### Part 3: Forward Propagation ###############################################

def node_value(node, input_values, neuron_outputs):  # PROVIDED BY THE STAFF
    """
    Given 
     * a node (as an input or as a neuron),
     * a dictionary mapping input names to their values, and
     * a dictionary mapping neuron names to their outputs
    returns the output value of the node.
    This function does NOT do any computation; it simply looks up
    values in the provided dictionaries.
    """
    if isinstance(node, str):
        # A string node (either an input or a neuron)
        if node in input_values:
            return input_values[node]
        if node in neuron_outputs:
            return neuron_outputs[node]
        raise KeyError("Node '{}' not found in either the input values or neuron outputs dictionary.".format(node))
    
    if isinstance(node, (int, float)):
        # A constant input, such as -1
        return node
    
    raise TypeError("Node argument is {}; should be either a string or a number.".format(node))

def forward_prop(net, input_values, threshold_fn=stairstep):
    """Given a neural net and dictionary of input values, performs forward
    propagation with the given threshold function to compute binary output.
    This function should not modify the input net.  Returns a tuple containing:
    (1) the final output of the neural net
    (2) a dictionary mapping neurons to their immediate outputs"""
    outputs = {}
    for neuron in net.topological_sort():
        summed_inputs = 0
        for wire in net.get_wires(None,neuron):
            summed_inputs += node_value(wire.startNode, input_values, outputs) * wire.get_weight()
        outputs[neuron] = threshold_fn(summed_inputs)
        if net.is_output_neuron(neuron):
            output = outputs[neuron]
    return (output,outputs)


#### Part 4: Backward Propagation ##############################################

def gradient_ascent_step(func, inputs, step_size):
    """Given an unknown function of three variables and a list of three values
    representing the current inputs into the function, increments each variable
    by +/- step_size or 0, with the goal of maximizing the function output.
    After trying all possible variable assignments, returns a tuple containing:
    (1) the maximum function output found, and
    (2) the list of inputs that yielded the highest function output."""
    #get all possible input combinations
    input_combinations = set()
    perturbations = [0,step_size,-step_size]
    for delta0 in perturbations:
        for delta1 in perturbations:
            for delta2 in perturbations:
                input_combinations.add( (inputs[0]+delta0, inputs[1]+delta1, inputs[2]+delta2) )
    
    #determine best input
    best = max(input_combinations, key=lambda x: func(*x))
    return (func(*best),best)
    
def get_back_prop_dependencies(net, wire):
    """Given a wire in a neural network, returns a set of inputs, neurons, and
    Wires whose outputs/values are required to update this wire's weight."""
    dependencies = set([wire,wire.startNode,wire.endNode])
    for wire0 in net.get_wires(wire.endNode,None):
        dependencies.add(wire0)
        dependencies = dependencies.union(get_back_prop_dependencies(net,wire0))
    return dependencies

def calculate_deltas(net, desired_output, neuron_outputs):
    """Given a neural net and a dictionary of neuron outputs from forward-
    propagation, computes the update coefficient (delta_B) for each
    neuron in the net. Uses the sigmoid function to compute neuron output.
    Returns a dictionary mapping neuron names to update coefficient (the
    delta_B values). """
    deltas = {}            
    neurons = net.topological_sort()
    neurons.reverse()
    for neuron in neurons:
        coef = neuron_outputs[neuron]*(1-neuron_outputs[neuron])
        if net.is_output_neuron(neuron):
            deltas[neuron] = coef*(desired_output-neuron_outputs[neuron])
        else:
            summation = 0
            for child in net.get_outgoing_neighbors(neuron):
                summation += deltas[child] * net.get_wires(neuron,child)[0].get_weight()
            deltas[neuron] = coef*summation
    return deltas

def update_weights(net, input_values, desired_output, neuron_outputs, r=1):
    """Performs a single step of back-propagation.  Computes delta_B values and
    weight updates for entire neural net, then updates all weights.  Uses the
    sigmoid function to compute neuron output.  Returns the modified neural net,
    with the updated weights."""
    deltas = calculate_deltas(net, desired_output, neuron_outputs)
    for wire in net.get_wires():
        wire.set_weight(wire.get_weight() + r * node_value(wire.startNode,input_values,neuron_outputs) * deltas[wire.endNode])
    return net

def back_prop(net, input_values, desired_output, r=1, minimum_accuracy=-0.001):
    """Updates weights until accuracy surpasses minimum_accuracy.  Uses the
    sigmoid function to compute neuron output.  Returns a tuple containing:
    (1) the modified neural net, with trained weights
    (2) the number of iterations (that is, the number of weight updates)"""
    output, neuron_outputs = forward_prop(net, input_values, sigmoid)
    iterations = 0
    while accuracy(desired_output, output) < minimum_accuracy:
        net = update_weights(net, input_values, desired_output, neuron_outputs, r)
        iterations += 1
        output, neuron_outputs = forward_prop(net, input_values, sigmoid)
    return (net, iterations)
        

#### Part 5: Training a Neural Net #############################################

ANSWER_1 = 11
ANSWER_2 = 21
ANSWER_3 = 5
ANSWER_4 = 200
ANSWER_5 = 47

ANSWER_6 = 1
ANSWER_7 = 'checkerboard'
ANSWER_8 = ['small','medium','large']
ANSWER_9 = 'B'

ANSWER_10 = 'D'
ANSWER_11 = ['A','C']
ANSWER_12 = ['A','E']


#### SURVEY ####################################################################

NAME = 'Griffin Leonard'
COLLABORATORS = 'None'
HOW_MANY_HOURS_THIS_LAB_TOOK = 3
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None
SUGGESTIONS = None

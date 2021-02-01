# MIT 6.034 Lab 2: Games
# Written by 6.034 staff

from game_api import *
from boards import *
from toytree import GAME1

INF = float('inf')

# Please see wiki lab page for full description of functions and API.

#### Part 1: Utility Functions #################################################

def is_game_over_connectfour(board):
    """Returns True if game is over, otherwise False."""
    for chain in board.get_all_chains(): #check for win
        if len(chain) >= 4: return True
    for col in range(board.num_cols): #check for tie
        if not board.is_column_full(col): return False
    return True

def next_boards_connectfour(board):
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""
    if is_game_over_connectfour(board): return []
    boards = []
    for col in range(board.num_cols):
        if not board.is_column_full(col):
            boards.append(board.add_piece(col))
    return boards
    
def endgame_score_connectfour(board, is_current_player_maximizer):
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""
    for chain in board.get_all_chains(current_player=False):
        if len(chain) >= 4:
            if is_current_player_maximizer: return -1000
            return 1000
    return 0

def endgame_score_connectfour_faster(board, is_current_player_maximizer):
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    empty =  board.num_rows*board.num_cols - board.count_pieces()
    for chain in board.get_all_chains(current_player=False):
        if len(chain) >= 4:
            if is_current_player_maximizer: return -1000 -empty
            return 1000 +empty
    return 0

def heuristic_connectfour(board, is_current_player_maximizer):
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""
    score = 0
    for chain in board.get_all_chains(current_player=True):
        chain_len = len(chain)
        if chain_len == 1: score += 1
        elif chain_len == 2: score += 10
        elif chain_len == 3: score += 50
        else: score = 1000
    for chain in board.get_all_chains(current_player=False):
        chain_len = len(chain)
        if chain_len == 1: score -= 1
        elif chain_len == 2: score -= 10
        elif chain_len == 3: score -= 50
        else: score = -1000
    if not is_current_player_maximizer: score = -score
    return score
    

# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### Part 2: Searching a Game Tree #############################################

# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.

def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""
    best_path = None
    best_score = 0
    evals = 0
    queue = [[state]]
    while queue:
        path = queue.pop(0)
        
        #check if path has ended, update evals and best score and path
        if path[-1].is_game_over(): 
            score = path[-1].get_endgame_score()
            evals += 1
            if score > best_score:
                best_path = path
                best_score = score
            elif score == best_score:
                if best_path == None or len(path) < len(best_path): 
                    best_path = path
                    best_score = score
        
        #add next depth to queue
        else:
            next_states = path[-1].generate_next_states() 
            new_queue = []
            for next_state in next_states:
                new_path = path.copy()
                new_path.append(next_state)
                new_queue.append(new_path)
            queue = new_queue + queue
    
    return (best_path, best_score, evals)


# Uncomment the line below to try your dfs_maximizing on an
# AbstractGameState representing the games tree "GAME1" from toytree.py:

#pretty_print_dfs_type(dfs_maximizing(GAME1))


def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""
    #base case: leaf node reached, evaluate and return
    if state.is_game_over():
        score = state.get_endgame_score(maximize)
        return ([state], score, 1)
        
    #recursive step
    children = []
    evals = 0
    for child in state.generate_next_states(): 
        out = minimax_endgame_search(child, not maximize)
        evals += out[2]
        children.append(out)
        
    #determine min or max
    if maximize: best = max(children, key=lambda x: x[1])
    else: best = min(children, key=lambda x: x[1])
    return ([state]+best[0], best[1], evals)


# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

# pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))


def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    """Performs standard minimax search. Same return type as dfs_maximizing."""
    #base case: leaf node reached, evaluate and return
    if state.is_game_over():
        score = state.get_endgame_score(maximize)
        return ([state], score, 1)

    #base case: depth limit reached, evaluate and return
    if depth_limit == 0:
        score = heuristic_fn(state.get_snapshot(), maximize)
        return ([state], score, 1)
        
    #recursive step
    children = []
    evals = 0
    for child in state.generate_next_states(): 
        out = minimax_search(child, heuristic_fn, depth_limit-1, not maximize)
        evals += out[2]
        children.append(out)
        
    #determine min or max
    if maximize: best = max(children, key=lambda x: x[1])
    else: best = min(children, key=lambda x: x[1])
    return ([state]+best[0], best[1], evals)


# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1. Try increasing the value of depth_limit to see what happens:

# pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=1))


def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True) :
    """"Performs minimax with alpha-beta pruning. Same return type 
    as dfs_maximizing."""
    #base case: leaf node reached, evaluate and return
    if state.is_game_over():
        score = state.get_endgame_score(maximize)
        return ([state], score, 1)

    #base case: depth limit reached, evaluate and return
    if depth_limit == 0:
        score = heuristic_fn(state.get_snapshot(), maximize)
        return ([state], score, 1)
        
    #recursive step
    children = []
    evals = 0
    for child in state.generate_next_states(): 
        out = minimax_search_alphabeta(child, alpha, beta, heuristic_fn, depth_limit-1, not maximize)
        evals += out[2]
        children.append(out)
        if maximize: alpha = max([alpha, out[1]])
        else: beta = min([beta, out[1]])
        if alpha >= beta: break #prune        
        
    #determine min or max
    if maximize: best = max(children, key=lambda x: x[1])
    else: best = min(children, key=lambda x: x[1])
    return ([state]+best[0], best[1], evals)


# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4. Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

# pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True) :
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    if depth_limit==INF: return None
    anytime = AnytimeValue()
    depth = 1
    while depth != depth_limit+1:
        val = minimax_search_alphabeta(state, -INF, INF, heuristic_fn, depth, maximize)
        if anytime.get_value() != val: anytime.set_value(val)
        depth += 1
    return anytime


# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4. Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

# progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4).pretty_print()


# Progressive deepening is NOT optional. However, you may find that 
#  the tests for progressive deepening take a long time. If you would
#  like to temporarily bypass them, set this variable False. You will,
#  of course, need to set this back to True to pass all of the local
#  and online tests.
TEST_PROGRESSIVE_DEEPENING = True
if not TEST_PROGRESSIVE_DEEPENING:
    def not_implemented(*args): raise NotImplementedError
    progressive_deepening = not_implemented


#### Part 3: Multiple Choice ###################################################

ANSWER_1 = '4'

ANSWER_2 = '1'

ANSWER_3 = '4'

ANSWER_4 = '5'


#### SURVEY ###################################################

NAME = 'Griffin Leonard'
COLLABORATORS = 'None'
HOW_MANY_HOURS_THIS_LAB_TOOK = '6'
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None
SUGGESTIONS = None

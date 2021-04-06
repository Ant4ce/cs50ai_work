"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = 0;
    o_count = 0;
    for every in board:
        for each in every:
            if each == "X":
                x_count += 1
            if each == "O":
                o_count += 1

    if (x_count + o_count)%2 != 0:
        return O
    if (x_count + o_count)%2 != 1:
        return X
    else:
        print("something went wrong in the player function")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions_set = []
    row_counter = -1
    column_counter = -1
    for every in board:
        row_counter += 1
        for each in every:
            column_counter += 1
            if each == None:
                actions_set.append((row_counter, column_counter))
        column_counter = -1
    row_counter =  -1

    return actions_set



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board_deep_copy = copy.deepcopy(board)
        
    if board[action[0]][action[1]] != None:
        raise Exception("that move is illegal given the board state. ")

    board_deep_copy[action[0]][action[1]] = player(board) 

    return board_deep_copy

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #checks for winner on horizontal
    for every in board:
        value_board = every[0]
        if every == [value_board, value_board, value_board]:
            return value_board
    #checks for winner on vertical
    for each in [0,1,2]: 
        if board[0][each] == board[1][each] == board[2][each]:
            return board[0][each]
        
    #checks for winner on diagonal
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    return None
         

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if actions(board) == [] or winner(board) != None:
        return True
    else: 
        return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    if winner(board) == O:
        return -1
    if winner(board) == None:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board) == True:
        return None
    
    if player(board) == X:
        v = [-2,(-1,-1)]
        for every in actions(board):
            if minma(result(board, every)) > v[0]:
                v[1] = every
                v[0] = minma(result(board, every))
        return v[1] 

    if player(board) == O:
        w = [2,(-2,-2)]
        for every in actions(board):
            if maxima(result(board, every)) < w[0]:
                w[1] = every
                w[0] = maxima(result(board, every))
        return w[1]

def maxima(board):
    v = -2
    if terminal(board):
        return utility(board)
    for every in actions(board):
        v = max(v,minma(result(board,every)))
    return v 

def minma(board):
    v = 2
    if terminal(board):
        return utility(board)
    for every in actions(board):
        v = min(v,maxima(result(board,every)))
    return v 

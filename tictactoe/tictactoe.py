"""
Tic Tac Toe Player
"""

import math,copy

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
    count_X = sum(row.count(X) for row in board)
    count_O = sum(row.count(O) for row in board)

    if count_X <= count_O:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    choices=[]
    for i in range(3):
        for j in range(3):
            if board[i][j]==None:
                choices.append((i,j))

    return set(choices)


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] is not None:
        raise ValueError
    temp=copy.deepcopy(board)
    temp[action[0]][action[1]]=player(board)
    return temp


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    for i in range(3):
        if board[i][0]==board[i][1]==board[i][2] and(board[i][2]!=None):
            return board[i][0]
        if board[0][i]==board[1][i]==board[2][i]and(board[2][i]!=None):
            return board[0][i]
    if board[0][0]==board[1][1]==board[2][2]and(board[2][2]!=None):
        return board[1][1]
    if board[0][2]==board[1][1]==board[2][0]and(board[0][2]!=None):
        return board[1][1]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or all(all(cell is not None for cell in row) for row in board):
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    util=0
    if winner(board)==X:
        util=1
    elif winner(board)==O:
        util=-1
    return util



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    def max_value(board):
        if terminal(board):
            return (utility(board),None)
        v=-float("inf")
        for action in actions(board):
            w=max(v,min_value(result(board,action))[0])
            if w!=v:
                v=w
                act=action
        return (v,act)

    def min_value(board):
        if terminal(board):
            return (utility(board),None)
        v=float("inf")
        for action in actions(board):
            w=min(v,max_value(result(board,action))[0])
            if w!=v:
                v=w
                act=action
        return (v,act)

    if terminal(board):
        return None
    elif player(board)==X:
        return max_value(board)[1]
    else:
        return min_value(board)[1]
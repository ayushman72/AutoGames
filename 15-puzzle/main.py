#This is a 15-puzzle solver using A* algorithm.
#This particular cost fuction is weighted so it gives results fast rather than optimal
#Also it does not check if the board is solvable or not

from copy import deepcopy
from queue import PriorityQueue

from typing import Self, Tuple, Iterator

class Node():
    def __init__(self,state:list[list[int]],parent:Self|None=None,moved:Tuple[int,int]|None=None):
        """Creates a node with present state and parent state"""
        self.state = state
        self.parent = parent
        self.moved = moved

    def __hash__(self) -> int:
        k=[]
        for i in self.state:
            k.append(tuple(i))
        return hash(tuple(k))
    
    def __eq__(self,other)-> bool:
        return (self.state == other.state)
        
    def __lt__(self,other)->bool:
        return False
    
    def __repr__(self) -> str:
        if self.parent is not None:
            p = self.parent.state
        else:
            p = None
        return f"state: {self.state}\n parent: {p}\n move = {self.moved} "


global size


def find_empty(state:list[list[int]])->Tuple[int,int]:
    """Finds the empty space in the puzzle"""
    for i in range(size):
        for j in range(size):
            if state[i][j] == 0:
                return (i,j)
    return(-1,-1)

def swapable(state: list[list[int]]) -> Iterator[Tuple[int,int]]:
    empty = find_empty(state)    
    nexts = [(-1,0),(1,0),(0,-1),(0,1)]
    for n in nexts:
        if 0<=empty[0]+n[0]<size and 0<=empty[1]+n[1]<size:
            yield (empty[0]+n[0],empty[1]+n[1])


def swap(state:list[list[int]],idx1:Tuple[int,int]):
    state = deepcopy(state)
    empty = find_empty(state)
    state[idx1[0]][idx1[1]],state[empty[0]][empty[1]] = state[empty[0]][empty[1]],state[idx1[0]][idx1[1]]
    return state


def manhatten_distance(state:list[list[int]])->int:
    distance = 0
    for i in range(size):
        for j in range(size):
            tile = state[i][j]
            if tile != 0:
                target_row = (tile - 1) // size
                target_col = (tile - 1) % size
                distance += abs(i - target_row) + abs(j - target_col)
    return distance


def linear_conflict(position):
        conflict = 0
        # Row conflicts
        for row in range(size):
            max_val = -1
            for col in range(size):
                value = position[row][col]
                if value != 0 and (value - 1) // size == row:
                    if value > max_val:
                        max_val = value
                    else:
                        conflict += 2
        # Column conflicts
        for col in range(size):
            max_val = -1
            for row in range(size):
                value = position[row][col]
                if value != 0 and (value - 1) % size == col:
                    if value > max_val:
                        max_val = value
                    else:
                        conflict += 2
        return conflict


distance = lambda x : manhatten_distance(x) + linear_conflict(x)


size = int(input("Enter the size of the puzzle: "))
solved = list(range(1,size**2))
solved.append(0)
solvedState = [solved[i:i+size] for i in range(0,len(solved),size)]


start = list(map(int,input("Enter the start state of the puzzle: ").split()))
startState = [start[i:i+size] for i in range(0,len(solved),size)]



def astar(start1: list[list[int]],goal: list[list[int]]):
    start = Node(start1)
    queue:PriorityQueue[Tuple[int,Node]] = PriorityQueue()
    queue.put((0+distance(start.state),start))
    explored:set[Node] = set()
    cost_so_far = {start:0}
    
    while not queue.empty():
        _,state = queue.get()
        
        if state.state == goal:
            path =[]
            while state.parent is not None:
                path.append(state)
                state = state.parent
            path.append(state)  
            path.reverse()
            return path
        
        if state in explored:
            continue
        
        explored.add(state)
        for i in swapable(state.state):
            newState = swap(state.state,i)
            newCost = cost_so_far[state] + 1
            new = Node(newState,state,i)
            if new in explored:
                continue
            cost_so_far[new] = newCost
            priority = newCost + int(2*distance(newState))
            queue.put((priority,new))
                
    return None
    
out = astar(startState,solvedState)
l = len(out)
print("Pieces to move -> ")
for i in range(l-1):
    base = out[i].state
    move = out[i+1].moved
    print(base[move[0]][move[1]],end = " ") 

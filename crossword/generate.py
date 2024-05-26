import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword:Crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            dm=self.domains[var].copy()
            for word in self.domains[var]:
                if var.length !=len(word):
                    dm.remove(word)
            self.domains[var]=dm

    def conflict(self, x, y, wordX, wordY):
        """
        Return True if x = wordX and y = wordY has conflict
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
        (i, j) = overlap
        return wordX[i] != wordY[j]

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised=False
        for wordx in self.domains[x].copy():
            if all(self.conflict(x,y,wordx,wordy) for wordy in self.domains[y]):
                self.domains[x].remove(wordx)
                revised=True
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs==None:
            arcs=[]
            for x in self.domains:
                for y in self.crossword.neighbors(x):
                    if self.crossword.overlaps[x,y]:
                        arcs.append((x,y))
        while arcs:
            x,y=arcs.pop(0)
            if self.revise(x,y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x):
                    if z!=y:
                        arcs.append((z,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment)==len(self.crossword.variables):
            return True
        return False

    def consistent(self, assignment:dict[Variable,str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(assignment.values())!=len(set(assignment.values())):
            return False
        for i in assignment:
            if len(assignment[i])!=i.length:
                return False
        for var,word in assignment.items():
            if var.length!=len(word):
                return False
        for x,wX in assignment.items():
            for y,wY in assignment.items():
                if y in self.crossword.neighbors(x) and self.conflict(x,y,wX,wY):
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)

        def elimination_count(word):
            return sum(
                1 for neighbor in neighbors
                if neighbor not in assignment
                and word in self.domains[neighbor]
            )

        return sorted(self.domains[var], key=elimination_count)


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        res=[i for i in self.crossword.variables if i not in assignment]
        def sortby(x):
            # list will be sorted by ascending order of len(domains) and desc wrt number of neighbours
            return(len(self.domains[x]),-len(self.crossword.neighbors(x)))
        res.sort(key=sortby)
        return res[0]

    def inference(self, x, assignment):
        """
        Draw inference from assignment of variable x. Returns False if assignment
        to variable x cannot maintain arc consistency, otherwise True.
        """

        def maintain_arc_consistency(x):
            """
            Returns True if arc consistency is enforced and no domain is empty,
            False otherwise.
            """
            arcs = []
            for y in self.crossword.neighbors(x):
                if y not in assignment:
                    arcs.append((y, x))
            return self.ac3(arcs)

        if maintain_arc_consistency(x):
            for var, values in self.domains.items():
                if len(values) == 1:
                    value = list(values)[0]
                    if value not in assignment.values():
                        assignment[var] = value
            return True
        return False

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var=self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var,assignment):
            restore = assignment.copy(), copy.deepcopy(self.domains)
            if self.consistent(assignment | {var: value}):
                assignment[var], self.domains[var] = value, {value}
                inferences = self.inference(var, assignment)
                if not inferences:
                    return None
                result = self.backtrack(assignment)
                if result is not None:
                    return result

            assignment, self.domains = restore
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
 
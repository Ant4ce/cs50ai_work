import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for variable in self.crossword.variables:
            words_for_removal = set()
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    words_for_removal.add(word)

            self.domains[variable] = self.domains[variable].difference(words_for_removal)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        crossover = self.crossword.overlaps[x, y]
        bool_return = False

        if crossover is not None:
            words_for_removal = set()
            for word in self.domains[x]:
                if all(other_words[crossover[1]] != word[crossover[0]] for other_words in self.domains[y]):
                    words_for_removal.add(word)
                    bool_return = True
            #print("before removal: ")
            #print(words_for_removal)
            #print(self.domains[x])
            self.domains[x] = self.domains[x].difference(words_for_removal)
            #print("after removal: ")
            #print(self.domains[x])

        return bool_return

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        list_queue = arcs

        if arcs is None:
            list_queue = []
            for variable in self.crossword.variables:
                for other_var in self.crossword.variables:
                    if variable == other_var:
                        continue
                    if (variable, other_var) in list_queue:
                        continue

                    list_queue.append((variable, other_var))


        while list_queue != []:

            current_arc = list_queue.pop(0)
            #print(current_arc)
            if self.revise(current_arc[0], current_arc[1]):
                if len(self.domains[current_arc[0]]) == 0:
                    return False
                neighboring_set = self.crossword.neighbors(current_arc[0])
                neighboring_set.remove(current_arc[1])
                for every in neighboring_set:
                    list_queue.append((every, current_arc[0]))
        
        return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return False
            if assignment[variable] not in self.crossword.words:
                return False
        return True

         

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        for variable, word in assignment.items():
            if variable.length != len(word):
                return False
            for other_var, word_other in assignment.items():
                if variable == other_var:
                    continue
                if  word == word_other:
                    return False

                crossover = self.crossword.overlaps[variable, other_var] 
                if crossover:
                    x, y = crossover
                    if word[x] != word_other[y]:
                        return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        word_dict = {} 

        for word in self.domains[var]:
            word_dict.update({word : 0}) 
            for variable in assignment:
                if var == variable:
                    continue
                crossover = self.crossword.overlaps[var, variable]
                if crossover is None:
                    continue
                for other_word in self.domains[variable]:
                    if word[crossover[0]] != other_word[crossover[1]]:
                        word_dict[word] += 1

        sorted_word_list = sorted(word_dict, key=word_dict.get )

        return sorted_word_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        my_dict_words = {}
        my_dict_neighbours = {}
        for variable in self.crossword.variables:
            if variable not in assignment:
                my_dict_words.update({variable: len(self.domains[variable])})
                my_dict_neighbours.update({variable: len(self.crossword.neighbors(variable))})

        sorted_variables = sorted(my_dict_words, key=my_dict_words.get) 
        sorted_neighbours = sorted(my_dict_neighbours, key= my_dict_neighbours.get)
        if len(my_dict_words) > 1: 
            if my_dict_words[sorted_variables[0]] == my_dict_words[sorted_variables[1]]:
                if my_dict_neighbours[sorted_variables[0]] == my_dict_neighbours[sorted_variables[1]]:
                    return sorted_neighbours[0]
                
                if my_dict_neighbours[sorted_variables[0]] < my_dict_neighbours[sorted_variables[0]]:
                    return sorted_neighbours[1]

        return sorted_variables[0]
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete( assignment):
            return assignment

        var = self.select_unassigned_variable( assignment)
        for word in self.order_domain_values( var, assignment):
            assignment[var] = word
            if self.consistent( assignment):
                result = self.backtrack( assignment)
                if result is not None: 
                    return result
            assignment.pop(var)
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

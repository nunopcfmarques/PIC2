import numpy as np
import random
from typing import Any
from src.utils import Tree
import re

'''
TLogic is a class that holds some place holder truth functions that are meant to be used as methods os a subclass TLogic if it does not explicitly use them. 
It also contains the methods to constract the abstract syntax tree and to evaluate the formula.
Additionally it defines the set of connectives and how we can map them to their respective truth functions.
'''

class TLogic:
    connectives = {"¬", "⊙", "⊕", "⇒", "δ", "!=", "=="}

    connectives_to_truth_function = {
        "¬": "NEG",
        "⊙": "CONJ",
        "⊕": "DISJ",
        "⇒": "IMPLIES",
        "δ": "DELTA",
        "==": "EQUALS",
        "!=": "UNEQUALS",
    }
    
    def random_formula(self, atoms: list, choosable_connectives: list, max_depth) -> str:
        if max_depth == 0:
            return random.choice(atoms)

        connective = random.choice(choosable_connectives)
        if connective == "¬":
            return f"(¬{self.random_formula(atoms, choosable_connectives, max_depth - 1)})"
        
        elif connective == "δ": # we leave spaces
            return f"(δ_{random.randint(1, 15)} {self.random_formula(atoms, choosable_connectives, max_depth - 1)})"
        
        elif connective == "":
            return random.choice(atoms)
        else:
            return f"({self.random_formula(atoms, choosable_connectives, max_depth - 1)}{connective}{self.random_formula(atoms, choosable_connectives, max_depth - 1)})"
    

    @staticmethod
    def subdivide_formula(formula: str) -> tuple:
        # Takes the parenthesis out of the formula and divides it according to its arity
        if formula.startswith("(") and formula.endswith(")"):
            formula = formula[1:-1]

        subformula_count = 0
        for index, character in enumerate(formula):
            if character == "(":
                subformula_count += 1
            elif character == ")":
                subformula_count -= 1
            elif subformula_count == 0 and character in TLogic.connectives:
                if character == "¬":
                    return formula[index + 1:], None, character
                elif character == "δ":
                    i = re.match(r'\d+', formula[index + 2:]).group(0)
                    return formula[index + 3 + len(i):], None, f"{character}{i}" # we need to get δ_i and i is the next character
                elif character == "!":
                    return formula[:index], formula[index + 2:], "!="
                elif character == "=":
                     return formula[:index], formula[index + 2:], "=="
                else:
                    return formula[:index], formula[index + 1:], character

        return formula, None, None
    
    @staticmethod
    def is_atom(formula: str) -> bool:
        # atoms are always a character followed by 0 or more digits
        return re.match(r'[a-zA-Z]\d*', formula)
    
    @staticmethod
    def is_constant(formula: str) -> bool:
        return formula == "0" or formula == "1"
    
    def generate_ast(self, formula: str, depth: int = 0) -> tuple[Tree.Node, int, list[str]]:
        if self.is_atom(formula):
            return Tree.Node(formula, depth), depth
        
        elif self.is_constant(formula):
            return Tree.Node(formula, depth), depth

        else:
            l_formula, r_formula, connective = self.subdivide_formula(formula)
            root = Tree.Node(connective, depth)
            if connective[0] == "¬":
                left_node, max_depth = self.generate_ast(l_formula, depth + 1)
                root.left = left_node
            elif connective[0] == "δ":
                left_node, max_depth = self.generate_ast(l_formula, depth + 1)
                root.left = left_node
            else:
                left_node, left_max_depth = self.generate_ast(l_formula, depth + 1)
                right_node, right_max_depth = self.generate_ast(r_formula, depth + 1)
                root.left = left_node
                root.right = right_node
                max_depth = max(left_max_depth, right_max_depth)

            return root, max_depth
    
    def generate_ast_with_degs(self, formula:str, subformula_to_node={}, depth=0) -> tuple[Tree.Node, int]:
        if formula in subformula_to_node:
            return subformula_to_node[formula]
        
        elif self.is_atom(formula):
            return Tree.Node(formula, depth), depth
        
        elif self.is_constant(formula):
            return Tree.Node(formula, depth), depth
        
        else:
            l_formula, r_formula, connective = self.subdivide_formula(formula)
            root = Tree.Node(connective, depth)
            if connective[0] == "¬":
                left_node, max_depth = self.generate_ast_with_degs(l_formula, subformula_to_node, depth + 1)
                root.left = left_node

            elif connective[0] == "δ":
                left_node, max_depth = self.generate_ast_with_degs(l_formula, subformula_to_node, depth + 1)
                root.left = left_node

            else:
                left_node, left_max_depth = self.generate_ast_with_degs(l_formula, subformula_to_node, depth + 1)
                right_node, right_max_depth = self.generate_ast_with_degs(r_formula, subformula_to_node, depth + 1)
                root.left = left_node
                root.right = right_node
                max_depth = max(left_max_depth, right_max_depth)

            subformula_to_node[formula] = (root, max_depth)
            return subformula_to_node[formula]
    
    def get_function_name(self, connective: str) -> Any:
        return getattr(self, self.connectives_to_truth_function[connective[0]])
    
    def evaluate_formula(self, root: Tree.Node, val: dict) -> np.float64:
        if root.left == None:
            if root.data in val:
                return val[root.data]
            try:
                return float(root.data)
            except:
                return TLogic.characters_to_truth_function[root.data]()
            
        else:
            function = self.get_function_name(root.data)

            if root.data[0] == "¬":
                eval = function(self.evaluate_formula(root.left, val))
            elif root.data[0] == "δ":
                eval = function(root.data[1:], self.evaluate_formula(root.left, val))
            else:
                eval = function(self.evaluate_formula(root.left, val), self.evaluate_formula(root.right, val))
        
            return eval

# Here the multiplicative connectives collapse! meaning ∧ is ⊙ and ∨ is ⊕
class Godel(TLogic):
    def IMPLIES(self, x: np.float64, y: np.float64) -> np.float64:
        return y if x > y else np.float64(1)
    
    #v(A∧B) = min(v(A),v(B))
    def CONJ(self, x: np.float64, y: np.float64) -> np.float64:
        return np.minimum(x, y)

    #v(A∨B) = max(v(A),v(B))
    def DISJ(self, x: np.float64, y: np.float64) -> np.float64:
        return np.maximum(x, y)

class Product(TLogic):
    @staticmethod
    def CONJ(x: np.float64, y: np.float64) -> np.float64:
        pass

    @staticmethod
    def DISJ(x: np.float64, y: np.float64) -> np.float64:
        pass

    @staticmethod
    def NEG(x: np.float64) -> np.float64:
        pass


class Lukasiewicz(TLogic):
    #v(A → B) = min(1,1−v(A) +v(B))
    def IMPLIES(self, x: np.float64, y: np.float64) -> np.float64:
        return np.float64(np.minimum(1, 1 - x + y))

    #v(A⊙B) = max(0,v(A) +v(B)−1)
    def CONJ(self, x: np.float64, y: np.float64) -> np.float64:
        return np.float64(np.maximum(0, x + y - 1))

    #v(A⊕B) = min(1,v(A) +v(B))
    def DISJ(self, x: np.float64, y: np.float64) -> np.float64:
        return np.float64(np.minimum(1, x + y))
    
    #v(¬A) = 1−v(A)
    def NEG(self, x: np.float64) -> np.float64:
        return np.float64(1 - x)
    
    def DELTA(self, i: int, x: np.float64 = 1.) -> np.float64:
        return np.float64(x / int(i))
    
    def EQUALS(self, x: np.float64, y: np.float64) -> np.float64:
        return np.float64(x == y)

    def UNEQUALS(self, x: np.float64, y: np.float64) -> np.float64:
        return np.float64(x != y)
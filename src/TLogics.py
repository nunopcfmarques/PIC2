import numpy as np
import random
from typing import Any
from src.utils import Tree

'''
TLogic is a class that holds some place holder truth functions that are meant to be used as methods os a subclass TLogic if it does not explicitly use them. 
It also contains the methods to constract the abstract syntax tree and to evaluate the formula.
Additionally it defines the set of connectives and how we can map them to their respective truth functions.
'''

class TLogic:
    connectives = {"¬", "⊙", "⊕", "⇒"}

    connectives_to_truth_function = {
        "¬": "NEG",
        "⊙": "CONJ",
        "⊕": "DISJ",
        "⇒": "IMPLIES",
    }

    truth_values_to_truth_function = {
        "T": "TRUE",
        "⊥": "FALSE",
    }

    def IMPLIES(self, x, y):
        pass

    def FALSE(self):
        return 0

    # 0 → 0
    def TRUE(self):
        return self.IMPLIES(self.FALSE(), self.FALSE())

    # ¬A = A → ⊥
    def NEG(self, x):
        return self.IMPLIES(x, self.FALSE())

    # A⊙B = ¬(A → ¬B) 
    def CONJ(self, x, y):
        return self.NEG(self.IMPLIES(x, self.NEG(y)))

    # A⊕B = ¬A → B
    def DISJ(self, x, y):
        return self.IMPLIES(self.NEG(x), y)
    
    def random_formula(self, atoms: list, choosable_connectives: list, max_depth) -> str:
        if max_depth == 0:
            return random.choice(atoms)

        connective = random.choice(choosable_connectives)
        if connective == "¬":
            return "(¬" + self.random_formula(atoms, choosable_connectives, max_depth - 1) + ")"
        elif connective == "":
            return random.choice(atoms)
        else:
            return "(" + self.random_formula(atoms, choosable_connectives, max_depth - 1) + connective + self.random_formula(atoms, choosable_connectives, max_depth - 1) + ")"
    

    @staticmethod
    def subdivide_formula(formula: str) -> tuple:
        '''
        Takes the parenthesis out of the formula and divides it according to its arity
        '''
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
                else:
                    return formula[:index], formula[index + 1:], character

        return formula, None, None
    
    def generate_ast(self, formula: str, depth=0) -> tuple[Tree.Node, int]:
        if len(formula) == 1:
            return Tree.Node(formula, depth), depth

        else:
            l_formula, r_formula, connective = self.subdivide_formula(formula)
            root = Tree.Node(connective, depth)
            if connective == "¬":
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
        elif len(formula) == 1:
            subformula_to_node[formula] = Tree.Node(formula, depth), depth
            return subformula_to_node[formula]
        else:
            l_formula, r_formula, connective = self.subdivide_formula(formula)
            root = Tree.Node(connective, depth)
            if connective == "¬":
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
        return getattr(self, self.connectives_to_truth_function[connective])
    
    def evaluate_formula(self, root: Tree.Node, val: dict) -> np.float64:
        if root.left == None:
            if val[root.data] in self.truth_values_to_truth_function:
                return getattr(self, self.truth_values_to_truth_function[val[root.data]])()
            else:
                return val[root.data]
        else:
            function = self.get_function_name(root.data)

            if root.data == "¬":
                eval = function(self.evaluate_formula(root.left, val))
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
        return np.minimum(np.float64(1), np.float64(1) - x + y)

    #v(A⊙B) = max(0,v(A) +v(B)−1)
    def CONJ(self, x: np.float64, y: np.float64) -> np.float64:
        return np.maximum(np.float64(0), x + y - np.float64(1))

    #v(A⊕B) = min(1,v(A) +v(B))
    def DISJ(self, x: np.float64, y: np.float64) -> np.float64:
        return np.minimum(np.float64(1), x + y)
    
    #v(¬A) = 1−v(A)
    def NEG(self, x: np.float64) -> np.float64:
        return np.float64(1) - x
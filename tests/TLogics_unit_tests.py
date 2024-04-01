import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.TLogics import *

val = {'A': np.float64(0.7), 'B': np.float64(0.5)}

result, depth = Lukasiewicz.generate_ast("(A⊙B)")
print("Level Order Traversal: " + str(Tree.level_order_traversal(result)) + " Expected Result: [(⊙, 0), (A, 1), (B, 1)]")
print(depth)

result = Lukasiewicz.evaluate_formula(result, val)
print("Example 1: " + str(result) + " Expected Result: 0.2") 

result, depth = Lukasiewicz.generate_ast("(A⇒B)")
print("Level Order Traversal: " + str(Tree.level_order_traversal(result)) + " Expected Result: [(⇒, 0), (A, 1), (B, 1)]")
print(depth)

result = Lukasiewicz.evaluate_formula(result, val)
print("Example 2: " +  str(result) + " Expected Result: 0.8") 

result, depth = Lukasiewicz.generate_ast("(¬A)")
print("Level Order Traversal: " + str(Tree.level_order_traversal(result)) + " Expected Result: [(¬, 0), (A, 1)]")
print(depth)

result = Lukasiewicz.evaluate_formula(result, val)
print("Example 3: " + str(result) + " Expected Result: 0.3") 

result, depth = Lukasiewicz.generate_ast("(A⇒(B⊕(¬A)))")
print("Level Order Traversal: " +  str(Tree.level_order_traversal(result)) + " Expected Result: [(⇒, 0), (A, 1), (⊕, 1), (B, 2), (¬, 2), (A, 3)]")
print(depth)

result = Lukasiewicz.evaluate_formula(result, val)
print("Example 4: " + str(result) + " Expected Result: 1")

result, depth = Lukasiewicz.generate_ast("(A⊙(B⇒(¬A)))")
print("Level Order Traversal: " + str(Tree.level_order_traversal(result)) + " Expected Result: [(⊙, 0), (A, 1), (⇒, 1), (B, 2), (¬, 2), (A, 3)]")
print(depth)

result = Lukasiewicz.evaluate_formula(result, val)
print("Example 5: " + str(result) + " Expected Result: 0.5")
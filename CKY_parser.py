from nltk.data import load
from nltk import grammar
import numpy as np
import os, sys, re

class Cell:
    """
    A cell in the matrix for CKY parsing algorithm.
    """
    def __init__(self):
        """
        Construct a cell with lists of nodes and corresponding backpointers
        
        :param nodes: stores the nltk.grammar.Nonterminal objects on the lhs of all valid rules that produce the subtree 
            corresponding to the cell.
        :type nodes: list of nltk.grammar.Nonterminal objects
        :param backpointers: stores the index of the rhs constituents that form the corresponding Nonterminal in nodes
            in the format of ((row, column, index of node in Cell.nodes), (row, column, index of node in Cell.nodes))
        :type backpointers: list of tuples of tuples of integers
        :param word: stores the corresponding word in the case of lexical cells
        :type word: str
        
        """
        self.nodes = []
        self.backpointers = []
        self.word = ""
    
    def __repr__(self):
        """
        Return the string representaion of nodes
        
        :rtype: str
        """
        return f"{str(self.nodes)}->{str(self.backpointers)}->{self.word}" 
    
class TreeNode:
    """
    A TreeNode object to store the result of the CKY parsing matrix after backtracking as a binary parse tree.
    """
    def __init__(self, node, word=""):
        """
        Construct a TreeNode from a given grammar.Nonterminal object and a string in the case of lexical nodes.
        
        :param node: the nonterminal of this TreeNode
        :type node: nltk.grammar.Nonterminal
        :param left: the left child of this TreeNode
        :type left: TreeNode
        :param right: the right child of this TreeNode
        :type right: TreeNode
        :param word: the word corresponding to the node if it is the lhs of a lexical rule
        :type word: str
        
        """
        self.node = node
        self.left = None
        self.right = None
        self.word = word
    
    def __repr__(self):
        return str(self.node)
        
def backtrack(matrix, node, backpointers, idx, col_idx, sent):
    """
    Construct a binary parse tree with TreeNode objects backtracking from the CKY parse matrix.
    """
    
    # reached lexical cell
    if not backpointers:
        return TreeNode(node, sent[col_idx])
    
    new_node = TreeNode(node)
    bp = backpointers[idx]
    left_cell = matrix[bp[0][0], bp[0][1]]
    right_cell = matrix[bp[1][0], bp[1][1]]
    left_idx = bp[0][2]
    right_idx = bp[1][2]

    new_node.left = backtrack(matrix, left_cell.nodes[left_idx], left_cell.backpointers, left_idx, bp[0][1]-1, sent)
    new_node.right = backtrack(matrix, right_cell.nodes[right_idx], right_cell.backpointers, right_idx, bp[1][1]-1, sent)
        
    return new_node
    

def print_tree(TreeNode, out_file, depth=0):
    """
    Print out the binary parse tree of TreeNode objects in human readable format.
    """
    q = []
    # each node has exactly 0 or 2 children
    print("\t" * depth + f"{str(TreeNode)}", end=" ", file=out_file)
    if TreeNode.right is not None:
        q.append(TreeNode.left)
        q.append(TreeNode.right)
    if not len(q):
        print(f"({TreeNode.word})", file=out_file)
        return
    print(file=out_file)
    for node in q:
        print_tree(node, out_file, depth + 1)
        


def CKY_parse(my_gr, sent):
    """
    Parse a given sentence using Cocke-Younger-Kasami algorithm.
    
    :param my_gr: chomsky normal form grammar
    :type my_gr: nltk.grammar.CFG
    :param sent: sentence to be parsed
    :type sent: list of tokens that correspond to the lexical rules in my_gr
    
    :rtype: list of possible parses stored in TreeNode objects as binary parse trees
    """
    len_sent = len(sent)
    
    # init matrix with one column padding to the left
    matrix = np.frompyfunc(Cell, 0, 1)(np.empty((len_sent,len_sent+1), dtype=object))

    # fill out the CKY parsing matrix
    for i in range(1, len_sent+1): # columns
        for j in range(i - 1, -1, -1): # row
            if j + 1 == i:
                matrix[j, i].nodes = [rule.lhs() for rule in my_gr.productions(rhs=sent[i-1])]
                matrix[j, i].word = sent[i-1]
            else:
                for k in range(j + 1, i): # all posible binary splits s.t. j < k < i
                    for idxA, nodeA in enumerate(matrix[j, k].nodes):
                        for rule in my_gr.productions(rhs=nodeA):
                            rhs = rule.rhs()
                            if len(rhs) > 1:
                                for idxB, nodeB in enumerate(matrix[k, i].nodes):
                                    if rhs[1] == nodeB:
                                        matrix[j, i].nodes.append(rule.lhs())
                                        matrix[j, i].backpointers.append(((j,k,idxA),(k,i,idxB)))
                                        
    # Backtrack parsed result and form a binary parse tree 
    parses = []
    if my_gr.start() in matrix[0, len_sent].nodes: # check if sent is accepted by our grammar
        for i, node in enumerate(matrix[0, len_sent].nodes):
            if node == my_gr.start():
                S = backtrack(matrix, node, matrix[0, len_sent].backpointers, i, len_sent-1, sent)
                parses.append(S)
    
    return parses
                                        
                                        
if __name__ == "__main__":

    inp = sys.argv[1]
    test = sys.argv[2]
    out = sys.argv[3]
    # load cfg grammar in cnf
    my_gr = load(f"{inp}")
    
    # load sentences to parse
    with open(f"{cwd}/{test}") as f:
        sentences = f.readlines()
        
    res = []
    for sent in sentences:
        sent = re.findall(r"[\w']+|[.,!?;]", sent)
        parses = CKY_parse(my_gr, sent)
        res.append(parses)
    
    out_file = open(f"{out}", "w")
    for i, parses in enumerate(res):
        print(sentences[i], end="", file=out_file)
        for parse in parses:
            print_tree(parse, out_file)
        print(f"Number of parses: {len(parses)}\n", file=out_file)



        
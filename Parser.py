from NLP import *
import nltk
from grammar import *
from IPython.display import display
import math

class Parser:
    def __init__(self, text):
        self.reset()
        self.text = text
        tokenizer = NLP(self.text)
        tokenizer.tokenize()
        self.tokens = tokenizer.dirty_tokens
        self.parsed_text = nltk.pos_tag(self.tokens)
        self.table = [[[] for i in range(len(self.tokens))] for j in range(len(self.tokens))]
        self.links_table = [[[] for i in range(len(self.tokens))] for j in range(len(self.tokens))]
    
    def reset(self):
        self.text = []
        self.parsed_text = []
        self.tokens = []
        self.links_table = []

    def get_all_tags(self, index):
        """
        Function to get all possible grammar tags of a token.
        The input is the index of the token in the sentence.
        """
        tags = []
        tags.append(self.parsed_text[index][1]) # getting the PoS of the token
        flag = True
        while(flag):
            flag = False
            for key in rules.keys():
                for rule in rules[key]:
                    # if the PoS is the singular rule then add the key of the dictionary that corresponds to that PoS
                    if rule[0] in tags and len(rule) == 1 and not(key in tags):
                        tags.append(key)
                        flag = True
        #del tags[0] # deleting the Penn treebank tag at the first position
        return tags
    
    def check_possible_pairs(self, set1, set2): 
        """
        A function which check if there is rule that is formed as a pair of 
        two tags from two sets of tags.
        """
        tag_rules = []
        tags = []
        product = [[a, b] for a in set1 for b in set2] # cartesian product of two sets
        indices = [] # where the indices of the chosen constituents will be stored 
        s = 0
        for p in product:
            for key in rules.keys():
                for rule in rules[key]:
                    if rule == p: # and not(key in tags): # if the rule is among the product add it to the tags
                        tag_rules.append(p)
                        tags.append(key)
                        # to retrieve the original indices from the lists that made the cartesian product list we need to do the following
                        # e.g. l1 = ['a', 'b', 'c'], l2 = ['d', 'e'], l = l1xl2 = ['ad','ae', 'bd', 'be', 'cd' 'ce']
                        # e.g. we want to know the indices of 'bd' which has ind = 2 in l
                        # so, ind1 = floor(ind/len(l2)) = 1, ind2 = ind mod len(2) = 0, so the l1[1] = b, l2[0] = d
                        indices.append([math.floor(s/len(set2)), s%len(set2)])
                        #indices.append([s%len(set1), s%len(set2)])
                        #break
            s = s + 1
        return tags, tag_rules, indices

    def parse(self):
        """
        Main function for parsing a sentence using the CKY algorithm. 
        """
        for j in range (len(self.table)):
            self.table[j][j] = self.get_all_tags(j) # getting all the tags for the diagonal entries
            for i in range(j-1, -1, -1):
                for k in range(i,j):
                    # checking possible pairs of tags which could be used as the RHS of a constituent rule
                    tags, tag_rules, indices = self.check_possible_pairs(self.table[i][k], self.table[k+1][j]) # left cells, lower cells
                    # extending the current table entry with the non-terminals gotten from the possible pairs of the left and lower cells
                    self.table[i][j].extend(tags) 
                    # this part stores the links between the gotten non-terminals and the RHS constituents that formed them
                    # can be thought as a possible node in the end graph
                    # it has the form [(a, b, c, <Name1>), (d, e, f, <Name2>)] of the two RHS constituents that formed it together with
                    # the the cell index they came from (e.g. a & b), their index in the cell they came from (e.g. c), and their name (e.g. <Name>)
                    for tag, tag_rule, index in zip(tags, tag_rules, indices):
                        self.links_table[i][j].append([(i, k, index[0], tag_rule[0]), 
                            (k+1, j, index[1], tag_rule[1]), tag])
        return self.table, self.links_table
    
    def make_tree(self):
        """
        The function that outputs the actual parse trees in the bracket and graph form.
        """
        bracket_trees = [] # where the bracket form is stored
        graph_trees = [] # where the graph form is store (for the nltk library needs)
        # the last cell of the first row of the links table contains the start symbol ("S")
        for cell in self.links_table[0][-1]:
            if cell[2] == "S":
                # inputting the cell for the tree generation function
                bracket_trees.append(self.gen_tree(cell, mode="bracket"))
                graph_trees.append(self.gen_tree(cell, mode="graph"))
        # printing the output
        for tree, v_tree in zip(bracket_trees, graph_trees):
            print(tree)
            display(v_tree)
            #v_trees.draw()
            
    
    def gen_tree(self, node, mode="bracket"):
        """
        Recursive approach to get the parse tree from the linking table.
        """
        # case when we have a terminal (marked as node[0] = -1)
        if node[0] == -1:
            if mode == "bracket":
                # write the terminal name (node[1]) and the token name (node[2])
                return f"[{node[1]} '{node[2]}']"
            elif mode == "graph":
                return nltk.Tree(node[1], [node[2]])
        # a node is made up of two children nodes (node[0] and node[1])
        # a the first three entries of a children node contain the linking information (their cell indices, like a 3D array)
        # the row and column in the linking table and the index of the constituent in that cell
        # the fourth entry of the cell is the name of the constituent
        node1_index = node[0][0:3]
        node2_index = node[1][0:3]
        node1 = []
        node2 = []
        # case for terminal node (row and column are the same), change the structure of the node as [-1, <constituent name>, <token>]
        if node1_index[0] == node1_index[1]:
            node1 = [-1, node[0][3], self.tokens[node1_index[0]]]
        # in the other case the extract the child node information from the table (3D array as explained before)
        else:
            node1 = self.links_table[node1_index[0]][node1_index[1]][node1_index[2]]
        # same thing for the other child node
        if node2_index[0] == node2_index[1]:
            node2 = [-1, node[1][3], self.tokens[node2_index[0]]]
        else:
            node2 = self.links_table[node2_index[0]][node2_index[1]][node2_index[2]]

        # recursively call this function with the two children nodes as inputs
        if mode == "bracket":
            return f"[{node[2]} {self.gen_tree(node1)} {self.gen_tree(node2)}]"
        elif mode == "graph":
            return nltk.Tree(node[2], [self.gen_tree(node1, mode), self.gen_tree(node2, mode)])

    def save_table(self, path):
        """
        Function to save the parse table as a .txt file.
        """
        f = open(path,'w')
        for tab in self.table:
            for t in tab:
                print("{0:25}".format(str(t)), file = f, end = "")
            print("", file=f) 

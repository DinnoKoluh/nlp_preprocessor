from NLP import *
import nltk
from grammar import *

class Parser:
    def __init__(self, text):
        self.reset()
        self.text = text
        tokenizer = NLP(self.text)
        tokenizer.tokenize()
        self.tokens = tokenizer.dirty_tokens
        self.parsed_text = nltk.pos_tag(self.tokens)
        self.table = [[[] for i in range(len(self.tokens))] for j in range(len(self.tokens))]
        self.my_table = [[[] for i in range(len(self.tokens))] for j in range(len(self.tokens))]
    
    def reset(self):
        self.text = []
        self.parsed_text = []
        self.tokens = []
        self.my_table = []

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
        for p in product:
            for key in rules.keys():
                for rule in rules[key]:
                    if rule == p and not(key in tags): # if the rule is among the product add it to the tags
                        tag_rules.append(p)
                        tags.append(key)
                        #break
        # use as of now, later will be abolished when multiple rules can be output
        return tags, tag_rules

    def parse(self):
        links = []

        for j in range (len(self.table)):
            self.table[j][j] = self.get_all_tags(j)
            for i in range(j-1, -1, -1):
                for k in range(i,j):
                    tags, tag_rules = self.check_possible_pairs(self.table[i][k], self.table[k+1][j]) # left cell, lower cell
                    self.table[i][j].extend(tags)
                    for tag, tag_rule in zip(tags, tag_rules):
                        self.my_table[i][j].append([(i,k, tag_rule[0]), (k+1,j, tag_rule[1]), tag])
                    # for tag_rule in tag_rules:
                    #     tag_rule.append([(i,j), (i, k), (k+1, j)])
                    links.extend(tag_rules)
        return self.table, links, self.my_table
    
    def make_tree(self):
        n_parses = self.table[0][-1].count("S")
        trees = []
        tree_index = 0
        for cell in self.my_table[0][-1]:
            if cell[2] == "S":
                trees.append(["S"])
                left_cell = cell[0][0:2]
                bottom_cell = cell[1][0:2]
                
                #nth_list = [my_table]
                # left cell empty
                if self.my_table[left_cell[0]][left_cell[1]] == []:
                    pass
                    #nth_list.append(c[])

                tree_index = tree_index + 1
    
    def gen_tree(self, node):
        if node[0][0] == node[0][1]:
            index = node[0][0]
            return f"[{self.my_table[index][index]} '{self.tokens[index]}']"
        node1_index = node[0][0:2]
        node2_index = node[1][0:2]
        #return f"[{node[3]} {self.gen_tree(self.my_table[][])} {}]"

    def save_table(self, path):
        """
        Function to save the parse table as a .txt file.
        """
        f = open(path,'w')
        for tab in self.table:
            for t in tab:
                print("{0:25}".format(str(t)), file = f, end = "")
            print("", file=f) 

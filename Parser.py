from NLP import *
import nltk
from grammar import *

class Parser:
    text = ""
    parsed_text = ""
    tokens = ""

    def __init__(self, text):
        self.reset()
        self.text = text
        tokenizer = NLP(self.text)
        tokenizer.tokenize()
        self.tokens = tokenizer.dirty_tokens
        self.parsed_text = nltk.pos_tag(self.tokens)
    
    def reset(self):
        self.text = []
        self.parsed_text = []
        self.tokens = []

    def make_CKY_table(self, length):
        """
        Function to make a template of the CKY table based on the length of the 
        sequence of words.
        """
        table = [None] * length
        for i in range (length):
            table[i] = [None] * (length-i)
        return table

    def get_all_tags(self, index):
        """
        Function to get all possible grammar tags of a token.
        The input is the index of the token in the sentence.
        """
        tags = []
        pos = self.parsed_text[index][1] # getting the PoS of the token
        if index == 0:
            tags.append("S")
        flag = True
        while(flag):
            flag = False
            for key in rules.keys():
                for rule in rules[key]:
                    # if the PoS is the singular rule then add the key of the dictionary that corresponds to that PoS
                    if pos == rule[0] and len(rule) == 1 and not(key in tags):
                        tags.append(key)
                        pos = key
                        flag = True
        return tags
    
    def check_possible_pairs(self, set1, set2): 
        """
        A function which check if there is rule that is formed as a pair of 
        two tags from two sets of tags.
        """
        tag_rules = []
        product = [[a, b] for a in set1 for b in set2] # cartesian product of two sets
        for p in product:
            for key in rules.keys():
                for rule in rules[key]:
                    if rule == p: # if the rule is among the product add it to the tags
                        tag_rules.append([key, p])
                        break
        return tag_rules

    def parse(self):
        table = self.make_CKY_table(len(self.tokens))
        links = [None] * (len(table)-1)
        for j in range (len(table)):
            table[j][0] = self.get_all_tags(j)
            # print("column " + str(j))
            for i in range(j-1, -1, -1):
                # j is shifted as (j - i)
                # print("Current table entry: [" + str(i) + " " + str(j-i) + "]")
                # print("Set1: " + str(table[i][0]))
                # print("Set2: " + str(table[i+1][j-i-1]))
                tag_rules = self.check_possible_pairs(table[i][0], table[i+1][j-i-1])
                tag = []
                if len(tag_rules) > 0:
                    tag = [tag_rules[0][0]]
                table[i][j-i] = tag

                if j == len(table) - 1:
                    links[i] = tag_rules[0]
                
        return table, links

        # I eat sushi
        # [S      [NP    [I]]    [VP      [Verb    [eat]]      [Nominal     [Sushi] ]]]
            


        

from lexicons import * # getting the lexicons for contractions, abbreviations, stop-words
from PorterStemmer import *

class NLP:
    rough_tokens = [] # tokens gathered after only removing whitespaces and newlines from text, useful for sentence reconstruction
    dirty_tokens = [] # tokens separated from punctuations but punctuations are still regarded as valid tokens
    tokens = [] # clean tokens where only tokens that begin with a number of letter are kept as valid tokens
    stemmed_tokens = [] # tokens obtained after the Porter stemming of clean tokens
    pruned_tokens = [] # tokens for which stop-words were removed after stemming
    sentences = []
    text = []
    vocabulary = []
    # punctuation lists which are valid for a specific type of tokens
    puncs = ['.', ',', '!', '?', '(', ')', ':', ';', '"', '"', '\'']
    email_puncs = [',', '!', '?', '(', ')', ':', ';', '"', '"', '\'']
    web_puncs = [',', '!', '?', '(', ')', ';', '"', '"']

    def __init__(self, text):
        self.reset()
        self.text = text
    
    def reset(self):
        self.rough_tokens = []
        self.tokens = []
        self.stemmed_tokens = []
        self.dirty_tokens = []
        self.pruned_tokens = []
        self.sentences = []
        self.text = []
        self.vocabulary = []

    # rough tokenization where only whitespaces and newlines are removed from text
    def tokenize_rough(self):
        splitters = [' ', '\n'] # chars used for splitting words
        word = '' # where to store a single word
        self.rough_tokens = [] 
        i = 0
        while i < len(self.text):
            split = False # flag if we are going to split e.g. add a new token
            while self.text[i] in splitters: # while the i-th character is among splitters keep splitting
                split = True
                i = i + 1 # skip that position in text
                if i == len(self.text):
                    break

            if split:
                if word == '': continue # in the case we have an empty document with ' ' and '\n'
                self.rough_tokens.append(word)
                word = '' # reset for next word
                continue
            word = word + self.text[i] # adding letters to words
            i = i + 1
        if word != '':
            self.rough_tokens.append(word) # appending the last word in a text
    
    def tokenize(self):
        self.tokenize_rough() # do the rough tokenization first
        self.dirty_tokens = list(self.rough_tokens) # for a shallow copy
        i = 0
        while i < len(self.dirty_tokens):
            word = self.dirty_tokens[i]    
            sub_tokens = self.split_token(word, self.puncs) # where to store subtokens found in a word
            
            #inserting sub_tokens into tokens
            if len(sub_tokens) > 0:
                del self.dirty_tokens[i] # delete the current token where the sub tokens will be substituted
                for item in sub_tokens:
                    self.dirty_tokens.insert(i, item)
                    i = i + 1
            else:
                i = i + 1
        # TOKEN NORMALIZATION
        self.clean_tokens() # clean tokens of punctuations
        self.expand_clitics() # clitics expansion before token lowering (for cases like I'd -> I would, i'd -> i'd)
        self.lower_tokens() # case lowering for tokens
        self.expand_clitics() # clitics expansion after token lowering (for cases like don't -> do not, Don't -> Don't)
        self.stem_tokens() # stemming tokens

# FUNCTIONS ON TOKEN EDITING
    def split_token(self, token, puncs):
        """
        Main function which splits a single rough token into subtokens. 
        For example the token "don't,be.:example@gmail.com" will be split as 
        a list of the following subtokens ["don't", ",", "be", ".", ",", "example@gmail.com"].
        """
        sub_tokens = [] # where to store subtokens found in a word
        # RULES
        if self.has_number(token): return sub_tokens # if token is number with ., return empty 
        if self.has_clitic(token): return self.split_by_char(token, '\'', self.puncs) # if token has a clitic split it 
        if self.has_abbreviation(token): return sub_tokens
        if self.has_email(token): return self.split_by_char(token, '@', self.email_puncs)
        substr = self.get_token_lex_substring(token)
        if len(substr) > 0: return self.split_by_string(token, substr, self.email_puncs)
        if self.has_web_address(token): return sub_tokens

        j = 0
        while j < len(token):
            if token[j] in puncs:
                if j > 0: sub_tokens.append(token[0:j]) # insert left over word only if its length is bigger than 0
                sub_tokens.append(token[j]) # insert punc into sub tokens
                token = token[j+1:] # the new word is the leftover
                j = -1 # reset counter to -1 (it will be zero in the next line)
            j = j + 1
        if len(token) > 0: sub_tokens.append(token) # add the last part of the word to sub_tokens if it is not empty
        return sub_tokens

    def split_by_char(self, token, character, puncs):
        """
        Split token based on desired character and list of punctuations. 
        If for example we have the string "example@gmail.com,done" and the desired 
        character as "@" and the punctuation list the list for emails (so, excluding ".")
        the string will be split as ["example@gmail.com", ",", "done"].
        """
        sub_tokens = []
        i = 0
        # Find the position of the first appearance of character
        while i < len(token):
            if i > 0 and i < (len(token) - 1) and token[i] == character:
                if self.is_letter(token[i-1]) and self.is_letter(token[i+1]):
                    break
            i = i + 1
        # done recursively for an arbitrary number of characters in token
        sub_tokens1 = self.split_token(token[0:i], puncs) # take the string up to the first appearance of character and split it
        sub_tokens2 = self.split_token(token[i+1:], puncs) # take the string after the first appearance of character and split it

        # sub_tokens1[0:-1] -> subtokens before the first appearance of character
        # sub_tokens1[-1] + character + sub_tokens2[0] -> the last element of subtokens_1 and 
            # first element of subtokens_2 concatenated together with the character in middle (e.g. example + @ + com)
        # sub_tokens2[1:] -> subtokens after the first appearance of character
        # e.g. [',', ':'] + [example + @ + gmail.com] + [':']
        return sub_tokens1[0:-1] + [sub_tokens1[-1] + character + sub_tokens2[0]] + sub_tokens2[1:]
    
    def split_by_string(self, token, string, puncs):
        """
        Split token depending on desired string and list of punctuations.
        If for example we have and abbreviation "Mr." inside a string like "hello,Mr.," 
        the string will be split as follows ["hello", ",", "Mr.", ","].
        """
        # Find the position of the first appearance of string
        pos = token.find(string)
        # done recursively for an arbitrary number of strings in token
        sub_tokens1 = self.split_token(token[0:pos], puncs) # tokenize again up to first appearance of string
        sub_tokens2 = self.split_token(token[pos+len(string):], puncs) # tokenize again after the first appearance of string
        return sub_tokens1 + [string] + sub_tokens2

# SENTENCE SPLITTING
    def sentence_split(self):
        """
        Splitting the input text into a list of sentences.
        """
        self.is_tokenized()
        # using the rough_tokens rebuilding the text again and splitting it into sentences based on rules
        sentence = ''
        i = 0
        while i < len(self.rough_tokens):
            if self.has_punctuation_at_end(self.rough_tokens[i]):
                if (len(self.get_token_lex_substring(self.rough_tokens[i])) > 0 or self.has_email(self.rough_tokens[i]) or
                    self.has_abbreviation(self.rough_tokens[i]) or self.has_number(self.rough_tokens[i])): # if token is in lexicon or is an email address
                    sentence = sentence + self.rough_tokens[i] + ' '
                    i = i + 1
                    continue
                sentence = sentence + self.rough_tokens[i] # adding the last token in sentence
                self.sentences.append(sentence) # adding sentence to sentences
                sentence = '' # restarting sentence 
            else:
                sentence = sentence + self.rough_tokens[i] + ' ' # concatenating tokens with whitespace
            i = i + 1
        return self.sentences

# VOCABULARY MAKING
    def make_vocabulary(self, token_type = "clean"):
        """
        makes a sorted vocabulary from the available tokens with clean tokens by default
        if token_type is set to "stemmed" then the vocabulary is made from stemmed tokens
        """
        self.is_tokenized()
        to_add = self.tokens
        if token_type == "stemmed":
            to_add = self.stemmed_tokens
        self.vocabulary = list(set(to_add))
        self.vocabulary.sort()

# WORD FREQUENCY GENERATION 
    def get_word_frequencies(self, token_type = "dirty"):
        """ 
        outputs word frequency dictionary (by default with dirty tokens)
        if token_type is "clean" then word frequency is done one clean tokens
        it token_type is "stemmed" then word frequency is done on stemmed tokens 
        """
        self.is_tokenized()
        to_add = self.dirty_tokens
        if token_type == "clean":
            to_add = self.tokens
        elif token_type == "stemmed":
            to_add = self.stemmed_tokens
        
        word_frequencies = {} # dictionary for word frequencies
        # adding tokens in a word frequency dictionary
        for token in to_add:
            if not(token in word_frequencies.keys()): 
                word_frequencies[token] = to_add.count(token)
        # sorting word frequency
        word_frequencies = dict(sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True))
        return word_frequencies

# STOP-WORD REMOVING
    def remove_stopwords(self, token_type = "stemmed"):
        """
        Function to remove stop-words from clean tokens.
        """
        self.is_tokenized()
        i = 0
        self.pruned_tokens = [] # if run two times, not to append to already generated list
        while i < len(self.tokens):
            if self.tokens[i] in stopword_lex:
                i += 1
                continue
            else:
                self.pruned_tokens.append(self.tokens[i])
            i += 1
        
# FUNCTIONS ON TOKEN NORMALIZATION
    def stem_tokens(self, token_type = "clean"):
        """
        Function to stem all the tokens using the Porter Stemmer. By default it stems
        clean tokens, but with the token_type set to "pruned" it will stem tokens for which
        stop-words were removed.
        """
        self.stemmed_tokens = []
        to_add = self.tokens
        if token_type == "pruned":
            self.remove_stopwords()
            to_add = self.pruned_tokens
        i = 0
        while i < len(to_add):
            stemmer = PorterStemmer()
            self.stemmed_tokens.append(stemmer.stem(to_add[i]))
            i = i + 1
        return self.stemmed_tokens

    def expand_clitics(self):
        """
        Function to expand clitics (e.g. we're -> we are)
        """
        self.is_tokenized()
        i = 0
        while i < len(self.tokens):
            # 
            if self.tokens[i] in contractions_lex.keys():
                expansion = contractions_lex[self.tokens[i]]
                self.tokens = self.tokens[0:i] + expansion + self.tokens[i+1:]
                i = i + len(expansion)
                continue
            # in the case a token ends with 's expand it as 'is' (e.g. "there's" -> "there is")
            elif len(self.tokens[i]) > 2 and self.tokens[i][-2:] == "'s":
                expansion = [self.tokens[i][0:-2], 'is']
                self.tokens = self.tokens[0:i] + expansion + self.tokens[i+1:]
                i = i + 2

            i = i + 1

    def lower_tokens(self):
        """
        Function to lower-case all tokens.
        """
        i = 0
        while i < len(self.tokens):
            self.tokens[i] = self.tokens[i].lower()
            i = i + 1

    def clean_tokens(self):
        """
        Function to clean dirty_tokens. A clean token is one that starts with a number or a letter.
        """
        self.tokens = []
        i = 0
        while i < len(self.dirty_tokens):
            character = self.dirty_tokens[i][0]
            # if the first character of a dirty token is a number or a letter, add it to clean tokens
            if self.is_letter(character) or self.is_number(character):
                self.tokens.append(self.dirty_tokens[i])
            i = i + 1
    
# PIPELINING THE CLASS
    # def pipeline(self):
    #     self.tokenize()
    #     self.sentence_split()
        

# HELPER FUNCTIONS
    def is_tokenized(self):
        """
        If text is not tokenized, tokenize it (used for sentence splitting and vocabulary making) as
        it may be a prerequisite for an operation.
        """
        if len(self.tokens) == 0:
            self.tokenize()

    def is_letter(self, c):
        """
        Checks if a character is a letter.
        """
        return self.is_lower_case(c) or self.is_upper_case(c)
    
    def is_lower_case(self, c):
        """
        Checks if a character is a lower-case letter.
        """
        return c >= 'a' and c <= 'z'

    def is_upper_case(self, c):
        """
        Checks if a character is an upper-case letter
        """
        return c >= 'A' and c <= 'Z'

    # if token has an entry from lexicon as substring return it
    def get_token_lex_substring(self, token):
        for l in abbreviations_lex:
            if l in token:
                return l
        return ''

    # if a token has a punctuation 
    def has_punctuation(self, token):
        puncs = ['.', '!', '?']
        for pun in puncs:
            if pun in token:
                return True
        return False
    
    # if the last character of a token is a punctuation sign
    def has_punctuation_at_end(self, token):
        puncs = ['.', '!', '?']
        if len(token) == 0:
            return 
        return token[-1] in puncs

    def is_number(self, c):
        """
        Checks if a character is a number.
        """
        return c >= '0' and c <= '9'

    def has_number(self, token):
        """
        Checks if a token has a "." or "," character followed or preceded by a number.
        """
        i = 0
        while i < len(token):
            if token[i] == '.' or token[i] == ',':
                if i > 0 and i < (len(token) - 1) and (self.is_number(token[i-1]) or self.is_number(token[i+1])):
                    return True
            i = i + 1
        return False

    #if the end of the token is an abbreviation for a name i.e. in the form "D.K."
    def has_abbreviation(self, token): 
        return len(token) > 1 and token[-1] == '.' and self.is_upper_case(token[-2])
    
    def has_email (self, token):
        """
        Checks if a token has "@" inside of it (i.e. has an email address)
        """
        return '@' in token

    def has_web_address (self, token):
        """
        Checks if a token has "http" or "www" as substring.
        """
        return 'http' in token or 'www' in token

    def has_clitic (self, token):
        """
        Checks if a token has a clitic as a substring.
        """
        i = 0
        while i < len(token):
            if i > 0 and i < (len(token) - 1) and token[i] == '\'':
                if self.is_letter(token[i-1]) and self.is_letter(token[i+1]):
                    return True
            i = i + 1
        return False

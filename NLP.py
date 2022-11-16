from lexicons import * # getting the lexicons for contractions and abbreviations

class NLP:
    rough_tokens = []
    tokens = []
    sentences = []
    text = []
    vocabulary = []
    word_frequency = {}
    stems = []
    puncs = ['.', ',', '!', '?', '(', ')', ':', ';', '"', '"', '\'']
    email_puncs = [',', '!', '?', '(', ')', ':', ';', '"', '"', '\'']
    web_puncs = [',', '!', '?', '(', ')', ';', '"', '"']

    def __init__(self, text):
        self.reset()
        self.text = text
    
    def reset(self):
        self.rough_tokens = []
        self.tokens = []
        self.sentences = []
        self.text = []
        self.vocabulary = []
        self.word_frequency = {}
        self.stems = []

    def tokenize_rough(self):
        splitters = [' ', '\n'] # chars used for splitting words
        word = '' # where to store a single word
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
        self.rough_tokens.append(word) # appending the last word in a text
    
    def tokenize(self):
        self.tokenize_rough() # do the rough tokenization first
        self.tokens = list(self.rough_tokens) # for a shallow copy
        i = 0
        while i < len(self.tokens):
            word = self.tokens[i]    
            sub_tokens = self.split_token(word, self.puncs) # where to store subtokens found in a word
            
            #inserting sub_tokens into tokens
            if len(sub_tokens) > 0:
                del self.tokens[i] # delete the current token where the sub tokens will be substituted
                for item in sub_tokens:
                    self.tokens.insert(i, item)
                    i = i + 1
            else:
                i = i + 1

    def sentence_split(self):
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

    # function to split a rough token
    def split_token(self, token, puncs):
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

    # split token based on desired character
    def split_by_char(self, token, character, puncs):
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
    
    # split token depending on string (e.g. "hello,Mr.," = ["hello", ",", "Mr.", ","])
    def split_by_string(self, token, string, puncs):
        # Find the position of the first appearance of string
        pos = token.find(string)
        # done recursively for an arbitrary number of strings in token
        sub_tokens1 = self.split_token(token[0:pos], puncs) # tokenize again up to first appearance of string
        sub_tokens2 = self.split_token(token[pos+len(string):], puncs) # tokenize again after the first appearance of string
        return sub_tokens1 + [string] + sub_tokens2

    def make_vocabulary(self):
        self.is_tokenized()
        self.expand_clitics()

        # adding tokens in a word frequency dictionary
        for token in self.tokens:
            if not(token in self.word_frequency.keys()): 
                self.word_frequency[token] = self.tokens.count(token)
        # sorting word frequency
        self.word_frequency = dict(sorted(self.word_frequency.items(), key=lambda x: x[1], reverse=True))
        # make vocabulary
        self.vocabulary = list(self.word_frequency.keys())
        self.vocabulary.sort()
    
    # cleans vocabulary and word frequency of noisy tokens (e.g. removes '?', '..!', '...' )
    def clean_vocabulary(self):
        # in the case a vocabulary was not created
        if len(self.vocabulary) == 0:
            self.make_vocabulary()
        i = 0
        removed_words = []
        while i < len(self.vocabulary):
            character = self.vocabulary[i][0]
            # if the first character of a token is a number or letter keep it in the dictionary, otherwise remove it
            if self.is_letter(character) or self.is_number(character):
                i = i + 1
                continue
            else:
                removed_words.append(self.vocabulary[i])
                self.vocabulary.remove(self.vocabulary[i])
        # clean word frequency dictionary
        for word in removed_words:
            del self.word_frequency[word]

    def normalize(self):
        print("to come")

    def expand_clitics(self):
        self.is_tokenized()
        i = 0
        while i < len(self.tokens):
            # 
            if self.tokens[i] in contractions_lex.keys():
                expansion = contractions_lex[self.tokens[i]]
                self.tokens = self.tokens[0:i] + expansion + self.tokens[i+1:]
                i = i + len(expansion)
            # in the case a token ends with 's expand it as 'is' (e.g. "there's" -> "there is")
            elif len(self.tokens[i]) > 2 and self.tokens[i][-2:] == "'s":
                expansion = [self.tokens[i][0:-2], 'is']
                self.tokens = self.tokens[0:i] + expansion + self.tokens[i+1:]
                i = i + 2

            i = i + 1

    def pipeline(self):
        self.tokenize()
        self.sentence_split()
        self.expand_clitics()
        self.clean_vocabulary()

# HELPER FUNCTIONS
    # if text is not tokenized, tokenize it (used for sentence splitting and vocabulary making)
    def is_tokenized(self):
        if len(self.tokens) == 0:
            self.tokenize()

    # if a character is a letter
    def is_letter(self, c):
        return self.is_lower_case(c) or self.is_upper_case(c)
    
    # if a character is lower case
    def is_lower_case(self, c):
        return c >= 'a' and c <= 'z'

    # if a character is upper case
    def is_upper_case(self, c):
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
        return token[-1] in puncs

    # if a character is a number
    def is_number(self, c):
        return c >= '0' and c <= '9'

    #if a token has a legit number inside like 4,3 or 4.56M
    def has_number(self, token):
        i = 0
        while i < len(token):
            if token[i] == '.' or token[i] == ',':
                if i > 0 and i < (len(token) - 1) and self.is_number(token[i-1]) and self.is_number(token[i+1]):
                    return True
            i = i + 1
        return False

    #if the end of the token is an abbreviation for a name i.e. in the form "D.K."
    def has_abbreviation(self, token): 
        return len(token) > 1 and token[-1] == '.' and self.is_upper_case(token[-2])
    
    #if token has @ (i.e. has email address) 
    def has_email (self, token):
        return '@' in token

    # if token has domain name
    def has_web_address (self, token):
        return 'http' in token or 'www' in token

    # if token has clitic
    def has_clitic (self, token):
        i = 0
        while i < len(token):
            if i > 0 and i < (len(token) - 1) and token[i] == '\'':
                if self.is_letter(token[i-1]) and self.is_letter(token[i+1]):
                    return True
            i = i + 1
        return False

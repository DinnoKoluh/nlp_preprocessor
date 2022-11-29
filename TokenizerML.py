from AbstractNLP import *
from sklearn.naive_bayes import MultinomialNB

class TokenizerML(AbstractNLP):
    """
    Class for text tokenization using the Naive Bayes model.
    """
    def __init__(self):
        pass

# FEATURE/CLASS COMPILATION
    def get_features(self, sample, index):
        """
        Function for feature compilation. To see the composition of sample list
        look at get_samples function.
        Features:
        F0: Is character a letter?
        F1: Is character a number?
        F2: Is character a whitespace?
        F3: Is character between two alphanumeric values?
        F4: Is character a punctuation sign?
        F5: Is character next to a number?
        F6: Is character @?
        F7: Is character a punctuation sign between two alphanumeric values?

        """
        features = [None]*8 # features of a sample
        char = sample[index] # the character we try to find the features for 
        # F0
        features[0] = 0
        if self.is_letter(char):
            features[0] = 1
        # F1
        features[1] = 0
        if self.is_number(char):
            features[1] = 1
        # F2
        features[2] = 0
        if char == " ":
            features[2] = 1
        # F3
        features[3] = 0
        if index > 0 and index < len(sample) - 1 and self.is_alphanumeric(sample[index-1]) and self.is_alphanumeric(sample[index+1]):
            features[3] = 1
        # F4
        features[4] = 0
        if char in self.puncs:
            features[4] = 1
        # F5
        features[5] = 0
        if index > 0 and index < len(sample) - 1 and self.is_number(sample[index-1]):
            features[5] = 1
        # F6
        features[6] = 0
        if char == '@':
            features[6] = 1
        # F7
        features[7] = 0
        if features[3] == 1 and features[4] == 1:
            features[7] = 1
        return features


    def make_dataset(self, txt):
        """
        Function used to compile the actual dataset. The dataset consists of features 
        defined in the get_features function and targets which are binary class labels 
        which tell us if the chosen character should be place of the split.
        We find that out by the rule based tokenizer in the super class.
        """
        self.standardize_text(txt)
        sample = self.stand_text
        features = []
        targets = []
        # Supervised dataset
        i = 0
        while i < len(sample):
            features.append(self.get_features(sample, i))
            if sample[i] == " ":
                targets.append(1)
                i = i + 1
                continue
            # setting up a moving window
            wsize = 12
            left = i - wsize
            right = i + wsize
            if left < 0: left = 0 # boundary condition for left side of the window
            if right > len(sample): right = len(sample) # boundary condition for the right side of the window
            self.text = sample[left:right] # taking a sample from the text
            self.tokenize() # splitting token bounded by the moving window
            if sample[i] in self.dirty_tokens: targets.append(1) # if the character is a dirty token then it should be a splitter
            else: targets.append(0)
            i = i + 1
        # save training dataset as .csv file
        header = ['F0', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'Class']
        self.save_dataset('data\dataset_tokenization.csv', features, targets, header) 
        return features, targets

# TOKENIZATION
    def tokenize_ml(self, txt):
        """
        Main function for tokenization using NaiveBayes.
        Training dataset required for fitting.
        """
        #*note: I did not have the time to build the classifier from scratch, so I used the sklearn one).
        X, y = self.load_dataset('data\dataset_tokenization.csv') # loading training data
        gnb = MultinomialNB()
        self.standardize_text(txt)
        i = 0
        features = []
        while i < len(self.stand_text):
            features.append(self.get_features(self.stand_text, i))
            i = i + 1
        targets = gnb.fit(X, y).predict(features) # fitting
        probabilities = gnb.predict_proba(features)
        tokens = []
        current_token = ""
        # building token list from the obtained targets
        for target, char in zip(targets, self.stand_text):
            if target == 1:
                if current_token != "": tokens.append(current_token)
                if char != " ": tokens.append(char)
                current_token = ""
            else:
                current_token = current_token + char
        tokens.append(current_token)
        return tokens, features, targets, probabilities


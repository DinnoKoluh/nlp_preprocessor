from AbstractNLP import *
from sklearn.linear_model import LogisticRegression

class SentenceSplitterML(AbstractNLP):
    """
    Class for sentence splitting using Machine Learning.
    """
    punctuations = ['.', '!', '?']
    
    def __init__(self):
        pass

# FEATURE/CLASS COMPILATION
    def get_features(self, sample_list):
        """
        Function for feature compilation. To see the composition of sample list
        look at get_samples function.
        Features:
        F0: Is punctuation a period?
        F1: Is previous character lower_case?
        F2: Is previous character upper_case?
        F3: Is previous character number?
        F4: Is next character letter?
        F5: Is next character number?
        F6: Is next character whitespace?
        F7: Is previous token an abbreviation?
        """
        features = [None]*8 # features of a sample
        sample = sample_list[0] # sample string 
        punc = sample_list[1] # punctuation of current sample
        index = sample_list[2] # index of current punctuation
        # F0
        features[0] = 0
        if punc == '.':
            features[0] = 1
        # F1
        features[1] = 0
        if index > 0 and self.is_lower_case(sample[index-1]):
            features[1] = 1
        # F2
        features[2] = 0
        if index > 0 and self.is_upper_case(sample[index-1]):
            features[2] = 1
        # F3
        features[3] = 0
        if index > 0 and self.is_number(sample[index-1]):
            features[3] = 1
        # F4
        features[4] = 0
        if index < len(sample)-1 and self.is_letter(sample[index+1]):
            features[4] = 1
        # F5
        features[5] = 0
        if index < len(sample)-1 and self.is_number(sample[index+1]):
            features[5] = 1
        # F6
        features[6] = 0
        if index < len(sample)-1 and sample[index+1] == " ":
            features[6] = 1
        # F7
        features[7] = 0
        if sample[0:index+1] in abbreviations_lex or sample[1:index+1] in abbreviations_lex: # case " Mr." and "Mr. "
            features[7] = 1
        return features

    def get_samples(self, txt):
        """
        Function used to get samples from a text. A sample in this case is a list
        where the first entry is the string s.t. it contains a punctuation sign and 
        all the characters left and right from it until a whitespace or end of text is reached 
        (e.g. "Hello world. Am I a human?" -> [" world. ", " human?"]).
        The second entry is the punctuation sign that occurred, the third entry is the local 
        index value of the punctuation sign and the fourth entry is the global index value 
        of the punctuation.
        e.g. "Mr. Hello world. Am I a human?"
        ['Mr. ', '.', 2, 2]
        [' world. ', '.', 6, 15]
        [' human?', '?', 6, 29]
        """
        self.standardize_text(txt)
        i = 0
        samples = []
        while i < len(self.stand_text):
            if self.stand_text[i] in self.punctuations:
                start_index = i # start index of sample string
                final_index = i # end index of sample string
                while start_index > 0 and self.stand_text[start_index] != " ":
                    start_index -= 1
                while final_index < len(self.stand_text) and self.stand_text[final_index] != " ":
                    final_index += 1
                # appending string, punctuation, local index, global index
                samples.append([self.stand_text[start_index:final_index+1], self.stand_text[i], i-start_index, i])
            i = i + 1    
        return samples
    
    def make_dataset(self, txt):
        """
        Function used to compile the actual dataset. The dataset consists of features 
        defined in the get_features function and targets which are binary class labels 
        which tell us if the punctuation inside the sample should be a sentence splitter.
        We find that out by the rule based sentence splitter in the super class.
        """
        samples = self.get_samples(txt)
        features = []
        targets = []
        # Supervised dataset
        self.sentence_split() # rule-based sentence splitting
        target_text = "" # Target text which we will get from the rule based sentence splitting

        for sentence in self.sentences:
            # adding new line for a new sentence s.t. the target text and the standardized input text have the same length
            target_text = target_text + sentence + "\n" 
        target_text = target_text[0:-1] # removing the last new line

        for sample in samples:
            features.append(self.get_features(sample)) # appending features
            # if the character after the index of the punctuation sign is "\n", it means that that punctuation sign is a sentence splitter
            # so assign 1 as its class, otherwise 0
            if sample[3]+1 < len(target_text) and target_text[sample[3]+1] == "\n":
                targets.append(1)
            else:
                targets.append(0)  
        # save training dataset as .csv file
        header = ['F0', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'Class']
        self.save_dataset('data\dataset_sentences.csv', features, targets, header)  

# SENTENCE SPLITTING
    def sentence_split_ml(self, txt):
        """
        Main function for sentence splitting using Logistical Regression.
        Training dataset required for fitting.
        """
        X, y = self.load_dataset('data\dataset_sentences.csv') # loading training data
        clf = LogisticRegression(random_state=0).fit(X, y)
        samples = self.get_samples(txt) # samples of the input text
        features = [] # features of the input text
        for sample in samples:
            features.append(self.get_features(sample))
        targets = clf.predict(features) # predicting targets for input text
        probabilities = clf.predict_proba(features) # predicting target probabilities for input text
        print(targets)
        print(probabilities)

        sentences = []
        cursor = 0 # the position of the beginning of a sentence
        for sample, target in zip(samples, targets):
            # if the target is '1' split sentence from the standardized text.
            # it is split from the position of the cursor until the punctuation index which 
            # was kept inside the sample list at position 3
            if target == 1:
                sentences.append(self.stand_text[cursor:sample[3]+1])
                cursor = sample[3] + 1 # move the cursor to the beginning of the next sentence
        # in the case the the text only contains one sentence
        if len(sentences) == 0:
            sentences.append(self.stand_text)
        # adding the last sentence in the cases the cursor is not at the end of the text
        if cursor != len(self.stand_text):
            sentences.append(self.stand_text[cursor:])
        # removing whitespace from beginning of sentences
        for i in range(0, len(sentences)):
            if sentences[i][0] == " ":
                sentences[i] = sentences[i][1:]
        return sentences
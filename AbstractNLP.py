from NLP import *
import csv

class AbstractNLP(NLP):
    stand_text = "" # standardized text (concatenation of rough tokens)

    def load_dataset(self, name):
        """
        Function for loading the training set.
        """
        reader = csv.reader(open(name, "r"))
        output = list(reader)
        output = output[1:] # disregard the header
        X = [] # features
        y = [] # targets
        for out in output:
            X.append(out[0:-1])
            y.append(out[-1])
        return X, y

    def save_dataset(self, name, features, targets, header):
        with open(name, 'w', newline='') as f:
            write = csv.writer(f)
            write.writerow(header) # header
            to_write = [] # the matrix that is going to be written in the .csv file, features + targets
            i = 0
            while i < len(features):
                to_write.append(features[i]+[targets[i]])
                i = i + 1
            write.writerows(to_write) 

    def standardize_text(self, txt):
        """
        Function used to standardize a text which means that all occurrences
        of newlines and multiple whitespaces will be deleted. This is done by
        just concatenating rough tokens with a whitespace in between.
        """
        self.stand_text = ""
        self.text = txt
        self.tokenize_rough()
        for token in self.rough_tokens:
            self.stand_text = self.stand_text + token + " "
        self.stand_text = self.stand_text[0:-1] # eliminate the last " " from the for loop
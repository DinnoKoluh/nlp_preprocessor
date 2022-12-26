# Penn Treebank tagset: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
rules = {
    "S": [["NP", "VP"], ["Aux", "NP", "VP"]],
    "NP": [["Det", "Nominal"], ["Nominal"], ["Pronoun"], ["Pronoun", "Nominal"], ["Det", "Adjective"], ["Adjective", "Noun"]],
    "VP": [["Verb"], ["Verb", "NP"], ["Verb", "Noun"], ["VP", "PP"], ["Verb", "NP", "PP"], ["Verb", "PP"]],
    "PP": [["Preposition", "NP"]],
    "Nominal": [["Nominal", "Noun"], ["Nominal", "PP"], ["Noun"], ["Adjective", "Nominal"]],
    "Pronoun": [["PRP"], ["PRP$"]],
    "Det": [["DT"]],
    "Preposition": [["IN"]],
    "Noun": [["NN"], ["NNS"], ["NNP"],["NNPS"]], # different types of nouns
    "Verb": [["VB"], ["VBD"], ["VBG"], ["VBN"], ["VBP"], ["VBZ"]],
    "Adjective": [["JJ"], ["JJR"], ["JJS"]]
}

# lexical rules are directly obtained from the PoS of the nltk library



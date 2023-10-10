This repository contains a system for the preprocessing of the English language. Namely, the described toolkit consists of a 
rule-based and machine-learning-based tokenizer and sentence splitter respectively, normalizer, stemmer, a system for stopword elimination, 
vocabulary generation and word frequency generation. These systems take into account ambiguous punctuations, URLs,
hashtags, e-mails, MWEs, clitics expansion and tokens with numbers.

The other part of the repository contains a system which takes as an input a user-defined context-free grammar (CFG)
and parses a sentence using the implementation of the CKY parser for English. The goal of the
parser is to be able to parse declarative, imperative and question sentences using a suitable CFG.
It is assumed that we have the SVO word order in the English language.

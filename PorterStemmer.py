# reference: https://iq.opengenus.org/porter-stemmer/

class PorterStemmer:
    def __init__(self):
        pass
    
    # helper functions for consonants, the case for "y" must be regarded 
    def is_cons1(self, let):
        if let == 'a' or let == 'e' or let == 'i' or let == 'o' or let == 'u':
            return False
        return True
    
    # if a letter is a consonant
    def is_consonant(self, token, i):
        if self.is_cons1(token[i]): # if the letter is "y" and the letter before is a consonant, then "y" is a vowel in that case
            if token[i] == 'y' and i > 0 and self.is_cons1(token[i-1]):
                return False
            return True
        return False
    
    # if letter is a vowel
    def is_vowel(self, token, i):
        return not(self.is_consonant(token, i))

    # if token contains a vowel (not considering "y")
    def has_vowel(self, token):
        for l in token:
            if not self.is_cons1(l):
                return True
        return False

    # checks if a token ends with a double consonant (e.g. "-bb", "-cc")
    def endswith_double_consonant(self, token):
        if len(token) >= 2:
            if self.is_consonant(token, -1) and self.is_consonant(token, -2) and token[-1] == token[-2]:
                return True
            return False
        return False

    # checks if token ends with let (e.g. check if library end with y)
    #def endswith_letter(self, token, let):

    # return true of the last three letters of a token are in the form CVC and the last letter is not 'w', 'x' or 'y'
    def endswith_cvc(self, token):
        if len(token) >= 3:
            if self.is_consonant(token, -3) and self.is_vowel(token, -2) and self.is_consonant(token, -1):
                if token[-1] != 'w' and token[-1] != 'x' and token[-1] != 'y':
                    return True
        return False

    # getting the porter form of a token (e.g. )
    def get_form(self, token):
        form = ''
        i = 0
        while i < len(token):
            if self.is_consonant(token, i): 
                form = form + 'C'
                i = i + 1
                while (i < len(token) and self.is_consonant(token, i)):
                    i = i + 1
            else:
                form = form + 'V'
                i = i + 1
                while (i < len(token) and self.is_vowel(token, i)):
                    i = i + 1
        return form
    
    def get_measure(self, token):
        form = self.get_form(token)
        return form.count('VC')

    # replace the ending of a token with a new ending
    def replace_ending(self, token, ending, new_ending):
        index = token.rfind(ending)
        base = token[0:index]
        return base + new_ending

    # same as replace(), but if the base of the token is a measure = 0, then it returns the original token
    def replace_ending_m0(self, token, ending, new_ending):
        index = token.rfind(ending)
        base = token[0:index]
        if self.get_measure(base) > 0:
            return base + new_ending
        return token

    # same as replace(), but if the base of the token is a measure < 2, then it returns the original token
    def replace_ending_m1(self, token, ending, new_ending):
        index = token.rfind(ending)
        base = token[0:index]
        if self.get_measure(base) > 1:
            return base + new_ending
        return token

    # STEPS for the Porter Algorithm / check the website at the heading of the file for information and examples
    def step1a(self, token):
        if token.endswith('sses'):
            token = self.replace_ending(token, 'sses', 'ss')
        elif token.endswith('ies'):
            token = self.replace_ending(token, 'ies', 'i')
        elif token.endswith('ss'):
            token = self.replace_ending(token, 'ss', 'ss')
        elif token.endswith('s') and len(token[0:-1]) > 1:
            token = self.replace_ending(token, 's', '')
        else:
            pass
        return token
    
    def step1b(self, token):
        flag = False
        if token.endswith('eed'):
            index = token.rfind('eed')
            base = token[:index]
            if self.get_measure(base) > 0:
                token = base
                token += 'ee'
        elif token.endswith('ed'):
            index = token.rfind('ed')
            base = token[:index]
            if self.has_vowel(base):
                token = base
                flag = True
        elif token.endswith('ing'):
            index = token.rfind('ing')
            base = token[:index]
            if self.has_vowel(base):
                token = base
                flag = True
        if flag:
            if token.endswith('at') or token.endswith('bl') or token.endswith('iz'):
                token += 'e'
            elif self.endswith_double_consonant(token) and not token.endswith('l') and not token.endswith('s') and not token.endswith('z'):
                token = token[:-1]
            elif self.get_measure(token) == 1 and self.endswith_cvc(token):
                token += 'e'
            else:
                pass
        else:
            pass
        return token

    def step1c(self, token):        
        if token.endswith('y'):
            index = token.rfind('y')
            base = token[:index]
            if self.has_vowel(base):
                token = base
                token += 'i'
        return token

    def step2(self, token):
        if token.endswith('ational'):
            token = self.replace_ending_m0(token, 'ational', 'ate')
        elif token.endswith('tional'):
            token = self.replace_ending_m0(token, 'tional', 'tion')
        elif token.endswith('enci'):
            token = self.replace_ending_m0(token, 'enci', 'ence')
        elif token.endswith('anci'):
            token = self.replace_ending_m0(token, 'anci', 'ance')
        elif token.endswith('izer'):
            token = self.replace_ending_m0(token, 'izer', 'ize')
        elif token.endswith('abli'):
            token = self.replace_ending_m0(token, 'abli', 'able')
        elif token.endswith('alli'):
            token = self.replace_ending_m0(token, 'alli', 'al')
        elif token.endswith('entli'):
            token = self.replace_ending_m0(token, 'entli', 'ent')
        elif token.endswith('eli'):
            token = self.replace_ending_m0(token, 'eli', 'e')
        elif token.endswith('ousli'):
            token = self.replace_ending_m0(token, 'ousli', 'ous')
        elif token.endswith('ization'):
            token = self.replace_ending_m0(token, 'ization', 'ize')
        elif token.endswith('ation'):
            token = self.replace_ending_m0(token, 'ation', 'ate')
        elif token.endswith('ator'):
            token = self.replace_ending_m0(token, 'ator', 'ate')
        elif token.endswith('alism'):
            token = self.replace_ending_m0(token, 'alism', 'al')
        elif token.endswith('iveness'):
            token = self.replace_ending_m0(token, 'iveness', 'ive')
        elif token.endswith('fulness'):
            token = self.replace_ending_m0(token, 'fulness', 'ful')
        elif token.endswith('ousness'):
            token = self.replace_ending_m0(token, 'ousness', 'ous')
        elif token.endswith('aliti'):
            token = self.replace_ending_m0(token, 'aliti', 'al')
        elif token.endswith('iviti'):
            token = self.replace_ending_m0(token, 'iviti', 'ive')
        elif token.endswith('biliti'):
            token = self.replace_ending_m0(token, 'biliti', 'ble')
        return token
    
    def step3(self, token):
        if token.endswith('icate'):
            token = self.replace_ending_m0(token, 'icate', 'ic')
        elif token.endswith('ative'):
            token = self.replace_ending_m0(token, 'ative', '')
        elif token.endswith('alize'):
            token = self.replace_ending_m0(token, 'alize', 'al')
        elif token.endswith('iciti'):
            token = self.replace_ending_m0(token, 'iciti', 'ic')
        elif token.endswith('ical'):
            token = self.replace_ending_m0(token, 'ical', 'ic')
        elif token.endswith('ful'):
            token = self.replace_ending_m0(token, 'ful', '')
        elif token.endswith('ness'):
            token = self.replace_ending_m0(token, 'ness', '')
        return token

    def step4(self, token):
        if token.endswith('al'):
            token = self.replace_ending_m1(token, 'al', '')
        elif token.endswith('ance'):
            token = self.replace_ending_m1(token, 'ance', '')
        elif token.endswith('ence'):
            token = self.replace_ending_m1(token, 'ence', '')
        elif token.endswith('er'):
            token = self.replace_ending_m1(token, 'er', '')
        elif token.endswith('ic'):
            token = self.replace_ending_m1(token, 'ic', '')
        elif token.endswith('able'):
            token = self.replace_ending_m1(token, 'able', '')
        elif token.endswith('ible'):
            token = self.replace_ending_m1(token, 'ible', '')
        elif token.endswith('ant'):
            token = self.replace_ending_m1(token, 'ant', '')
        elif token.endswith('ement'):
            token = self.replace_ending_m1(token, 'ement', '')
        elif token.endswith('ment'):
            token = self.replace_ending_m1(token, 'ment', '')
        elif token.endswith('ent'):
            token = self.replace_ending_m1(token, 'ent', '')
        elif token.endswith('ou'):
            token = self.replace_ending_m1(token, 'ou', '')
        elif token.endswith('ism'):
            token = self.replace_ending_m1(token, 'ism', '')
        elif token.endswith('ate'):
            token = self.replace_ending_m1(token, 'ate', '')
        elif token.endswith('iti'):
            token = self.replace_ending_m1(token, 'iti', '')
        elif token.endswith('ous'):
            token = self.replace_ending_m1(token, 'ous', '')
        elif token.endswith('ive'):
            token = self.replace_ending_m1(token, 'ive', '')
        elif token.endswith('ize'):
            token = self.replace_ending_m1(token, 'ize', '')
        elif token.endswith('ion'):
            index = token.rfind('ion')
            base = token[0:index]
            if self.get_measure(base) > 1 and (base.endswith('s') or base.endswith('t')):
                token = base
            token = self.replace_ending_m1(token, '', '')
        return token

    def step5a(self, token):
        if token.endswith('e'):
            base = token[:-1]
            if self.get_measure(base) > 1:
                token = base
            elif self.get_measure(base) == 1 and not self.endswith_cvc(base):
                token = base
        return token

    def step5b(self, token):
        if self.get_measure(token) > 1 and self.endswith_double_consonant(token) and token.endswith('l'):
            token = token[:-1]
        return token

    # combing all the steps into a pipeline to stem a token
    def stem(self, token):
        token = self.step1a(token)
        token = self.step1b(token)
        token = self.step1c(token)
        token = self.step2(token)
        token = self.step3(token)
        token = self.step4(token)
        token = self.step5a(token)
        token = self.step5b(token)
        return token  
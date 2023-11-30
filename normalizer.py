import re
from collections import Counter

# This code is written based on Peter Norvig's spell corrector: https://norvig.com/spell-correct.html
def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcçdefgğhijklmnoöpqrsştuüvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


class TurkishNormalizer:
    def __init__(self, corpus_path, lexicon_path, ngram=1):
        self.corpus_path = corpus_path
        self.lexicon_path = lexicon_path
        self.ngram = ngram
        
        self.__build_lang_model__()
        
        
    def __build_lang_model__(self):
        with open(self.corpus_path, encoding="utf8") as file:
            corpus = file.read()
            
        # removing punctuations
        corpus = re.findall("\w+|<s>|<\\\s>", corpus)
        
        # preparing ngrams
        ngrams = []

        for i in range(self.ngram):
            ngrams.append(corpus[i:])
    
        # preparing the language model
        self.lang_models =  [Counter(ngrams[0])]
        self.lang_models += [Counter(zip(*ngrams[:i])) for i in range(2, self.ngram+1)]
    
        
    def normalize(self, word):
        E1 = list(edits1(word))
        E2 = [e2 for e in E1 for e2 in edits1(e)]
       
        # searching possible candidates in the language model
        cands = {var: self.lang_models[0][var] for var in E1 or E2}
        cands = {c: cands[c] for c in cands if cands[c] > 0}
        cands = sorted(cands.items(), key=lambda i:i[1], reverse=True)
        
        if len(cands) > 0:
            return cands[0][0] # most likelihood
        else:
            return word
    
    
    def normalize_from_ngram(self, word, context):
        E1 = list(edits1(word))
        E2 = [e2 for e in E1 for e2 in edits1(e)]
        
        # generating ngram from the given context
        E1 = [[*context, e1] for e1 in E1]
        E2 = [[*context, e2] for e2 in E2]
        
        # searching possible candidates in the language model
        cands = {tuple(var): self.lang_models[2].get(tuple(var)) for var in E1 or E2}
        cands = {c: cands[c] for c in cands if cands[c] is not None}
        cands = sorted(cands.items(), key=lambda i: i[1], reverse=True)
        
        if len(cands) > 0:
            return cands[0][0][-1] # most likelihood
        else:
            return word
    
    
    def normalize_sentence(self, sentence):
        sentence  = re.findall("\w+", sentence)
        norm_sent = []
        
        for i, word in enumerate(sentence):
            if i < self.ngram:
                norm_sent.append(self.normalize(word))
            else:
                for n in range(self.ngram-1, 0, -1):
                    candidate = self.normalize_from_ngram(sentence[i], norm_sent[i-n:i])
                    
                    # candidate is found in higher ngrams
                    if candidate != sentence[i]:
                        break

                norm_sent.append(candidate)                    
                        
        return " ".join(norm_sent)
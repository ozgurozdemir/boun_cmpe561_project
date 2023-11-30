import re

class TurkishStemmer:
    def __init__(self, lexicon_path, grammar_path, use_derivational=True):
        """
            Main Class for appyling Turkish Stemmer
            
            lexicon_path(str): path for the lexicon file
            grammar_path(str): path for the grammar file
            use_derivational(bool): including derivational suffixes in the stemming or not
            
            ---
            stem(str) -> str: function for stemming single token
            stem_sentence(str) -> str: function for stemming all tokens in the given sentence
        """
        self.lexicon_path = lexicon_path
        self.grammar_path = grammar_path
        self.use_derivational = use_derivational
        
        self.grammar = self.__read_grammar__()
            
        with open(self.lexicon_path, encoding="utf8") as file:
            self.lexicon = file.read().split()
    
    
    def __read_grammar__(self):
        def __applyRulesRegex__(self, rules):
            rules = [re.sub("\(y\)", "y*", r) for r in rules] 
            rules = [re.sub("-", "", r) for r in rules]

            return rules

        with open(self.grammar_path, encoding="utf8") as file:
            self.grammar = json.load(file)
        
        # reading suffixes
        _suffixes = []
        for rule in grammar:
            # deciding to include derivational suffixes
            if rule is "Derivational" 
                if self.use_derivational:
                    _suffixes += grammar[rule]
            else:
                _suffixes += grammar[rule]
            
        
        # removing dash sign
        _suffixes = [s.replace("-", "") for s in _suffixes]
        
        # sorting suffixes with respect to their length
        self.max_suffix_len = max([len(s) for s in _suffixes])

        suffixes = {l: [] for l in range(1, self.max_suffix_len + 1)}
        
        for suffix in _sufxs:
            suffixes[len(suffix)].append(suffix) 
            
        # preparing suffix regexes
        for sfx in suffixes:
            suffixes[sfx] = f"\w*({'|'.join(suffixes[sfx])})"
        
        return suffixes
        
    
    def stem(self, token: str) -> str:
        # token is found in the lexicon
        if token in self.lexicon:
            return token 

        for suffix_len in range(self.max_suffix_len, 1, -1):
            
            # matching suffix rule is found
            if re.match(self.grammar[suffix_len], token):
                return self.stem(token[:-suffix_len]) 

        return token        
    
    
    def stem_sentence(self, sentence:str) -> str:
        sentence  = sentence.split(" ")
        stem_sent = [self.stem(word) for word in sentence]
        
        return " ".join(stem_sent)
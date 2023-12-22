import re
import json
from collections import Counter

class TurkishStemmer:
    def __init__(self, lexicon_path, suffixes_path, corpus_path, include_categories=False, use_derivational=True):
        """
            Main Class for appyling Turkish Stemmer

            lexicon_path(str): path for the lexicon file
            suffixes_path(str): path for the suffixes file
            corpus_path(str): path for the corpus file
            use_derivational(bool): including derivational suffixes in the stemming or not

            ---
            stem(str) -> str: function for stemming single token
            stem_sentence(str) -> str: function for stemming all tokens in the given sentence
        """
        self.lexicon_path = lexicon_path
        self.suffixes_path = suffixes_path
        self.corpus_path = corpus_path
        self.include_categories = include_categories
        self.use_derivational = use_derivational

        self.suffixes = self.__read_suffixes__()

        with open(self.lexicon_path, encoding="utf8") as file:
            self.lexicon = file.read().split()

        with open(self.corpus_path, encoding="utf8") as file:
            corpus = file.read()

        corpus = re.findall("\w+|<s>|<\\\s>", corpus)
        self.corpus = Counter(corpus)


    def __read_suffixes__(self) -> list[(str, str)]:
        def __applyRulesRegex__(self, rules):
            rules = [re.sub("\(y\)", "y*", r) for r in rules]
            rules = [re.sub("-", "", r) for r in rules]

            return rules

        with open(self.suffixes_path, encoding="utf8") as file:
            suffixes_dict = json.load(file)

        # reading suffixes
        suffixes = []

        # reading max length
        self.max_suffix_len = max([max([len(s.replace("-", "")) for s in suffixes_dict[sfx]]) for sfx in suffixes_dict])

        # ordering the suffixes in descending with respect to their lengths
        for i in range(self.max_suffix_len, 0, -1):
            length_list = []
            for rule in suffixes_dict:
                for suffix in suffixes_dict[rule]:
                    if len(suffix) == i:

                        # deciding to include derivational suffixes
                        if rule == "Derivational":
                            if self.use_derivational:
                                length_list.append((suffix.replace("-", ""), rule))
                        else:
                            length_list.append((suffix.replace("-", ""), rule))

            if len(length_list):
                suffixes.append(length_list)

        return suffixes


    def stem(self, token: str) -> str:
        if self.include_categories:
            return self.stem_to_categories(token, [])
        else:
            return self.stem_to_word(token)

    def stem_to_categories(self, token: str, categories: list[str]) -> list[str, list]:
        # termination
        if token in self.lexicon:
            return token, categories
        elif self.normalize_word(token) in self.lexicon:
            return self.normalize_word(token), categories

        # recursion
        for suffixes in self.suffixes:
            for suffix in suffixes:
                (suffix, category) = (suffix[0], suffix[1])
                suffix_len = len(suffix)

                if suffix == token[-suffix_len:]:
                    categories.append(category)
                    return self.stem_to_categories(token[:-suffix_len], categories)

        return token, categories


    def stem_to_word(self, token: str) -> str:
        # termination
        if token in self.lexicon:
            return token
        elif self.normalize_word(token) in self.lexicon:
            return self.normalize_word(token)

        # recursion
        for suffixes in self.suffixes:
            for suffix in suffixes:
                suffix = suffix[0]
                suffix_len = len(suffix)

                if suffix == token[-suffix_len:]:
                    return self.stem_to_word(token[:-suffix_len])

        return token


    def stem_sentence(self, sentence: str) -> str:
        sentence  = sentence.split(" ")
        stem_sent = [self.stem(word) for word in sentence]

        if self.include_categories:
            return stem_sent
        else:
            return " ".join(stem_sent)


    # This code is written based on Peter Norvig's spell corrector: https://norvig.com/spell-correct.html
    def edits1(self, word: str) -> list[str]:
        "All edits that are one edit away from `word`."
        letters    = 'abcçdefgğhijklmnoöpqrsştuüvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def normalize_word(self, word: str) -> str:
        E1 = list(self.edits1(word))
        cands = {var: self.corpus[var] for var in E1}
        cands = {c: cands[c] for c in cands if cands[c] > 0}
        cands = sorted(cands.items(), key=lambda i:i[1], reverse=True)

        return cands[0][0] if len(cands) > 0 else word
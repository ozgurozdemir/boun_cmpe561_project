from TurkishStemmer import *
import re
import json
from collections import Counter
import nltk
import string
from tabulate import tabulate
import zeyrek

class TurkishContextFreeGrammar:
    def __init__(self, grammar_path, stemmer_args):
        self.grammar_path = grammar_path
        self.stemmer_args = stemmer_args

        with open(grammar_path, "r", encoding="utf8") as file:
            grammar = json.load(file)

        self.variables = grammar["variables"]
        self.terminals = grammar["terminals"]

        self.constraints = grammar["constraints"]
        self.implies = grammar["implies"]

        self.stemmer = TurkishStemmer(**stemmer_args)

        self.suffixCategoryRules = {"person": "1st|2nd|3rd|1stPL|2ndPL|3rdPL",
                                    "tense": "Past|Present|Future",
                                    "number": "Plural"}

        self.categoryMappings = {"1st|2nd|3rd|1stPL|2ndPL|3rdPL": "person",
                                 "Past|Present|Future": "tense",
                                 "Singular|Plural": "number"}

        self.morph_analyzer = zeyrek.MorphAnalyzer()


    def prepareSuffixCategories(self, suffixCats):
        categories = {}

        for rule in self.suffixCategoryRules:
            for cat in suffixCats:
                categorySearch = re.search(self.suffixCategoryRules[rule], cat)
                if categorySearch:
                    categories[rule] = categorySearch.group()
        return categories


    def mapCategoryLabels(self, category):
        for mapping in self.categoryMappings:
            if re.search(mapping, category):
                return self.categoryMappings[mapping]

        # label is not found
        return "other"


    def search_terminal(self, query, suffixCategories):
        tags = []

        # suffix categories may override
        #suffixCategories = self.prepareSuffixCategories(query[1])

        # root categories
        for category in self.terminals:
            subcategories = {}

            for subcat in self.terminals[category]:

                # subcategory is found
                if query in self.terminals[category][subcat]:
                    categoryLabel = self.mapCategoryLabels(subcat)
                    subcategories[categoryLabel] = subcat

                    # add/override suffix subcategories
                    for sCat in suffixCategories:
                        subcategories[sCat] = suffixCategories[sCat]
            
            if len(subcategories) > 0:
                tags.append((category, subcategories))

        return tags


    def search_variable(self, query):
        tags = []
        # checking all variables
        for variable in self.variables:

            # checking each rule in the variables
            for idxRule, rule in enumerate(self.variables[variable]):
                cat    = [q[0] for q in query]
                subcat = [q[1] for q in query]
                # rule is found
                if rule == cat:
                    #tags.append((variable, subcat[0]))
                    constraintControl = True
                    constraintName = self.constraints[variable][idxRule]

                    # check constraints
                    if constraintName is not None:

                        # checking all defined constraints for the rule
                        for const in constraintName:

                            # for all variables constraint must be satisfied
                            for i in range(0, len(subcat)-1):
                                if const in subcat[i] and const in subcat[i+1]:
                                    constraintControl = constraintControl and subcat[i][const] == subcat[i+1][const]

                    # if the constraint is satisfied add the tag
                    if constraintControl:
                        implyIdx = self.implies[variable][idxRule]
                        tags.append((variable, subcat[implyIdx]))
        return tags

    def calculate_spans(self, tokens, sentence):
        spans = []
        last = 0
        for token in tokens:
            idx = sentence[last:].find(token)
            first = last + idx
            last = first + len(token)
            spans.append((first, last))

        return spans
    
    def cky(self, tokens, vars):
        table = [[[] for i in range(len(tokens))] for j in range(len(tokens))]
        for i in range(len(tokens)):
            table[i][i] = [vars[i]]
        for j in range(1, len(tokens)):
            for i in range(j-1, -1, -1):
                for k in range(i, j):
                    for var1 in table[i][k]:
                        for var2 in table[k+1][j]:
                            var = self.search_variable([var1, var2])
                            if var:
                                for v in var:
                                    if v not in table[i][j]:
                                        table[i][j].append(v)

        return table
    
    def print_table(self, table, tokens):
        print('----------- CKY Table -----------')
        chart = []
        chart.append([token for token in tokens])
        for i in range(len(tokens)):
            row = []
            for j in range(len(tokens)):
                parses = table[i][j]
                parse_list = []
                if parses:
                    for parse in parses:
                        parse_list.append(parse[0])
                    row.append(parse_list)
                else:
                    row.append([])
            chart.append(row)
        
        print(tabulate(chart, headers="firstrow", tablefmt="grid"))
            
    
    def remove_punctuation(self, sentence):
        for punc in string.punctuation:
            sentence = sentence.replace(punc, "")
        return sentence
    
    def get_tense(self, morphemes):
        tense = None
        present = ['Prog1', 'Prog2', 'Aor', 'Cop', 'Pres']
        for inf in morphemes:
            if inf in present:
                tense = 'Present'
            elif 'Past' in inf:
                tense = 'Past'
            elif 'Fut' in inf:
                tense = 'Future'
        return tense
    
    def get_person(self, morphemes):
        person = None
        number = None
        for inf in morphemes:
            if '1sg' in inf:
                person = '1st'
                number = 'Singular'
            elif '1pl' in inf:
                person = '1stPL'
                number = 'Plural'
            elif '2sg' in inf:
                person = '2nd'
                number = 'Singular'
            elif '2pl' in inf:
                person = '2ndPL'
                number = 'Plural'
            elif '3sg' in inf:
                person = '3rd'
                number = 'Singular'
            elif '3pl' in inf:
                person = '3rdPL'
                number = 'Plural'
        
        return person, number
    
    def get_number(self, morphemes):
        number = None
        if 'Plural' in morphemes:
            number = 'Plural'
        else:
            number = 'Singular'
        return number
    
    def create_subcategories(self, tense, person, number):
        return_dict = {}
        if tense:
            return_dict['tense'] = tense
        if person:
            return_dict['person'] = person
        if number:
            return_dict['number'] = number
        if return_dict == {}:
            return_dict['other'] = 'other'
        return return_dict
    
    def adjust_pos(self, pos):
        if pos == "Ques":
            return "Q"
        elif pos == "Adj":
            return "ADJ"
        elif pos == "Adv":
            return "ADV"
        else:
            return pos
    
    def check_validity(self, table):
        if 'S' not in table[0][len(table)-1]:
            return False
        else:
            return True
        
    def parse(self, sentence):
        sentence = self.remove_punctuation(sentence)
        tokens = nltk.tokenize.word_tokenize(sentence)
        print("Tokens: "+ str(tokens))
        vars = []
        pos_tags = []

        for token in tokens:
            #query = self.stemmer.stem(token.lower())
            #query = (token.lower(), [self.morph_analyzer.analyze(token)[0][0].pos])

            parse = self.morph_analyzer.analyze(token)[0][0]
            pos = parse.pos
            pos = self.adjust_pos(pos)
            morphemes = parse.morphemes
            tense = self.get_tense(morphemes)
            person, number = self.get_person(morphemes)
            subcats = self.create_subcategories(tense, person, number)
            var = self.search_terminal(token.lower(), subcats)
            if var:
                vars.append(var[0])
                pos_tags.append(var[0][0])
            else:
                vars.append((pos, subcats))
                pos_tags.append(pos)

        print("POS Tags:"+ str(pos_tags))
        table = self.cky(tokens, vars)
        self.print_table(table, tokens)
        if self.check_validity(table):
            print("Sentence is grammatically valid.")
        else:
            print("Sentence is grammatically invalid.")
        
    
if __name__ == "__main__":

    stemmer_args = {"lexicon_path": "project02/lexicon.txt",
                    "suffixes_path": "project02/suffix_rules.json",
                    "corpus_path": "project02/corpus.txt",
                    "include_categories": True,
                    "use_derivational": False}

    turkishCFG = TurkishContextFreeGrammar("project02/example_grammar.json", stemmer_args)

    turkishCFG.parse("Bu akşamki toplantıya katılacak mısınız")


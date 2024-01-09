from TurkishStemmer import *
import re
import json
from collections import Counter
import nltk
import string
from tabulate import tabulate

try:
    import zeyrek
    import nltk
    nltk.download('punkt')
    print(">> zeyrek module for morphological analysis is imported.")
except ImportError:
    print(":: zeyrek module for morphological analysis is missing. Program can run only in stemmer configuration.")

class Variable():
    def __init__(self, tag, terminal, left_child, right_child, subcat, text = None):
        self.terminal = terminal
        self.text = text
        self.pos = tag
        self.subcat = subcat
        self.left_child = left_child
        self.right_child = right_child

    def __in__(varlist, var):
        for v in varlist:
            if var.pos == v.pos and var.subcat == v.subcat:
                return True
        return False


class TurkishContextFreeGrammar:
    def __init__(self, grammar_path, morphological_analyzer_strategy="stemmer", stemmer_args=None):
        self.grammar_path = grammar_path
        self.stemmer_args = stemmer_args
        self.morphological_analyzer_strategy = morphological_analyzer_strategy

        with open(grammar_path, "r", encoding="utf8") as file:
            grammar = json.load(file)

        self.variables = grammar["variables"]
        self.terminals = grammar["terminals"]
        self.constraints = grammar["constraints"]

        if self.morphological_analyzer_strategy == "stemmer":
            self.stemmer = TurkishStemmer(**stemmer_args)
        elif morphological_analyzer_strategy == "zeyrek":
            self.morph_analyzer = zeyrek.MorphAnalyzer()


        self.suffixCategoryRules = {"person": "1st|2nd|3rd|1stPL|2ndPL|3rdPL",
                                    "tense": "Past|Present|Future",
                                    "number": "Plural"}

        self.categoryMappings = {"1st|2nd|3rd|1stPL|2ndPL|3rdPL": "person",
                                 "Past|Present|Future": "tense",
                                 "Singular|Plural": "number"}


    def prepareSuffixCategories(self, suffixCats):
        categories = {}

        for rule in self.suffixCategoryRules:
            for cat in suffixCats:
                categorySearch = re.search(self.suffixCategoryRules[rule], cat)
                if categorySearch:
                    categories[rule] = categorySearch.group()
        return categories


    def mapCategoryLabels(self, category):
        categoryLabels = {}

        for mapping in self.categoryMappings:
            mappingSearch = re.search(mapping, category)
            if mappingSearch:
                categoryLabels[self.categoryMappings[mapping]] = mappingSearch.group()

        # label is not found
        if len(categoryLabels) > 0:
            return categoryLabels
        else:
          return {"other": category}


    def search_terminal(self, query, suffixCategories):
        tags = []

        # root categories
        for category in self.terminals:
            subcategories = {}

            for subcat in self.terminals[category]:

                # subcategory is found
                if query in self.terminals[category][subcat]:
                    subcategories = self.mapCategoryLabels(subcat)

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
                    constraintControl = True
                    constraintName = self.constraints[variable][idxRule]

                    # check constraints
                    # if constraintName is not None:
                    # checking all defined constraints for the rule
                    for const in constraintName:

                        # for all variables constraint must be satisfied
                        for i in range(0, len(subcat)-1):
                            if const in subcat[i] and const in subcat[i+1]:
                                constraintControl = constraintControl and subcat[i][const] == subcat[i+1][const]

                    # if the constraint is satisfied add the tag
                    if constraintControl:
                        # TODO: append subcats
                        tags.append((variable, subcat[0]))
        return tags


    def cky(self, tokens, vars):
        table = [[[] for i in range(len(tokens))] for j in range(len(tokens))]

        # initalizing the diagonal elements
        for i in range(len(tokens)):
            if vars[i]:
                table[i][i] += vars[i]

        for j in range(1, len(tokens)):
            for i in range(j-1, -1, -1):
                for k in range(i, j):
                    left = table[i][k]
                    right = table[k+1][j]

                    for var1 in left:
                        for var2 in right:
                            var = turkishCFG.search_variable([(var1.pos, var1.subcat), (var2.pos, var2.subcat)])
                            for v in var:
                                found = Variable(v[0], False, var1, var2, v[1])
                                if not Variable.__in__(table[i][j], found):
                                    table[i][j].append(found)
        return table


    def print_tree(self, var):
        if var.terminal:
            return f"({var.pos} {var.text})"
        else:
            return f"({var.pos} {self.print_tree(var.left_child)} {self.print_tree(var.right_child)})"

    def return_possible_parses(self, table, tokens):
        parses = []
        for var in table[0][len(tokens)-1]:
            if var.pos == "S":
                parses.append(self.print_tree(var))
        return parses

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
                        parse_list.append(parse.pos)
                    row.append(parse_list)
                else:
                    row.append([])
            chart.append(row)

        print(tabulate(chart, headers="firstrow", tablefmt="grid"))


    def check_validity(self, table):
        posses = [var.pos for var in table[0][len(table)-1]]
        if 'S' not in posses:
            return False
        else:
            return True


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


    def extract_pos_categories_zeyrek(self, token):
        parse = self.morph_analyzer.analyze(token)[0]
        pos_list = []
        subcats_list = []

        for p in parse:
            pos = p.pos
            pos = self.adjust_pos(pos)
            morphemes = p.morphemes
            tense = self.get_tense(morphemes)
            person, number = self.get_person(morphemes)
            subcats = self.create_subcategories(tense, person, number)

            # if the token is in the grammar use it, otherwise use info from zeyrek
            var = self.search_terminal(token.lower(), subcats)
            if var:
                pos_list.append(var[0][0])
                subcats_list.append(var[0][1])

            pos_list.append(pos)
            subcats_list.append(subcats)

        subcats_list = [(p, subcats_list[i]) for i, p in enumerate(pos_list)]
        return pos_list, subcats_list



    def extract_pos_categories_stemmer(self, token):
        stem, suffixes = self.stemmer.stem(token)
        suffixes = self.prepareSuffixCategories(suffixes)

        categories = self.search_terminal(stem, suffixes)

        if len(categories) != 0:
            pos = categories[0][0]
            subcats = categories[0][1]
        else:
            pos = "??"
            subcats = {}
        return pos, subcats


    def tokenize(self, sentence):
        return re.findall("\w+|\.\.\.|[\.\?\!\-\"\']", sentence)

    def parse(self, sentence):
        tokens = self.tokenize(sentence)
        words = [token for token in tokens if token not in string.punctuation]
        punct = [(token, idx) for idx, token in enumerate(tokens) if token in string.punctuation]

        print("Tokens: "+ str(words))
        vars = []
        pos_tags = []

        for token in words:
            if self.morphological_analyzer_strategy == "zeyrek":
                pos, subcats = self.extract_pos_categories_zeyrek(token)

                _v, _p = [], []
                for p, s in zip(pos, subcats):
                    _v.append((Variable(p, True, None, None, s, token)))
                    _p.append(p)

                vars.append(_v)
                pos_tags.append(_p)

            elif self.morphological_analyzer_strategy == "stemmer":
                pos, subcats = self.extract_pos_categories_stemmer(token.lower())

                vars.append([Variable(pos, True, None, None, subcats, token)])
                pos_tags.append(pos)

        print("POS Tags:"+ str(pos_tags))
        table = self.cky(words, vars)
        self.print_table(table, words)
        if self.check_validity(table):
            print("Sentence is grammatically valid.")
            parses = self.return_possible_parses(table, words)
            print("Possible parses: ")
            for parse in parses:
                print(parse)

        else:
            print("Sentence is grammatically invalid.")

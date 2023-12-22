from TurkishStemmer import *
import re
import json
from collections import Counter

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


    def search_terminal(self, query):
        tags = []

        # suffix categories may override
        suffixCategories = self.prepareSuffixCategories(query[1])

        # root categories
        for category in self.terminals:
            subcategories = {}

            for subcat in self.terminals[category]:

                # subcategory is found
                if query[0] in self.terminals[category][subcat]:
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

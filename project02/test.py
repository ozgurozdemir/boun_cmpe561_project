from TurkishGrammar import *
from TurkishStemmer import *
import json

stemmer_args = {"lexicon_path": "./lexicon.txt",
                "suffixes_path": "./suffix_rules.json",
                "corpus_path": "./corpus.txt",
                "include_categories": True,
                "use_derivational": False}

turkishCFG = TurkishContextFreeGrammar("./example_grammar.json", stemmer_args)

# constraint check: "dün yapıyorum"
query = turkishCFG.stemmer.stem("dün")
var = turkishCFG.search_terminal(query)

query = turkishCFG.stemmer.stem("yapıyorum")
var2 = turkishCFG.search_terminal(query)
print("Search parsing for 'dün yapıyorum':", turkishCFG.search_variable([var[0], var2[0]]))


# constraint check: "dün yaptım"
query = turkishCFG.stemmer.stem("dün")
var = turkishCFG.search_terminal(query)

query = turkishCFG.stemmer.stem("yaptım")
var2 = turkishCFG.search_terminal(query)

print("Search parsing for 'dün yaptım':", turkishCFG.search_variable([var[0], var2[0]]))

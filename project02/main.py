from TurkishGrammar import TurkishContextFreeGrammar
import argparse
import os


parser = argparse.ArgumentParser(description="CYK Parser for Turkish language...")

parser.add_argument("-morph_analyzer", default="zeyrek", help="Strategy for morphological analysis. Opt: zeyrek/stemmer")
parser.add_argument('-grammar_path', default="./data/grammar.json", type=str, help="path of the grammar file for the stemmer")
parser.add_argument('-lexicon_path', default="./data/lexicon.txt", type=str, help="path of the lexicon file")
parser.add_argument('-suffixes_path', default="./data/suffix_rules.json", type=str, help="path of the suffixes file")
parser.add_argument('-corpus_path', default="./data/corpus.txt", type=str, help="path of the corpus file for the stemmer")

args = parser.parse_args()


def parse_sentence(cfg_object, sentence, print_table):
    cfg_object.parse(sentence, print_table)

def parse_multiple(cfg_object, print_table):
    sentences = []
    sent = input(">> Sentence (-1 for parsing all):")

    while sent != "-1":
        sentences.append(sent, print_table)

    for sent in sentences:
        cfg_object.parse(sent, print_table)

def parse_examples(cfg_object, print_table):
    cfg_object.parse("Dün arkadaşıma bir hediye aldım.", print_table)
    print("\n")
    cfg_object.parse("Tarihi romanları keyifle okuyorum.", print_table)
    print("\n")
    cfg_object.parse("Ben dün akşam yemegi için anneme yardım ettim.", print_table)
    print("\n")
    cfg_object.parse("Destanlar milli kültürümüzü ve tarihimizi anlatır.", print_table)
    print("\n")
    cfg_object.parse("Yaz meyvelerinden karpuz bence en güzel meyvedir.", print_table)
    print("\n")
    cfg_object.parse("Bu akşamki toplantıya katılacak mısınız?", print_table)
    print("\n")
    cfg_object.parse("Bu ağacın altında her gece mehtabı izlerdik.", print_table)
    print("\n")
    cfg_object.parse("Siz buraya en son ne zaman geldiniz?", print_table)
    print("\n")
    cfg_object.parse("Okul bizim köye epeyce uzaktaydı.", print_table)
    print("\n")
    cfg_object.parse("Yüksek sesle müzik dinleme.", print_table)
    print("\n")


def parse_negative_examples(cfg_object, print_table):
    cfg_object.parse("Ben arkadaşıma hediye aldın.", print_table)
    print("\n")
    cfg_object.parse("Tarihi bir romanlar okudum.", print_table)
    print("\n")
    cfg_object.parse("Dün babama yardım edeceğim.", print_table)
    print("\n")
    cfg_object.parse("Ben okul gittim.", print_table)
    print("\n")
    cfg_object.parse("Ben kitap okundu.", print_table)
    print("\n")
    cfg_object.parse("Ben okulda gittim.", print_table)
    print("\n")



if __name__ == "__main__":

    if args.morph_analyzer == "zeyrek":
        turkishCFG = TurkishContextFreeGrammar(args.grammar_path, morphological_analyzer_strategy="zeyrek")

    elif args.morph_analyzer == "stemmer":
        stemmer_args = {"lexicon_path": args.lexicon_path,
                        "suffixes_path": args.suffixes_path,
                        "corpus_path": args.corpus_path,
                        "include_categories": True,
                        "use_derivational": False}

        turkishCFG = TurkishContextFreeGrammar(args.grammar_path, morphological_analyzer_strategy="stemmer",
                                               stemmer_args=stemmer_args)

    else:
        raise Exception("Invalid morphological analyzer strategy")


    menu = "\n\t[p]arse single sentence\n\tparse [m]ultiple sentences\n\tparse sentences in the [d]ocument\n\tparse [n]egative sentences in the document\n\t[h]ide cky table\n\t[e]xit\n>> Selection: "
    print_table = True
    opt = input(menu)

    while(opt != "e"):

        if opt == "p":
            sentence = input(">> Sentence: ")
            parse_sentence(turkishCFG, sentence, print_table)

        elif opt == "m":
            parse_multiple(turkishCFG, print_table)

        elif opt == "d":
            parse_examples(turkishCFG, print_table)

        elif opt == "n":
            parse_negative_examples(turkishCFG, print_table)

        elif opt == "h":
            print_table = False
        else:
            print("xx Invalid input...")

        print()
        opt = input(menu)

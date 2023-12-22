import re
import numpy as np
from collections import Counter
from matplotlib import pyplot as plt


class TurkishStopwordRemover:
    def __init__(self, stopword_path, corpus_path=None, use_dynamic=False):
        self.stopword_path = stopword_path
        self.corpus_path = corpus_path
        self.use_dynamic = use_dynamic
        
        self.stopwords = self.__read_stopword_lexicon__()
        
        if self.use_dynamic:
            self.__acquire_unigram__()
            dynamic_stopwords = self.__get_dynamic_stopwords__()
            
            self.stopwords = set(self.stopwords + dynamic_stopwords)
        
        # preparing stopword regex for easy removal
        self.stopwords_regex = "|".join(self.stopwords)
        self.stopwords_regex = f"({self.stopwords_regex})(\s|\.|\?|\!)"
        
        
    def __read_stopword_lexicon__(self):
        with open(self.stopword_path, "r", encoding="utf8") as file:
            stopwords = file.read().split("\n")
        
        return stopwords
    
    
    def __acquire_unigram__(self):
        with open(self.corpus_path, "r", encoding="utf8") as file:
            corpus = file.read().lower()
            
        # removing punctuations, markers and digits
        corpus = re.sub("<s>|<\\\s>|\d+", "", corpus)
        corpus = re.findall("\w+", corpus)
        
        self.unigram = Counter(corpus)
        
        
    def __get_dynamic_stopwords__(self, threshold=0.02):
        # ranking the words wrt occurances  
        words  = [i[0] for i in self.unigram.most_common(1000)]
        counts = [i[1] for i in self.unigram.most_common(1000)]
        rel_freq = [counts[i]/sum(counts[:i]) if i != 0 else 1. for i in range(len(counts))]
        
        # filtering
        max_idx = max([i for i, freq in enumerate(rel_freq) if freq > threshold])
        stopwords = words[:max_idx]
        
        return stopwords
        

    def plot_analysis(self, c=25):
        keys_filtered   = [i[0] for i in self.unigram.most_common(c)]
        counts_filtered = [i[1] for i in self.unigram.most_common(c)]

        counts = [i[1] for i in self.unigram.most_common(len(self.unigram))]
        ranks  = [i for i in range(len(counts))]

        fig, ax = plt.subplots(1, 2, figsize=(15, 8))

        ax[0].plot(counts_filtered)
        ax[0].set_xticks([i for i in range(len(keys_filtered))])
        ax[0].set_xticklabels(keys_filtered, rotation="vertical")
        ax[0].set_title(f"Selected most common {c} words")

        ax[1].plot(np.log(counts), np.log(ranks))
        ax[1].axline((ax[1].get_ylim()[-1], 0), slope=-1, color="red")
        ax[1].set_xlabel("log(rank)")
        ax[1].set_ylabel("log(frequency)")
        ax[1].set_title("Overall corpus")

        plt.show()


    def print_analysis(self, c=25):
        print("Rank\tWord\tFreq\t\tRelative Freq")
        print("----\t----\t------\t\t-------------")

        total  = sum(self.unigram.values())
        words  = [i[0] for i in self.unigram.most_common(c)]
        counts = [i[1] for i in self.unigram.most_common(c)]

        for i in range(c):
            freq = (counts[i]/total)*10**2
            rel_freq = 1 if i == 0 else counts[i]/sum(counts[:i])

            print(f"{i+1}\t{words[i]}\t{freq:.2f} % \t\t{rel_freq:.2f} %")

            
    def remove_stopwords(self, sent: str) -> str:
        return re.sub(self.stopwords_regex, "", sent)
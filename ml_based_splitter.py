from conllu import parse
from sklearn.linear_model import LogisticRegression
import pickle

class MlBasedSentenceSplitter:
    def __init__(self, train_corpus_path, do_train=False):
        self.corpus_path = train_corpus_path
        self.upper_case_letters = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZQXW"
        self.lower_case_letters = "abcçdefgğhıijklmnoöprsştuüvyzqxw"
        self.digits = "0123456789"
        self.space_chars = " \t\n\r\v\f"
        self.apostrophes = "âàáäãèéêëíîòóôûúÂÈÉÊËÌÒÛ"
        self.brackets = "()[]{}"
        self.punctuations = "-.,:;!?\/&@#$%^*+=_<>\"'`~|"
        self.end_of_sentence = ".?!…;"
        if do_train:
            self.lr_classifier = LogisticRegression(max_iter=1000, solver="lbfgs")
            self.__train__()
        else:
            with open('models/ml_based_splitter.pkl', 'rb') as f:
                self.lr_classifier = pickle.load(f)

    
    def isUpper(self, char):
        if char in self.upper_case_letters:
            return 1
        else:
            return 0
    def isLower(self, char):
        if char in self.lower_case_letters:
            return 1
        else:
            return 0
    def isDigit(self, char):
        if char in self.digits:
            return 1
        else:
            return 0

    def isSpace(self, char):
        if char in self.space_chars:
            return 1
        else:
            return 0

    def isApostrophe(self, char):
        if char in self.apostrophes:
            return 1
        else:
            return 0

    def isAlpha(self, char):
        if self.isUpper(char) or self.isLower(char):
            return 1
        else:
            return 0
        
    def isBracket(self, char):
        if char in self.brackets:
            return 1
        else:
            return 0

    def isPunctuation(self, char):
        if char in self.punctuations:
            return 1
        else:
            return 0

    def isEndOfSentence(self, char):
        if char in self.end_of_sentence:
            return 1
        else:
            return 0

    def isNextUpper(self, sentence, index):
        if index == len(sentence) - 1:
            return 1
        else:
            if sentence[index+1] in self.upper_case_letters:
                return 1
            else:
                return 0

    def isNextLower(self, sentence, index):
        if index == len(sentence) - 1:
            return 1
        else:
            if sentence[index+1] in self.lower_case_letters:
                return 1
            else:
                return 0

    def isNextDigit(self, sentence, index):
        if index == len(sentence) - 1:
            return 1
        else:
            if sentence[index+1] in self.digits:
                return 1
            else:
                return 0

    def isNextSpace(self, sentence, index):
        if index == len(sentence) - 1:
            return 1
        else:
            if sentence[index+1] in self.space_chars:
                return 1
            else:
                return 0

    def isNextPunctuation(self, sentence, index):
        if index == len(sentence) - 1:
            return 1
        else:
            if sentence[index+1] in self.punctuations:
                return 1
            else:
                return 0

    def isNextBracket(self, sentence, index):
        if index == len(sentence) - 1:
            return 1
        else:
            if sentence[index+1] in self.brackets:
                return 1
            else:
                return 0

    def isPrevSpace(self, sentence, index):
        if index == 0:
            return 1
        else:
            if sentence[index-1] in self.space_chars:
                return 1
            else:
                return 0

    def isPrevPunctuation(self, sentence, index):
        if index == 0:
            return 1
        else:
            if sentence[index-1] in self.punctuations:
                return 1
            else:
                return 0

    def isPrevBracket(self, sentence, index):
        if index == 0:
            return 1
        else:
            if sentence[index-1] in self.brackets:
                return 1
            else:
                return 0

    def isNextUpper(self, sentence, index):
        if index == len(sentence) - 1:
            return 1
        else:
            if sentence[index+1] in self.upper_case_letters:
                return 1
            else:
                return 0

    def getWord(self, sentence, index):
        i = index
        last_index = index
        while i < len(sentence) and not self.isSpace(sentence[i]):
            last_index = i
            i += 1

        i = index
        first_index = index
        while i >= 0 and not self.isSpace(sentence[i]):
            first_index = i
            if i == 0:
                break
            i -= 1

        word = sentence[first_index:last_index+1]
        return word

    def startCapital(self, sentence, index):
        word = self.getWord(sentence, index)
        if self.isUpper(word[0]) and self.isLower(word[1:]):
            return 1
        else:
            return 0

    def isAllCapitalized(self, sentence, index):
        word = self.getWord(sentence, index)
        if word.isupper():
            return 1
        else:
            return 0

    def isAllLower(self, sentence, index):
        word = self.getWord(sentence, index)
        if word.islower():
            return 1
        else:
            return 0

    def isAllDigit(self, sentence, index):
        word = self.getWord(sentence, index)
        if word.isdigit():
            return 1
        else:
            return 0

    def isAllAlpha(self, sentence, index):
        word = self.getWord(sentence, index)
        if word.isalpha():
            return 1
        else:
            return 0

    def isEmail(self, sentence, index):
        word = self.getWord(sentence, index)
        if '@' in word:
            return 1
        else:
            return 0

    def isURL(self, sentence, index):
        word = self.getWord(sentence, index)
        if 'http://' in word or 'https://' in word:
            return 1
        else:
            return 0

    def isHashtag(self, sentence, index):
        word = self.getWord(sentence, index)
        if '#' in word:
            return 1
        else:
            return 0

    def lengthOfWord(self, sentence, index):
        word =self.getWord(sentence, index)
        return len(word)

    def isNextWordCapital(self, sentence, index):
        word = self.getWord(sentence, index)
        if index == len(sentence) - 1:
            return 1
        else:
            next_word = self.getWord(sentence, index+1)
            if self.isUpper(next_word[0]) and self.isLower(next_word[1:]):
                return 1
            else:
                return 0

    def isNextWordAllCapitalized(self, sentence, index):
        word = self.getWord(sentence, index)
        if index == len(sentence) - 1:
            return 1
        else:
            next_word = self.getWord(sentence, index+1)
            if next_word.isupper():
                return 1
            else:
                return 0

    def isNextWordAllLower(self, sentence, index):
        word = self.getWord(sentence, index)
        if index == len(sentence) - 1:
            return 1
        else:
            next_word = self.getWord(sentence, index+1)
            if next_word.islower():
                return 1
            else:
                return 0

    def isNextWordAllDigit(self, sentence, index):
        word = self.getWord(sentence, index)
        if index == len(sentence) - 1:
            return 1
        else:
            next_word = self.getWord(sentence, index+1)
            if next_word.isdigit():
                return 1
            else:
                return 0

    def isNextWordAllAlpha(self, sentence, index):
        word = self.getWord(sentence, index)
        if index == len(sentence) - 1:
            return 1
        else:
            next_word = self.getWord(sentence, index+1)
            if next_word.isalpha():
                return 1
            else:
                return 0

    def prevAndNextAlpha(self, sentence, index):
        if index == 0 or index == len(sentence) - 1:
            return 0
        else:
            if self.isAlpha(sentence[index-1]) and self.isAlpha(sentence[index+1]):
                return 1
            else:
                return 0

    def prevAndNextDigit(self, sentence, index):
        if index == 0 or index == len(sentence) - 1:
            return 0
        else:
            if self.isDigit(sentence[index-1]) and self.isDigit(sentence[index+1]):
                return 1
            else:
                return 0

    def insidePunctuation(self, sentence, index):
        if index == 0 or index == len(sentence) - 1:
            return 0
        else:
            if self.isPunctuation(sentence[index]) and self.isAlpha(sentence[index-1]) and self.isAlpha(sentence[index+1]):
                return 1
            else:
                return 0
        
    def read_cupt_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
        parsed_data = parse(data)
        return parsed_data
    
    def extractFeatures(self, sentence):
        features_list = []
        for i in range(len(sentence)):
            features = [0] * 33
            features[0] = self.isUpper(sentence[i])
            features[1] = self.isLower(sentence[i])
            features[2] = self.isDigit(sentence[i])
            features[3] = self.isSpace(sentence[i])
            features[4] = self.isApostrophe(sentence[i])
            features[5] = self.isBracket(sentence[i])
            features[6] = self.isPunctuation(sentence[i])
            features[7] = self.isEndOfSentence(sentence[i])
            features[8] = self.isNextUpper(sentence, i)
            features[9] = self.isNextLower(sentence, i)
            features[10] = self.isNextDigit(sentence, i)
            features[11] = self.isNextSpace(sentence, i)
            features[12] = self.isNextPunctuation(sentence, i)
            features[13] = self.isNextBracket(sentence, i)
            features[14] = self.isPrevSpace(sentence, i)
            features[15] = self.isPrevPunctuation(sentence, i)
            features[16] = self.isPrevBracket(sentence, i)
            features[17] = self.startCapital(sentence, i)
            features[18] = self.isAllCapitalized(sentence, i)
            features[19] = self.isAllLower(sentence, i)
            features[20] = self.isAllDigit(sentence, i)
            features[21] = self.isAllAlpha(sentence, i)
            features[22] = self.isEmail(sentence, i)
            features[23] = self.isURL(sentence, i)
            features[24] = self.isHashtag(sentence, i)
            features[25] = self.isNextWordCapital(sentence, i)
            features[26] = self.isNextWordAllCapitalized(sentence, i)
            features[27] = self.isNextWordAllLower(sentence, i)
            features[28] = self.isNextWordAllDigit(sentence, i)
            features[29] = self.isNextWordAllAlpha(sentence, i)
            features[30] = self.prevAndNextAlpha(sentence, i)
            features[31] = self.prevAndNextDigit(sentence, i)
            features[32] = self.insidePunctuation(sentence, i)
            features_list.append(features)

        return features_list
    
    def create_dataset(self, parsed_data):
        X = []
        y = []      
        i = 0
        paragraph = ''
        labels = []
        for sentence in parsed_data:
            if i < 5:
                sent = sentence.metadata['text']
                paragraph += sent + ' '
                sent_labels = [0] * len(sent)
                sent_labels[-1] = 1
                sent_labels = sent_labels + [0]
                labels.extend(sent_labels)
                i += 1
                continue
            
            i = 0
            features = self.extractFeatures(paragraph)
            X.extend(features)
            y.extend(labels)
            paragraph = ''
            labels = []
        return X, y
    
    def __train__(self):
        parsed_data = self.read_cupt_file(self.corpus_path)
        X, y = self.create_dataset(parsed_data)
        self.lr_classifier.fit(X, y)
        with open('models/ml_based_splitter.pkl', 'wb') as f:
            pickle.dump(self.lr_classifier, f)

    def split(self, paragraph):
        features = self.extractFeatures(paragraph)
        predictions = self.lr_classifier.predict(features)
        sentence_boundaries = []
        for i in range(len(predictions)):
            if predictions[i] == 1:
                sentence_boundaries.append(i)
        
        sentences = []
        for i in range(len(sentence_boundaries)):
            if i == 0:
                sentences.append(paragraph[:sentence_boundaries[i]+1].strip())
            else:
                sentences.append(paragraph[sentence_boundaries[i-1]+1:sentence_boundaries[i]+1].strip())
        try:
            sentences.append(paragraph[sentence_boundaries[-1]+1:].strip())
        except IndexError: 
            sentences.append(paragraph)
        return sentences
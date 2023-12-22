import re

class RuleBasedTokenizer:
    def __init__(self):
        self.special_chars = "\n()[]{}\"'\u05F4\uFF02\u055B’”‘“–­​	&  ﻿"
        self.upper_case_letters = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZQXW"
        self.lower_case_letters = "abcçdefgğhıijklmnoöprsştuüvyzqxw"
        self.digits = "0123456789"
        self.apostrophes = "âàáäãèéêëíîòóôûúÂÈÉÊËÌÒÛ"
        self.abbreviations = ["alb", "bnb", "bkz", "bşk", "co", "dr", "dç", "der", "em", "gn", "hz", "kd", "kur", "kuv", "ltd", "md", "mr", "mö", "muh", "müh", "no", "öğr", "op", "opr", "org", "sf", "tuğ", "uzm", "vb", "vd", "yön", "yrb", "yrd", "üniv", "fak", "prof", "dz", "yd", "krm", "gen", "pte", "p", "av", "II", "III", "IV", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "tuğa", "plt", "tğm", "tic", "srv", "bl", "dipl", "not", "min", "cul", "san", "rzv", "or", "kor", "tüm", "st", "sn", "fr", "pl", "ka", "tk", "ko", "vs", "yard", "bknz", "doç", "gör", "müz", "oyn", "m", "s", "kr", "ms", "hv", "uz", "re", "ph", "mc", "ed", "km", "yb", "bk", "jr", "bn", "os", "mrs", "bld", "sen", "alm", "sir", "ord", "dir", "yay", "man", "brm", "edt", "dec", "mah", "cad", "vol","kom", "sok", "apt", "elk", "mad", "ort", "cap", "ste", "exc", "ef"]

    def is_abbreviation(self, word):
        print(word.lower()[:-1])
        return word.lower()[:-1] in self.abbreviations

    def is_apostrophe(self, line, i):
        apostrophe_letters = self.upper_case_letters + self.lower_case_letters + self.digits + self.apostrophes
        return i > 0 and i + 1 < len(line) and line[i - 1] in apostrophe_letters and line[i + 1] in apostrophe_letters

    def is_next_char_uppercase_or_digit(self, line, i):
        while i < len(line) and (line[i] == ' ' or line[i] in self.special_chars):
            i += 1
        return i == len(line) or line[i] in self.upper_case_letters + self.digits + "-"

    def is_name_abbr(self, current_word):
        return len(current_word) == 1 and current_word in self.upper_case_letters or \
               (len(current_word) == 3 and current_word[1] == '.' and current_word[2] in self.upper_case_letters)

    def number_exists_before_and_after(self, line, i):
        return i > 0 and i + 1 < len(line) and line[i - 1] in self.digits and line[i + 1] in self.digits

    def is_next_char_uppercase(self, line, i):
        while i < len(line) and line[i] == ' ':
            i += 1
        return i == len(line) or line[i] in self.upper_case_letters + "\"’'"

    def is_previous_word_uppercase(self, line, i):
        while i >= 0 and (line[i] == ' ' or line[i] in self.lower_case_letters):
            i -= 1
        return i == -1 or line[i] in self.upper_case_letters

    def is_time(self, line, i):
        return i > 0 and i + 2 < len(line) and line[i - 1] in self.digits and line[i + 1] in self.digits and line[i + 2] in self.digits

    def tokenize(self, text):
        email_mode, web_mode = False, False
        i, last_sentence_index, special_quota_count, round_parenthesis_count, bracket_count, curly_bracket_count, quota_count,  apostrophe_count = 0, 0, 0, 0, 0, 0, 0, 0
        current_sentence, current_word, tokenized_sentences = [], "", []
        
        while i < len(text):
            if text[i] in self.special_chars:
                if text[i] in "'’‘\u055B" and current_word != "" and self.is_apostrophe(text, i):
                    current_word += text[i]
                else:
                    if current_word != "":
                        current_sentence.append(current_word)
                    if text[i] != '\n':
                        current_sentence.append(text[i])
                    current_word = ""
                    if text[i] == '{':
                        curly_bracket_count += 1
                    elif text[i] == '}':
                        curly_bracket_count -= 1
                    elif text[i] == '\uFF02':
                        special_quota_count += 1
                    elif text[i] == '\u05F4':
                        special_quota_count -= 1
                    elif text[i] == '“':
                        special_quota_count += 1
                    elif text[i] == '”':
                        special_quota_count -= 1
                    elif text[i] == '‘':
                        special_quota_count += 1
                    elif text[i] == '’':
                        special_quota_count -= 1
                    elif text[i] == '(':
                        round_parenthesis_count += 1
                    elif text[i] == ')':
                        round_parenthesis_count -= 1
                    elif text[i] == '[':
                        bracket_count += 1
                    elif text[i] == ']':
                        bracket_count -= 1
                    elif text[i] == '"':
                        quota_count = 1 - quota_count
                    elif text[i] == '\'':
                        apostrophe_count = 1 - apostrophe_count
                    if text[i] == '"' and bracket_count == 0 and special_quota_count == 0 and curly_bracket_count == 0 and round_parenthesis_count == 0 and quota_count == 0 and self.is_next_char_uppercase_or_digit(text, i + 1):
                        tokenized_sentences.append(current_sentence)
                        current_sentence = []
                        
            else:
                if text[i] in ".?!…":
                    if text[i] == '.' and current_word.lower() == "www":
                        web_mode = True
                    if text[i] == '.' and current_word != "" and (web_mode or email_mode or (text[i - 1] in self.digits + "-" and not self.is_next_char_uppercase_or_digit(text, i + 1))):
                        if (web_mode or email_mode) and i + 1 < len(text) and text[i + 1] != ' ':
                            current_word += text[i]
                        else:
                            current_word += text[i]
                            if not self.is_abbreviation(current_word):
                                current_sentence.append(current_word)
                                current_word = ""
                    else:
                        if text[i] == '.' and (current_word.lower() in self.abbreviations or self.is_name_abbr(current_word)):
                            current_word += text[i]
                            current_sentence.append(current_word)
                            current_word = ""
                        else:
                            if text[i] == '.' and self.number_exists_before_and_after(text, i):
                                current_word += text[i]
                            else:
                                if current_word != "":
                                    current_sentence.append(current_word)
                                current_word = text[i]
                                i += 1
                                while i < len(text) and text[i] in ".?!…":
                                    i += 1
                                i -= 1
                                current_sentence.append(current_word)
                                if round_parenthesis_count == 0 and bracket_count == 0 and curly_bracket_count == 0 and quota_count == 0:
                                    if i + 1 < len(text) and text[i + 1] == '\'' and apostrophe_count == 1 and self.is_next_char_uppercase_or_digit(text, i + 2):
                                        current_sentence.append("'")
                                        i += 1
                                        tokenized_sentences.append(current_sentence)
                                        current_sentence = []
                                        
                                    else:
                                        if i + 2 < len(text) and text[i + 1] == ' ' and text[i + 2] == '\'’' and apostrophe_count == 1 and self.is_next_char_uppercase_or_digit(text, i + 3):
                                            current_sentence.append("'")
                                            i += 2
                                            tokenized_sentences.append(current_sentence)
                                            current_sentence = []
                                            
                                        else:
                                            if self.is_next_char_uppercase_or_digit(text, i + 1):
                                                tokenized_sentences.append(current_sentence)
                                                current_sentence = []
                                                
                                current_word = ""
                else:
                    if text[i] == ' ':
                        email_mode, web_mode = False, False
                        if current_word != "":
                            current_sentence.append(current_word)
                            current_word = ""
                    else:
                        if text[i] == '-' and not web_mode and round_parenthesis_count == 0 and self.is_next_char_uppercase(text, i + 1) and not self.is_previous_word_uppercase(text, i - 1):
                            if current_word != "" and current_word not in self.digits:
                                current_sentence.append(current_word)
                            if len(current_sentence) > 0:
                                tokenized_sentences.append(current_sentence)
                                
                            current_sentence = []
                            round_parenthesis_count, bracket_count, curly_bracket_count, quota_count = 0, 0, 0, 0
                            special_quota_count = 0
                            if current_word != "" and re.match("\\d+", current_word):
                                current_sentence.append(current_word + " -")
                            else:
                                current_sentence.append("-")
                            current_word = ""
                        else:
                            if text[i] in ",:;‚+-*/=":
                                if text[i] == ':' and (current_word == "http" or current_word == "https"):
                                    web_mode = True
                                if web_mode:
                                    current_word += text[i]
                                else:
                                    if text[i] == ',' and self.number_exists_before_and_after(text, i):
                                        current_word += text[i]
                                    else:
                                        if text[i] == ':' and self.is_time(text, i):
                                            current_word += text[i]
                                        else:
                                            if text[i] == '-' and self.number_exists_before_and_after(text, i):
                                                current_word += text[i]
                                            else:
                                                if current_word != "":
                                                    current_sentence.append(current_word)
                                                current_sentence.append(text[i])
                                                current_word = ""
                            else:
                                if text[i] == '@':
                                    current_word += text[i]
                                    email_mode = True
                                else:
                                    current_word += text[i]
            i += 1
        if current_word != "":
            current_sentence.append(current_word)
        if len(current_sentence) > 0:
            tokenized_sentences.append(current_sentence)
        
        tokenized_text = [item for sublist in tokenized_sentences for item in sublist]
        return tokenized_text


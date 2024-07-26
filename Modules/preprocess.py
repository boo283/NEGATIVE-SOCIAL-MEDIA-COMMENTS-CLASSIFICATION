import pandas as pd
import numpy as np
import re

stopwords_path = ".\\vietnamese-stopwords.txt"
teencode_path = ".\\teencode_dict (1).csv"
teencode = pd.read_csv(teencode_path)

def check_hyperlink(text):
    return bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
    
def remove_line_breaks(text):
    return re.sub(r'\n', ' ', text)

def replace_comma(text):
    return re.sub(r',', ';', text)

def get_stopwords():
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = []
        for line in f:
            dd = line.strip('\n')
            stopwords.append(dd)
        stopwords = set(stopwords)
    return stopwords

def remove_character(text):
    character_to_remove = ["'", '"', '?', '=', ')', '(', ':', ';', '!', '-', '–', '+', '*', '>', '<', '...', '...', '…', '•', '“', '”', '•', '[', ']', '{', '}']
    #remove character from text
    for character in character_to_remove:
        text = text.replace(character, '')
    return text

def remove_redundant(text):
    #parkyyyyyyyy to parky
    text = re.sub(r'(\w)\1{2,}', r'\1', text)
    return text

def filter_stop_words(train_sentences, stop_words):
    new_sent = [word for word in train_sentences.split() if word not in stop_words]
    train_sentences = ' '.join(new_sent)
        
    return train_sentences

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

# def deteencode(text):
#     print(text)
#     for index, row in teencode.iterrows():
#         pattern = r'\b{}\b(?=[.,\s]|$)'.format(re.escape(row['teencode']))
#         text = re.sub(pattern, row['meaning'], text)
#     print(text)
#     return text
def deteencode(text):
    for index, row in teencode.iterrows():
        # Adjust pattern to handle special characters better
        pattern = r'(?<!\S){}(?=[.,\s]|$)'.format(re.escape(row['teencode']))
        text = re.sub(pattern, row['meaning'], text)
    return text

def replace_tagname(text, tagname):
    if tagname:
        return text.replace(tagname, 'username')

def remove_stopwords(text):
    with open(stopwords_path, 'r', encoding='utf-8') as file:
        stopwords = file.read().splitlines()
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)

def remove_multiple_spaces(input_string):
    return re.sub(r' +', ' ', input_string)

def preprocess(text):
    if check_hyperlink(text):
        return ''
    text = text.lower()
    text = remove_line_breaks(text)
    text = replace_comma(text)
    text = remove_redundant(text)
    text = deteencode(text)
    text = remove_character(text)
    text = deEmojify(text)
    text = remove_multiple_spaces(text)
    text = remove_stopwords(text)
    return text


import wikipedia
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk
import string
from collections import Counter
import re
import streamlit as st
import heapq

#nltk.download('punkt')
#nltk.download('stopwords')

def content_preprocessing(content):
    content = re.sub(r'[.]+(?!([0-9]|\ |[A-Z]{1}\.))', r'. ', content)
    return content

def sentence_tokenizer(content,portuguese):
    sentences = []
    if portuguese:
        sentences = sent_tokenize(content,language='portuguese')
    else:
        sentences = sent_tokenize(content,language='english')
    
    sentence_list = []
    for sentence in sentences:
        sentence_list.extend(sentence.split('\n'))
    return sentence_list

def word_tokenizer(sentence_list,portuguese):
    words = []
    for sentence in sentence_list:
        if portuguese:
            stopword_list = stopwords.words('portuguese')
            words.extend([word for word in word_tokenize(sentence,language='portuguese')
                         if word not in stopword_list
                         and word.isalpha()])
        else:
            stopword_list = stopwords.words('english')
            words.extend([word for word in word_tokenize(sentence,language='english')
                         if word not in stopword_list
                         and word.isalpha()])
    return words

def word_frequency(words):
    word_frequencies = Counter(words)

    maximum_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
    return word_frequencies

def sentence_score(sentence_list,word_frequencies,portuguese):
    sentence_scores = {}
    for sentence in sentence_list:
        if(portuguese):
            stopword_list = stopwords.words('portuguese')
            sent_words = [word for word in word_tokenize(sentence,language='portuguese')
                         if word not in stopword_list
                         and word.isalpha()]
        else:
            stopword_list = stopwords.words('english')
            sent_words = [word for word in word_tokenize(sentence,language='english')
                         if word not in stopword_list
                         and word.isalpha()]
        for word in sent_words:
            if len(sentence.split(' ')) < 30:
                if sentence not in sentence_scores.keys():
                    sentence_scores[sentence] = word_frequencies[word]
                else:
                    sentence_scores[sentence] += word_frequencies[word]
    return sentence_scores

def generate_summary(sentence_list,sentence_scores,result,number_of_phrases):
    summary_sentences = heapq.nlargest(number_of_phrases, sentence_scores, key=sentence_scores.get)
    sorted_summary = [sentence for sentence in sentence_list if sentence in summary_sentences]
    summary = result.summary.split('\n')[0] + '\n'.join(sorted_summary)
    return(summary)
    

st.title('Summary generator')
query = st.text_input('What do you want to know about?','Brasil')

portuguese = st.checkbox('Results in portuguese?')
if portuguese:
    wikipedia.set_lang('pt')
else:
    wikipedia.set_lang('en')

if (portuguese == False):
    page = st.radio('Choose the result that suit you most',wikipedia.search(query))
    st.write(f'You selected {page}')
    number_of_phrases = st.text_input('Choose the number of phrases in the summary (excluding the first paragraph from wikipedia page)','10')
else:
    page = st.radio('Escolha o resultado que mais se aproxima da sua pesquisa',wikipedia.search(query))
    st.write(f'Voce escolheu {page}')
    number_of_phrases = st.text_input('Escolha o numero de frases no resumo (excluindo o primeiro paragrafo da pagina wikipedia)','10') 
    
try:
    number_of_phrases = int(number_of_phrases)
except:
    number_of_phrases = 10
    if portuguese:
        st.write('Você não utilizou um número. Escolhendo 10 frases.')
    else:
        st.write('Your choice was not a number. Using 10 phrases')

progress_bar = st.progress(0)
result = wikipedia.page(page)
content = result.content

progress_bar.progress(20)
content = content_preprocessing(content)

progress_bar.progress(40)
sentence_list = sentence_tokenizer(content,portuguese)

progress_bar.progress(60)
words = word_tokenizer(sentence_list,portuguese)

progress_bar.progress(70)
word_frequencies = word_frequency(words)

progress_bar.progress(80)
sentence_scores = sentence_score(sentence_list,word_frequencies,portuguese)

progress_bar.progress(90)
summary = generate_summary(sentence_list,sentence_scores,result,number_of_phrases)

progress_bar.progress(100)
st.write(summary)
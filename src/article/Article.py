import re
import spacy
from spacy.pipeline import Sentencizer
from spacy.lang.en import English
from spacy import Language
class Article:
    sentence_separator = r"(?<!\w[\.]\w[\.])(?<![A-Z][a-z][\.])(?<=[\.]|\?|\!)\s"

    def __init__(self, langid: str):
        self.langid = langid
        self.text = None
        self.title = None
        self.contents = None
        self.sentences = []

    def from_text(self, text: str):
        if text is None:
            raise TypeError
        elif text == "":
            raise ValueError('The input text of the article must not be empty!')
        self.text = text
        # self.__detect_title()
        self.__split()

    def from_sentences(self, sentences: list):
        if all(isinstance(sentence, str) for sentence in sentences):
            self.title = sentences[0]
            self.contents = ' '.join(sentences[1:])
            self.text = self.title + '\n' + self.contents
            self.sentences = sentences
        else:
            raise TypeError('The type of a sentence in the sentence list is not string')

    # def __detect_title(self):
    #     parts = self.text.split("\n", 1)
    #     if len(parts) == 1:
    #         # Title does not exist
    #         self.contents = parts[0].strip()
    #     elif len(parts) == 2:
    #         # Title exists
    #         self.title = parts[0].strip()
    #         self.contents = parts[1].strip()
    #         self.sentences.append(self.title)
    #     else:
    #         # Empty article
    #         raise ValueError
    #     self.contents = self.contents.replace('\n', ' ')
    def __split(self):
        # self.text=self.text.replace('«','"')
        self.text=self.text.replace('\u200b','')
        self.text=self.text.replace('\xa0',' ')
        partss = self.text.split("\n")
        if self.langid=='km':
            nlp = English()
            config = {"punct_chars": [ '។', '៕', '?', '!','៚','\n']}
            # sbd = nlp.create_pipe("sentencizer",config=config)
            sentencizer = nlp.add_pipe('sentencizer',config=config)
            @Language.component('custom_km')
            def set_custom_boundaries(doc):
                for token in doc[:-1]:
                # print(token)
                    if token.text == '។':
                        if token.i+1<len(doc) and doc[token.i+1].text== 'ល':
                            if token.i+2<len(doc) and doc[token.i+2].text == '។':
                                doc[token.i+1].is_sent_start = False
                                doc[token.i+2].is_sent_start = False
                        elif token.i+1<len(doc) and doc[token.i+1].text== '។':
                            doc[token.i+1].is_sent_start = False
                return doc
            nlp.add_pipe('custom_km',after="sentencizer")
            for x in range(0,len(partss),1):
                # print(partss[x])
                text=" ".join(partss[x])
                doc = nlp(text)
                for sent in doc.sents:
                    # print(sent.text)
                    text2=list(sent.text)
                    # print(text2)
                    for i in range(0,len(text2)):
                        if text2[i]==" ":
                            if text2[i+1]==" ":
                                text2[i+1]=""
                            else:
                                text2[i]=""
                    text1=''.join(text2)
                    # print(text1)
                    self.sentences.append(text1.strip())
                    # print(self.sentences)
            while '' in self.sentences:
                self.sentences.remove('')
            while '\r' in self.sentences:
                self.sentences.remove('\r')
            while '\n' in self.sentences:
                self.sentences.remove('\n')
            while '\r\n' in self.sentences:
                self.sentences.remove('\r\n')
            while "។" in self.sentences:
                self.sentences.remove("។")
            while "៕" in self.sentences:
                self.sentences.remove("៕")
            while "?" in self.sentences:
                self.sentences.remove("?")
            while "!" in self.sentences:
                self.sentences.remove("!")
            while "៚" in self.sentences:
                self.sentences.remove("៚")   
        elif self.langid=='vi':
            nlp1 = English()
            nlp1.add_pipe('sentencizer')
            @Language.component('custom_vi')
            def set_custom_boundaries(doc):
                for token in doc[:-1]:
                    if token.text == "....":
                        doc[token.i+1].is_sent_start = True
                    if token.text == "…" or token.text == "...":
                        if doc[token.i + 1].text[0].isupper():
                            doc[token.i + 1].is_sent_start = True
                    if token.text == ".":
                        if doc[token.i+1].text == "(":
                            doc[token.i + 1].is_sent_start = True
                            doc[token.i + 2].is_sent_start = False
                    elif token.text == "Rs." or token.text == ")":
                        doc[token.i+1].is_sent_start = False
                    if token.text == "\n":
                        doc[token.i + 1].is_sent_start = True   
                return doc
            nlp1.add_pipe('custom_vi',after="sentencizer")
            for x in range(0,len(partss),1):
                doc = nlp1(partss[x])
                for sent in doc.sents:
                    self.sentences.append(sent.text.strip())
            while '' in self.sentences:
                self.sentences.remove('')
            while '\r' in self.sentences:
                self.sentences.remove('\r')
            while '\n' in self.sentences:
                self.sentences.remove('\n')
            while '\r\n' in self.sentences:
                self.sentences.remove('\r\n')
            while ' ' in self.sentences:
                self.sentences.remove(' ')
            while '.' in self.sentences:
                self.sentences.remove('.')
            while '!' in self.sentences:
                self.sentences.remove('!')
            while '?' in self.sentences:
                self.sentences.remove('?')    
        else:
            for x in range(0,len(partss),1):
                # print(partss[x])
                self.sentences.append(partss[x])
            if '' in self.sentences:
                self.sentences.remove('')

    def __str__(self):
        return self.text

import numpy as np
import jieba
import re
import json
from Emoji import Emoji

class Emotion():
    def __init__(self):
        self.AllSentiment = ['PA','PE','PD','PH','PG','PB','PK','PC','NB','NJ','NH','PF','NI','NC','NG','NE','ND','NN','NK','NL','NAU','Happy','Good','Surprise','Sad','Fear','Disgust','Anger']
        self.AllSentiment_value = {stm:0 for stm in self.AllSentiment}
        self.SentimentWords = {}
        self.sentiment_struct = self.getSentiment(mode=0)
        self.sentiment_dict = self.getSentiment(mode=1)
        self.subsentiment_dict = self.getSentiment(mode=2)
        self.stopwords = self.getStopWords()
        self.sentimentValue = {}
        self.sentimentObjectiveness = {}
        
    def getSentiment(self, mode):
        files = ['./rsc/sentiment.json','./rsc/sentimentvalue.json','./rsc/subsentimentvalue.json']
        with open(files[mode],'r') as f:
            data = json.load(f)
        return data
    
    def getStopWords(self):
        with open('./rsc/stopwords.json','r') as f:
            data = json.load(f)
        return data
    
    def removeStopWords(self,text):
        words = [w for w in text if w not in self.stopwords]
        return words
    
    def findword(self,text):
        word_list = []
        for item in self.sentiment_struct:
            if item[0] in text:
                word_list.append(item[0])
        return word_list
        
    def fit(self,text):
        self.AllSentiment_value = {stm:0 for stm in self.AllSentiment}
        self.SentimentWords = {}
        text_ = re.sub('[a-zA-Z]', '', text)
        words = jieba.lcut(text_)
        words = self.removeStopWords(words)
        words = self.findword(words)
        total_len = len(words)
        total_value = 0
        
        for word in words:
            self.AllSentiment_value[self.sentiment_dict[word][0]] += self.sentiment_dict[word][1]
            if self.subsentiment_dict[word][0] != None:
                self.AllSentiment_value[self.subsentiment_dict[word][0]] += self.subsentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['PA','PE']:
                self.AllSentiment_value['Happy'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['PD','PH','PG','PB','PK']:
                self.AllSentiment_value['Good'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['PC']:
                self.AllSentiment_value['Surprise'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NB','NJ','NH','PF']:
                self.AllSentiment_value['Sad'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NI','NC','NG']:
                self.AllSentiment_value['Fear'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NE','ND','NN','NK','NL']:
                self.AllSentiment_value['Disgust'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NAU']:
                self.AllSentiment_value['Anger'] += self.sentiment_dict[word][1]
            total_value += self.sentiment_dict[word][1]
            self.SentimentWords[word] = self.sentiment_dict[word][0]
            
        for sentiment in self.AllSentiment:
            self.AllSentiment_value[sentiment] /= total_len
        
        self.AllSentiment_value['Happy'] /= 2
        self.AllSentiment_value['Good'] /= 5
        self.AllSentiment_value['Sad'] /= 4
        self.AllSentiment_value['Fear'] /= 3
        self.AllSentiment_value['Disgust'] /= 5

        self.sentimentValue = sorted(self.AllSentiment_value.items(),key=lambda x:x[1],reverse=True)
        self.SentimentWords = sorted(self.SentimentWords.items(),key=lambda x:x[1],reverse=True)
        
    def getTopScore(self,length = 5):
        results = [[stm[0],stm[1]] for stm in self.sentimentValue if stm[1] != 0]
        length = min(length, len(results))
        return results[0:length]
    
    def getObjectiveness(self,length = 5,option='medium'):
        if option == 'weak':
            threshold = 0.5
        elif option == 'medium':
            threshold = 0.75
        elif option == 'strong':
            threshold == 1
        else:
            threshold = 0.75
        results = [[stm[0],1 if stm[1]<=threshold else 0] for stm in self.sentimentValue if stm[1] != 0]
        length = min(length,len(results))
        return results[0:length]
    
    def getClass(self,sentiment):
        if sentiment in ['PA','PE']:
            return 'happy'
        if sentiment in ['PD','PH','PG','PB','PK']:
            return 'good'
        if sentiment in ['PC']:
            return 'surprise'
        if sentiment in ['NB','NJ','NH','PF']:
            return 'sad'
        if sentiment in ['NI','NC','NG']:
            return 'fear'
        if sentiment in ['NE','ND','NN','NK','NL']:
            return 'disgust'
        if sentiment in ['NAU']:
            return 'anger'
    
    def getPicture(self,length=5):
        results = [[stm[0],stm[1]] for stm in self.sentimentValue if stm[1] != 0]
        length = min(length, len(results))
        
        picture = []
        for i in range(length):
            emoji = Emoji(self.getClass(results[i][0]),results[i][0],5 if results[i][1]<0.75 else 10)
            picture.append(emoji.picture)
        return picture
    
    def getWords(self,length=5):
        results = [word[0] for word in self.SentimentWords if word[1]!=0]
        length=min(length,len(results))
        return results[0:length]
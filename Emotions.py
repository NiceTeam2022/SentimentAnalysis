import numpy as np
import jieba
import re
import json
from Emoji import Emoji

class Emotion():
    def __init__(self):
        #Allsentiment包含所有小类大类情感名称
        self.AllSentiment = ['PA','PE','PD','PH','PG','PB','PK','PC','NB','NJ','NH','PF','NI','NC','NG','NE','ND','NN','NK','NL','NAU','Happy','Good','Surprise','Sad','Fear','Disgust','Anger']
        #AllSentiment_value记录每个大小类情感对于的V值
        self.AllSentiment_value = {stm:0 for stm in self.AllSentiment}
        #totalWords记录单词总数(必须先fit才能得到总数)
        self.totalWords = 0
        #记录文本中包含的情感词
        self.SentimentWords = {}
        #以下三个分别代表情感词典/情感-V/辅助情感-V，利用json读入
        #sentiment_struct元素形式[情感,词性,小类情感,强度,极性,辅助情感,辅助情感强度,辅助情感极性]
        self.sentiment_struct = self.getSentiment(mode=0)
        #sentiment_dict为字典，每个元素形式 情感词:[情感,V值]
        self.sentiment_dict = self.getSentiment(mode=1)
        #如上，为辅助情感，若不存在辅助情感，则为None
        self.subsentiment_dict = self.getSentiment(mode=2)
        #stopwords包含所有停词，初始化时就已读入
        self.stopwords = self.getStopWords()
        #包含所有情感对应的V值，降序排列，每个元素为一个二元列表[情感,V值]
        self.sentimentValue = []
        #包含所有情感对应的客观性，与上者形式同样，V值变为0/1,0表示不客观,1表示客观
        self.sentimentObjectiveness = []
    
    #读取文件    
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
    
    #找到文本中所有情感词
    def findword(self,text):
        word_list = []
        for item in self.sentiment_struct:
            if item[0] in text:
                word_list.append(item[0])
        return word_list
    
    #分析文本    
    def fit(self,text):
        #预处理
        self.AllSentiment_value = {stm:0 for stm in self.AllSentiment}
        self.SentimentWords = {}
        text_ = re.sub('[a-zA-Z]', '', text)
        words = jieba.lcut(text_)
        words = self.removeStopWords(words)
        words = self.findword(words)
        total_len = len(words)
        total_value = 0
        
        for word in words:
            #对应情感要加上情感词的V值
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
            self.SentimentWords[word] = self.sentiment_dict[word][1]
        
        #所有情感除以情感词总数    
        for sentiment in self.AllSentiment:
            self.AllSentiment_value[sentiment] /= total_len
        #大类情感额外除以小类情感数
        self.AllSentiment_value['Happy'] /= 2
        self.AllSentiment_value['Good'] /= 5
        self.AllSentiment_value['Sad'] /= 4
        self.AllSentiment_value['Fear'] /= 3
        self.AllSentiment_value['Disgust'] /= 5
        self.totalWords = total_len
        self.sentimentValue = sorted(self.AllSentiment_value.items(),key=lambda x:x[1],reverse=True)
        self.SentimentWords = sorted(self.SentimentWords.items(),key=lambda x:x[1],reverse=True)
        
    def getTopScore(self,length = 5):
        results = [[stm[0],stm[1]] for stm in self.sentimentValue if float(stm[1]) != 0]
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
        results = [[stm[0],1 if stm[1]<=threshold else 0] for stm in self.sentimentValue if float(stm[1]) != 0]
        length = min(length,len(results))
        return results[0:length]
    
    #返回小类情感对应的大类情感
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
        results = [[stm[0],stm[1]] for stm in self.sentimentValue if float(stm[1]) != 0]
        length = min(length, len(results))
        
        picture = []
        for i in range(length):
            emoji = Emoji(self.getClass(results[i][0]),results[i][0],5 if results[i][1]<0.75 else 10)
            picture.append(emoji.picture)
        return picture
    
    def getWords(self):
        results = [word[0] for word in self.SentimentWords if int(word[1])>=5]
        length = min(int(self.totalWords*0.1)+1,len(results))
        return results[0:length]
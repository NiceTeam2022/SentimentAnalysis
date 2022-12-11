import numpy as np
import jieba
import re
import json
from Emoji import Emoji


# 刘志远，2022-12-03：新增了全局变量，提高时间空间效率

# 所有小类和大类情感
AllSentiment = ['PA','PE','PD','PH','PG','PB','PK','PC','NB','NJ','NH','PF','NI','NC','NG','NE','ND','NN','NK','NL','NAU','Happy','Good','Surprise','Sad','Fear','Disgust','Anger']
#中英文对照字典
EmoDic = {"Happy":"高兴","Good":"愉快","Surprise":"惊奇","Sad":"哀伤","Fear":"害怕","Disgust":"厌恶","Anger":"愤怒",
          "PA":"快乐","PE":"安心","PD":"尊敬","PH":"赞扬","PG":"相信","PB":"喜爱","PK":"祝愿","NAU":"愤怒","NB":"悲伤",
          "NJ":"失望","NH":"内疚","PF":"思念","NI":"慌张","NC":"恐惧","NG":"害羞","NE":"烦闷","ND":"憎恶","NN":"贬责",
          "NK":"妒忌","NL":"怀疑","PC":"惊奇"}
# 大类情感
BigEmotion = ["Happy","Good","Surprise","Sad","Fear","Disgust","Anger"]
# 小类情感
SmallEmotion = ['PA','PE','PD','PH','PG','PB','PK','PC','NB','NJ','NH','PF','NI','NC','NG','NE','ND','NN','NK','NL','NAU']
# 停用词
# 刘志远，2022-12-05：改为txt文件
# 顾永威，2022-12-05：修复了json读入
with open('./rsc/stopwords.json', 'r', encoding='utf-8') as f:
    stopwords = json.load(f)
    
# 分句符号、标点符号
# 来源zhon.hanzi.sentence、zhon.hanzi.punctuation
sentence_sign = '[〇一-\u9fff㐀-\u4dbf豈-\ufaff𠀀-\U0002a6df𪜀-\U0002b73f𫝀-\U0002b81f丽-\U0002fa1f⼀-⿕⺀-⻳＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､\u3000、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·]*[！？｡。][」﹂”』’》）］｝〕〗〙〛〉】]*'
punctuation = '＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､\u3000、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。'

# Broadcasting计算长度
nplen = np.frompyfunc(len, 1, 1)


class DDNLP():
    def __init__(self, text, status):
        # 刘志远，2022-12-03：数据清洗步骤加入初始化，节约时间
        # 去除英文、数字、空格
        self.text_ = re.sub('[a-zA-Z0-9 ]', '', text)
        # 分词
        self.words = jieba.lcut(self.text_)
        self.words = list(filter(lambda x: False if x in punctuation else True, self.words))
        # 实词
        self.notions = self.removeStopWords(self.words)
        # 分句
        # 注：会忽略含英文的句子
        paras = self.text_.split('\n')
        sents = []
        for para in paras:
            para_sents = re.findall(sentence_sign, para)
            # 刘志远，2022-12-05：修复了bug - 无分句符号的段落不被识别为一个句子
            if (para != '') & (para_sents == []):
                sents += [para]
            else:
                sents += para_sents
        self.sents = sents
        # 刘志远，2022-12-03：应用场景选项参数内置
        # 0、1、2分别对应3个场景：公司、学校、其他
        self.status = status

        
        # 顾永威
        # 刘志远，2022-12-03：补充V值定义
        # 某类情感的V值定义为：SUM(情感词强度 if 情感词∈该情感类别) / COUNT(所有情感词)
        # 大类情感需额外除以其包含的小类情感数量
        # AllSentiment_value记录每个大小类情感对于的V值
        self.AllSentiment_value = {stm: 0 for stm in AllSentiment}
        # totalWords记录单词总数(必须先fit才能得到总数)
        self.totalWords = 0
        # 记录文本中包含的情感词
        self.SentimentWords = {}
        # 以下三个分别代表情感词典/情感-V/辅助情感-V，利用json读入
        # sentiment_struct元素形式[情感,词性,小类情感,强度,极性,辅助情感,辅助情感强度,辅助情感极性]
        self.sentiment_struct = self.getSentiment(mode=0)
        # sentiment_dict为字典，每个元素形式 情感词:[情感,V值]
        self.sentiment_dict = self.getSentiment(mode=1)
        # 如上，为辅助情感，若不存在辅助情感，则为None
        self.subsentiment_dict = self.getSentiment(mode=2)
        # 包含所有情感对应的V值，降序排列，每个元素为一个二元列表[情感,V值]
        self.sentimentValue = []
        # 包含所有情感对应的客观性，与上者形式同样，V值变为0/1,0表示不客观,1表示客观
        self.sentimentObjectiveness = []
        # 读入文本后开始分析
        self.fit()

    # 读取文件
    # 顾永威
    # 刘志远，2022-12-03：建议也改为全局变量
    def getSentiment(self, mode):
        files = ['./rsc/sentiment.json', './rsc/sentimentvalue.json', './rsc/subsentimentvalue.json']
        with open(files[mode], 'r') as f:
            data = json.load(f)
        return data

    # 去除停用词
    # 顾永威
    # 刘志远，2022-12-03：纠正变量命名，改用了更快的算法，在已测试算法中效率最高
    def removeStopWords(self, words):
        notions = list(filter(lambda x: False if x in stopwords else True, words))
        return notions
    
    # 找到文本中所有情感词
    # 顾永威
    # 刘志远，2022-12-03：纠正变量命名，修改输入
    def findSentWords(self):
        word_list = []
        for item in self.sentiment_struct:
            if item[0] in self.notions:
                word_list.append(item[0])
        return word_list
    
    # 计算情感类别强度
    # 顾永威
    # 刘志远，2022-12-03：依据新结构修改初始化部分，并增加注释
    def fit(self):
        # 重新初始化
        self.AllSentiment_value = {stm: 0 for stm in AllSentiment}
        self.SentimentWords = {}
        # 筛选情感词
        words = self.findSentWords()
        total_len = len(words)
        # 顾永威，2022-12-05：修复了无中文文本情况下除以0的情况
        if total_len == 0:
            return
        total_value = 0
        for word in words:
            # 对应情感要加上情感词的V值
            self.AllSentiment_value[self.sentiment_dict[word][0]] += self.sentiment_dict[word][1]
            if self.subsentiment_dict[word][0] != None:
                self.AllSentiment_value[self.subsentiment_dict[word][0]] += self.subsentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['PA', 'PE']:
                self.AllSentiment_value['Happy'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['PD', 'PH', 'PG', 'PB', 'PK']:
                self.AllSentiment_value['Good'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['PC']:
                self.AllSentiment_value['Surprise'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NB', 'NJ', 'NH', 'PF']:
                self.AllSentiment_value['Sad'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NI', 'NC', 'NG']:
                self.AllSentiment_value['Fear'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NE', 'ND', 'NN', 'NK', 'NL']:
                self.AllSentiment_value['Disgust'] += self.sentiment_dict[word][1]
            if self.sentiment_dict[word][0] in ['NAU']:
                self.AllSentiment_value['Anger'] += self.sentiment_dict[word][1]
            total_value += self.sentiment_dict[word][1]
            self.SentimentWords[word] = self.sentiment_dict[word][1]

        # 所有情感V值除以情感词总数
        for sentiment in AllSentiment:
            self.AllSentiment_value[sentiment] /= total_len
        # 大类情感额外除以小类情感数
        self.AllSentiment_value['Happy'] /= 2
        self.AllSentiment_value['Good'] /= 5
        self.AllSentiment_value['Sad'] /= 4
        self.AllSentiment_value['Fear'] /= 3
        self.AllSentiment_value['Disgust'] /= 5
        self.totalWords = total_len
        self.sentimentValue = sorted(self.AllSentiment_value.items(), key=lambda x: x[1], reverse=True)
        self.SentimentWords = sorted(self.SentimentWords.items(), key=lambda x: x[1], reverse=True)
    
    # 获取强度最高的情感类别
    # 刘志远，2022-12-03：增加注释
    # 刘志远，2022-12-11：修复了返回客观异常，调整了阈值
    def getTopScore(self, length=5):
        threshold = 0
        if self.status == 0: # 公司
            threshold = 0.75
        elif self.status == 1: # 学校
            threshold = 1
        elif self.status == 2: # 其他
            threshold = 1.5
        else:
            threshold = 1.5
        # 不考虑情感强度为0的类别
        results = [[stm[0] if stm[1] > threshold else "object", stm[1]] for stm in self.sentimentValue if float(stm[1]) != 0]
        length = min(length, len(results))
        zh_results = []
        
        for i in range(length):
            if results[i][0] == "object":
                zh_results.append(["客观",results[i][1]])
                break
            zh_results.append([EmoDic[results[i][0]],results[i][1]])
        return zh_results
        
    # 判断情感是否可以被认为是“客观”
    # 刘志远，2022-12-03：依据新结构修改初始化部分，并增加注释
    def getObjectiveness(self, length=5):
        threshold = 0
        if self.status == 0: # 公司
            threshold = 0.75
        elif self.status == 1: # 学校
            threshold = 1
        elif self.status == 2: # 其他
            threshold = 1.5
        else:
            threshold = 1.5
        results = [[stm[0], 1 if stm[1] <= threshold else 0]
                   for stm in self.sentimentValue if float(stm[1]) != 0]
        length = min(length, len(results))
        zh_results = []
        for i in range(length):
            zh_results.append([EmoDic[results[i][0]],results[i][1]])
        return zh_results

    # 返回小类情感对应的大类情感
    def getClass(self, sentiment):
        if sentiment in ['PA', 'PE']:
            return 'happy'
        if sentiment in ['PD', 'PH', 'PG', 'PB', 'PK']:
            return 'good'
        if sentiment in ['PC']:
            return 'surprise'
        if sentiment in ['NB', 'NJ', 'NH', 'PF']:
            return 'sad'
        if sentiment in ['NI', 'NC', 'NG']:
            return 'fear'
        if sentiment in ['NE', 'ND', 'NN', 'NK', 'NL']:
            return 'disgust'
        if sentiment in ['NAU']:
            return 'anger'
    
    # 获取表情图片
    def getPicture(self, length=5):
        threshold = 0
        if self.status == 0: # 公司
            threshold = 0.75
        elif self.status == 1: # 学校
            threshold = 1
        elif self.status == 2: # 其他
            threshold = 1.5
        else:
            threshold = 1.5
        results = [[stm[0] if stm[1] > threshold else "object", stm[1]] for stm in self.sentimentValue if float(stm[1]) != 0]
        length = min(length, len(results))
        if length == 0:
            return ["/rsc/emoji/loading.png"]
        picture = []
        for i in range(length):
            if results[i][0] in SmallEmotion:
                emoji = Emoji(self.getClass(results[i][0]), results[i][0], 5 if results[i][1] < 0.75 else 10)
            elif results[i][0] in BigEmotion:
                emoji = Emoji(results[i][0],None,5 if results[i][1] < 0.75 else 10)
            elif results[i][0] == "object":
                emoji = Emoji("object",5 if results[i][1] < 0.75 else 10)
                picture.append(emoji.picture)
                return picture
            picture.append(emoji.picture)
        return picture
    
    # 获取强度最高的情感词
    # 刘志远，2022-12-03：增加注释
    # 筛选规则：
    # 1. 强度不低于5；
    # 2. 在所有情感词中，强度排前10%。
    def getWords(self):
        results = [word[0] for word in self.SentimentWords if int(word[1]) >= 5]
        length = min(int(self.totalWords*0.1)+1, len(results))
        return results[0:length]
    
    # 平均句长
    # 刘志远，2022-12-03
    def getAverageLen(self): 
        # 保留汉字
        sents_de_punc = []
        for sent in self.sents:
            sents_de_punc += [re.sub('[^\u4e00-\u9fff]*', '', sent)]
        # 句长
        sents_len = nplen(sents_de_punc)
        sents_len = sents_len.astype(float)
        return np.nanmean(sents_len)
    
    # 长句
    # 刘志远，2022-12-03
    # 刘志远，2022-12-05：阈值调低10
    def getLongSent(self):
        # 句长阈值
        threshold = 40 if self.status==0 else (50 if self.status==1 else 60)
        # 保留汉字
        sents_de_punc = []
        for sent in self.sents:
            sents_de_punc += [re.sub('[^\u4e00-\u9fff]*', '', sent)]
        # 句长
        sents_len = nplen(sents_de_punc)
        # 长度大于阈值的句子
        long_sents = [self.sents[i] for i in range(len(self.sents)) if sents_len[i] > threshold]
        return long_sents
    
    # 信息密度
    # 刘志远，2022-12-03
    def getDensity(self):
        return len(self.notions) / len(self.words)
    
    # 注：当前计算未涉及情感极性


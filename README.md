# SentimentAnalysis
> 此仓库包含了情感分析方法  
> 使用方法详见Document.ipynb  
### 等等NLP
+ 使用方法  
    1. 引用DDNLP类
        ```python
        from ddnlp import DDNLP
        ```
    2. 准备一段文本
        ```python
        text  = '这是一段精彩至极的文本，非常地精彩'
        ```
    3. 初始化一个DDNLP类
        ```python
        #status表示使用场景,0表示公司，1表示学校，2表示其它
        dd = DDNLP(text,status=0)
        ```
    4. 使用以下的方法得到想要的数据吧
        ```python
        #得到得分最高的几个情感
        dd.getTopScore()
        #得到得分最高的几个情感的客观程度
        dd.getObjectiveness()
        #得到对应的emoji
        dd.getPicture()
        #得到情感最强烈的几个单词
        dd.getWords()
        #得到平均句长
        dd.getAverageLen()
        #得到长度长得不合理的句子
        dd.getLongSent()
        #得到信息密度
        dd.getDensity()
        ```
+ 遇到问题请找顾永威或刘志远
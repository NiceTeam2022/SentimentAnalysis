import sqlite3

class Emoji():
    def __init__(self,set_emotion="good",set_class = None,set_intensity = None):
        self.emotion = self.EmoAdjust(set_emotion,0)
        self.emoClass = self.EmoAdjust(set_class,1)
        self.intensity = set_intensity
        self.picture = self.getPicturePath()
    
    def EmoAdjust(self,emo,mode):
        if emo == None:
            return None
        if emo == 'Disgust' or emo == 'disgust':
            return 'hate'
        if mode == 0:
            return emo.lower()
        elif mode == 1:
            return emo
    
    
    def getPicturePath(self):
        if self.emotion == "object":
            return "./rsc/emoji/loading.png"
        if self.emoClass == None:
            if self.intensity == None:
                return "./rsc/emoji/{}.png".format(self.emotion)
            else:
                if self.intensity >= 0 and self.intensity <= 5:
                    return "./rsc/emoji/{}-5.png".format(self.emotion)
                elif self.intensity >=5 and self.intensity <= 10:
                    return "./rsc/emoji/{}-10.png".format(self.emotion)
        else:
            if self.intensity == None:
                return "./rsc/emoji/{}-{}.png".format(self.emotion,self.emoClass)
            else:
                if self.intensity >= 0 and self.intensity <= 5:
                    return "./rsc/emoji/{}-{}-5.png".format(self.emotion,self.emoClass)
                elif self.intensity >=5 and self.intensity <= 10:
                    return "./rsc/emoji/{}-{}-10.png".format(self.emotion,self.emoClass)
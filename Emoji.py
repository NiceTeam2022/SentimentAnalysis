import sqlite3

class Emoji():
    def __init__(self,set_emotion="good",set_class = None,set_intensity = None):
        self.emotion = set_emotion
        self.emoClass = set_class
        self.intensity = set_intensity
        self.picture = self.getPicturePath(self.emotion,self.intensity)
         
    def getPicturePath(self,emo,its):
        if self.emoClass == None:
            if self.intensity == None:
                return "./rsc/emoji/{}.png".format(self.emotion)
            else:
                if self.intensity >= 1 and self.intensity <= 5:
                    return "./rsc/emoji/{}-5.png".format(self.emotion)
                elif self.intensity >=6 and self.intensity <= 10:
                    return "./rsc/emoji/{}-10.png".format(self.emotion)
        else:
            if self.intensity == None:
                return "./rsc/emoji/{}-{}.png".format(self.emotion,self.emoClass)
            else:
                if self.intensity >= 1 and self.intensity <= 5:
                    return "./rsc/emoji/{}-{}-5.png".format(self.emotion,self.emoClass)
                elif self.intensity >=6 and self.intensity <= 10:
                    return "./rsc/emoji/{}-{}-10.png".format(self.emotion,self.emoClass)
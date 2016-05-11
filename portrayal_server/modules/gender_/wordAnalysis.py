# -*- coding: utf-8 -*-
__author__ = 'yu.fu'
from py4j.java_gateway import JavaGateway
class WordAnalysis:
    def __init__(self):
        self.__gateway = JavaGateway()
        pass

    def splitWords(self, sentence):
        words = self.__gateway.entry_point.getWords(sentence)
        return words

    def test(self,sentence):
        words = self.splitWords(sentence)
        print type(words)




if __name__ == '__main__':
    word = WordAnalysis()
    word.test(u"这个语句是什么意思? 每次运行都会出错呢")
    word.test(u"外设产品	摄像头	| |良田 窈窕淑女(专业版)|良田")
    word.test(u"电脑/办公	外设产品	摄像头 良田 窈窕淑女(专业版)|良田")
    word.test(u"电脑/办公	外设产品	摄像头")
    word.test(u"电脑/办公 窈窕淑女(专业版)|良田")

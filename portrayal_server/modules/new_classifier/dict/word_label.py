# coding=utf8
import re, json, sys, time, os

class WordLabel(object):
    def __init__(self, area_file=None, color_file=None, quantifier_file=None, num_file=None):
        curdir = os.path.dirname(os.path.abspath(__file__))
        if not area_file:
            area_file = curdir + "/city.txt"
        self.load_area(area_file)

        if not color_file:
            color_file = curdir + "/color.txt"
        self.load_color(color_file)

        if not quantifier_file:
            quantifier_file = curdir + "/quantifier.txt"
        if not num_file:
            num_file = curdir + "/num_zh.txt"
        self.load_quantifier(quantifier_file, num_file)



    # 地域
    def load_area(self, area_file):
        area_word = u"(市|省|地区|林区|自治区)$"
        self.re_area = re.compile(area_word)
        
        with open(area_file, "r") as f:
            self.area_lst = f.read().strip().decode("u8").split(u"\n")

    def is_area(self, word):
        new_word = self.re_area.sub(u"", word)
        if new_word in self.area_lst:
            word = u"area__%s" % new_word
        return word

    # 颜色
    def load_color(self, file_color):
        with open(file_color, "r") as f:
            self.color_lst = f.read().strip().decode("u8").split(u"\n")

    def is_color(self, word):
        if word in self.color_lst:
            return u"color__%s" % word.rstrip(u"色")
        new_word = word.rstrip(u"色")
        if new_word in self.color_lst:
            word = u"color__%s" % new_word
        return word

    # 量词
    def load_quantifier(self, file_quantifier, file_num):
        with open(file_quantifier, "r") as f:
            self.quantifier_lst = f.read().strip().decode("u8").split(u"\n")

        with open(file_num, "r") as f:
            self.num_zh = f.read().strip().decode("u8").split(u"\n")
        num_word = ur"^\d+\.?\d*|[%s]+" % (u"".join(self.num_zh))
        self.re_num = re.compile(num_word)

    def not_quantifier(self, word):
        brand = [u"361°", u"361度"]
        if word in brand:
            return True

    def is_quantifier(self, word, word0=None):
        if self.not_quantifier(word):
            return word
        if (word in self.quantifier_lst):
            if word0 and (not self.re_num.sub(u"", word0)):
                return u"qnt__%s" % word
            else:
                return word
        new_word = self.re_num.sub(u"", word)
        if new_word in self.quantifier_lst:
            word = u"qnt__%s" % new_word
        return word

    def word_label(self, word, word0=None):
        new_word = self.is_area(word)
        if new_word != word:
            return new_word
        new_word = self.is_color(word)
        if new_word != word:
            return new_word
        new_word = self.is_quantifier(word, word0)
        if new_word != word:
            return new_word
        return word

if __name__ == '__main__':
    test_file = "test_word_label"
    wl = WordLabel()
    with open(test_file, "r") as f:
        for line in f:
            word = line.strip().decode("u8")
            print word, wl.word_label(word)


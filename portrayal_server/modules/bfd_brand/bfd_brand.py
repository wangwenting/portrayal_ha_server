# -*- coding:utf-8 -*-
import re
import logging
import os
import HTMLParser


class BrandUtils(object):
    def __init__(self, dot_file=None, char_map_file=None):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if not dot_file:
            dot_file = cur_dir + "/resource/dot.txt"
        if not char_map_file:
            char_map_file = cur_dir + "/resource/char_map.txt"

        self.load_dots(dot_file)
        self.load_char_map(char_map_file)

        self.html_parser = HTMLParser.HTMLParser()
        # 判断是否包含括号
        self.brackets = u'(?=\\(.*\\)|（.*）)'
        brc = u'([^()（]+?)[（(]([^()2（]+?)[)）]|[（(]([^()（]+?)[)）]([^()（）]+)'
        self.PAT_brc = re.compile(brc)  # (en)cn or (cn)en

        # 干扰字的模式
        # shop = u'([^（(]+)[（(].*[%s].*[)）]' % u'人天地中海国州洲洋园店路街桥场所楼厦馆城市区院所寓座站房间床厅购票券签部社展江期锅送京屯途安圳华村庄司坊'
        shop = u'([（(].*[)）]|\[.*\])'
        self.PAT_shop = re.compile(shop)
        counter_word = u'(?P<counter>[仅售需付]*\d+[.0-9]*[元包券])'
        self.PAT_counter = re.compile(counter_word)

        # 中英文模式
        self.en_pa = r'[\w\s&+]'
        en_pattern = r'%s+(.%s+)*' % (self.en_pa, self.en_pa)
        self.en_sp = re.compile(en_pattern)
        self.cn_pattern = r'[^\w\s]+'

        ex_pattern = r'(^\w$)|(^\d+$)'    # 英文名为一个字母或纯数字
        self.ex_sp = re.compile(ex_pattern)
    
        null_pattern = u'^(na|none|null|other|others|无)$|unbrand|notprovide|其它|其他|品牌|产地'
        self.null_re = re.compile(null_pattern, re.IGNORECASE)        

    # 品牌特殊符
    def load_dots(self, dot_file):
        with open(dot_file, "r") as f:
            dots = r'[%s]' % f.read().replace('\n', '').decode('utf-8')
            self.dot_re = re.compile(dots)
        
    def rm_dot(self, text):
        return self.dot_re.subn(u'', text)[0]

    # 字符转换
    def load_char_map(self, char_map_file):
        self.char_map = {}
        with open(char_map_file, "r") as f:
            for line in f:
                try:
                    char, stn = line.decode("utf8").strip(u"\n").split(u"\t")
                    self.char_map[char] = stn
                except Exception, e:
                    logging.error(e)

    def char2map(self, text):
        string = u""
        for char in text:
            char = self.char_map.get(char, char)
            string += char
        return string

    # 英文名检测
    @staticmethod
    def is_alnum(s):
        for c in s:
            if ord(c) > 255:
                return False
        return True

    # 全角字符转换
    @staticmethod
    def full2half(text):
        string = u""
        for char in text:
            code = ord(char)
            if code == 12288:
                code = 32
            elif (code >=65281 and code <= 65374):
                code -= 65248
            string += unichr(code)
        return string

    # strip字符
    @staticmethod
    def myStrip(text):
        strip_char = u''' "'[]:;,.!|/\\·-*#\t\r\n'''
        return text.strip(strip_char)

    # 品牌名预处理
    def refine(self, brand, dot=False, strp=True):
        # 去除干扰字
        # brand = PAT_counter.sub(u'', brand)
        brand = self.char2map(brand)
        brand = self.html_parser.unescape(brand) 
        if strp:
            brand = self.myStrip(brand)
            brand = brand.lstrip(u")").rstrip(u"(")
        if dot:
            brand = self.rm_dot(brand)
        return brand

    # 空品牌
    def is_null(self, brand):
        if not brand.strip() or self.null_re.search(brand):
            return True
        else:
            return False

    # 品牌中英文名提取
    def brand_shop(self, brand):
        """团购类: CN_NAME(XXX店)"""
        brand = self.PAT_shop.sub(u'', brand)
        return brand 

    def brand_bracket(self, brand):
        """CN_NAME(EN_NAME) or (EN_NAME)CN_NAME"""
        m = self.PAT_brc.match(brand)
        if m:
            cn_name = m.groups()[0]
            en_name = m.groups()[1]
            if not cn_name:
                cn_name = m.groups()[2]
                en_name = m.groups()[3]
            if self.is_alnum(en_name):
                return set(cn_name, en_name)
            elif self.is_alnum(cn_name):
                return set(en_name, cn_name)
        return False

    def brand_back(self, brand):
        """(CN_NAME/EN_NAME) or (EN_NAME/CN_NAME)"""
        brand = self.refine(brand)
        if brand.find(u'/') != -1:
            segs = brand.split(u'/')
            if self.is_alnum(segs[0]):
                en_name = segs[0]
                cn_name = segs[1]
            else:
                cn_name = segs[0]
                en_name = segs[1]
            return set(cn_name, en_name)
        elif brand.find(u'\\') != -1:
            segs = brand.split(u'\\')
            if self.is_alnum(segs[0]):
                en_name = segs[0]
                cn_name = segs[1]
            else:
                cn_name = segs[0]
                en_name = segs[1]
            return set(cn_name, en_name)
        return False
    
    def brand_split(self, brand):
        """(CN_NAME EN_NAME) or (EN_NAME CN_NAME)"""
        brand = self.refine(brand)
        cn_name, en_name = brand, u''
        groups = self.en_sp.finditer(brand)
        for match in groups:
            en = match.group()
            if self.ex_sp.match(en):
                continue
            s, e = match.start(), match.end()
            if s == 0:
                cn = brand[e:]
            elif e == len(brand):
                cn = brand[:s]
            else:
                continue
            if len(cn) == 1:
                continue
            cn_name = cn
            en_name = en
            break
    
        cn_name = self.refine(cn_name)
        en_name = self.refine(en_name)
        return (cn_name, en_name)

    # 己知中文名，从名字中提取英文名
    def en_brand(self, cn_name, name):
        en_pattern = r'%s+?(.%s+?)*?' % (self.en_pa, self.en_pa)
        en_slash_a = r'%s/(?P<en1>%s)' % (cn_name, en_pattern)
        en_slash_b = r'(?P<en2>%s)/%s' % (en_pattern, cn_name)
        en_bracket_a = u'%s\\s*%s[（(](?P<en3>%s)[)）]' % (cn_name, self.brackets, en_pattern)
        en_bracket_b = u'(?P<en4>%s)\\s*%s[（(]%s[)）]' % (en_pattern, self.brackets, cn_name)
    
        en_cat = r'%s|%s|%s|%s' % (en_slash_a, en_slash_b, en_bracket_a, en_bracket_b)
        en_re = re.compile(en_cat)
    
        en_test = self.en_re.match(name)
        if en_test:
            en_name = filter(None, en_test.groups())[0]
        else:
            en_name = u''
        return en_name

    # 己知英文名，从名字中提取中文名
    def cn_brand(self, en_name, name):
    #   cn_slash_a = r'%s/(?P<en1>%s)' % (en_name, cn_pattern)
        cn_slash_b = r'(?P<en2>%s)/%s' % (self.cn_pattern, en_name)
        cn_bracket_a = u'%s\\s*%s[（(](?P<en3>%s?)[)）]' % (en_name, self.brackets, self.cn_pattern)
        cn_bracket_b = u'(?P<en4>%s?)\\s*%s[（(]%s[)）]' % (self.cn_pattern, self.brackets, en_name)
    
    #    cn_cat = r'%s|%s|%s|%s' % (cn_slash_a, cn_slash_b, cn_bracket_a, cn_bracket_b)
        cn_cat = r'%s|%s|%s' % (cn_slash_b, cn_bracket_a, cn_bracket_b)
        cn_re = re.compile(cn_cat)
    
        cn_test = self.cn_re.match(name)
        if cn_test:
            cn_name = filter(None, cn_test.groups())[0]
        else:
            cn_name = u''
        return cn_name





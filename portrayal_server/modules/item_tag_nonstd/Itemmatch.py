# -*- coding: utf8 -*-
# author:fangshu.chang
# modified by xiang.xu

import esm, json, sys, ConfigParser, logging

class Itemmatch():
    def __init__(self):
        self.cat_dic = dict()

    def init_category_esm(self, category, filename):
        if type(category) == unicode:
            category = category.encode('u8')

        if category not in self.cat_dic:
            self.cat_dic[category] = {'map': dict(), 'esmer': esm.Index()}

        self.init(category, filename)

    def init(self, category, filename):
        try:
            fp = open(filename,'r')
            logging.info("add tag resource %s" % category)
        except IOError:
            logging.error('could not open file:', filename)
            return 
        
        mapdict = self.cat_dic[category]['map'] 
        esmer = self.cat_dic[category]['esmer']       
        data = fp.readlines()
        for line in data:
            #这两个分隔符可以改变
            tmpd = line.strip().split("#BFD_TAG#")
            tmpdd = tmpd[1].split(",")
            for kw in tmpdd:
                mapdict[kw] = tmpd[0]
                esmer.enter(kw)
        esmer.fix()
        fp.close()
    
    #输入：string
    #输出：json字符串,结果可能为空字符串
    #文本提取标签
    def texttotag(self, text, category):
        if type(text) == unicode:
            text = text.encode('u8')
        if type(category) == unicode:
            category = category.encode('u8')

        result = "" 
        if category not in self.cat_dic:
            return result

        mapdict = self.cat_dic[category]['map']
        esmer = self.cat_dic[category]['esmer']

        tmplist = []
        tmpdict = {}
        tmpresult = esmer.query(text)
        if len(tmpresult) > 0:
            for i in range(len(tmpresult)):
                tmplist.append(mapdict[tmpresult[i][1]])
            tmplist = list(set(tmplist))
            for i in tmplist:
                tmpi = i.split("$")
                if tmpdict.has_key(tmpi[0]):
                    tmpdict[tmpi[0]].append(tmpi[1])
                else:
                    tmpdict[tmpi[0]] = []
                    tmpdict[tmpi[0]].append(tmpi[1])
            result = json.dumps(tmpdict,ensure_ascii=False)
        return result

if __name__ == '__main__':
    test = Itemmatch()
    test.init_category_esm('箱包', "resource/xiangbao.cfg")
    print test.texttotag(u"纯棉宝石蓝斜跨包男女通用", "箱包")
        

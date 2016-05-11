#encoding=utf-8
import re
import traceback

class PatternPool(object):
    def __init__(self, config_path=None, config_dict=None):
        '''
         正则表达式字典，键为名字，值为二元组(未展开的表达式字符串，Pattern对象)
          :dict( str -> (str, Pattern) )
        '''
        self.patterns = {}

        if config_path:
            try:
                with open(config_path, "r") as inputfile:
                    for line in inputfile:
                        idx = line.find("=")
                        if idx<0:
                            continue
                        name, patstr = line[:idx].strip(), line[idx+1:].strip()
                        self.patterns[name] = (patstr, None)
            except:
                raise Exception("file '%s' not found" % config_path)
        elif config_dict:
            for name in config_dict:
                self.patterns[name] = (config_dict[name], None)

        for name in self.patterns: #lazy compilation
            try:
                patstr, _ = self.patterns[name]
                self.patterns[name] = ( patstr, re.compile(self.flatten(patstr).decode("utf-8")) )
            except Exception as e:
                traceback.print_exc()
                raise Exception("pattern %s='%s' fail to compile\n%s" % (name,patstr,e))

    def flatten(self, pat):
        bracket = re.compile("{(.+?)}")
        return re.sub( bracket, 
                       lambda m: self.flatten(self.patterns.get(m.group(1))[0]), 
                       pat )

    def get(self, pat):
        return self.patterns.get(pat)[1]


config_dict = { 
    #数字
    "digit" : "[0-9一二三四五六七八九十零百千万亿]+(?:\.\d+)?",
    #单位
    "unit" : "(?:%|cm|kg|g|千克|克|斤|公斤|厘米|米|毫米|mm|ml|英尺|英寸|毫升|升|m|岁|个月|月)",
    #example: 20*20厘米
    "single-digit" : "{digit}({unit})?(?:[X*]{digit}({unit})?)*",
    #example: 7岁~9岁
    "interval-digit" : "({digit})({unit})?(?:[到至\-~]({digit})({unit})?|以上)"
}


class SpecialMatcher(object):

    def __init__(self):
        self.unit2key_map = {
            u"片": u"片数",
            u"岁" : u"年龄",
            u"月" : u"年龄",
            u"个月" : u"年龄",
            u"ml" : u"容量",
            u"g" : u"重量",
            u"kg" : u"重量",
            u"克" : u"重量"
        }
        self.pattern_pool = PatternPool(config_dict=config_dict)
        self.single_pattern = self.pattern_pool.get("single-digit")
        self.interval_pattern = self.pattern_pool.get("interval-digit")

    def match_single(self, s):
        m = self.single_pattern.search(s)
        if not m:
            return None
        if not m.group(1) and not m.group(2):
            return None
        if m.group(1)==u"月":
            return None
        else:
            return [m.group(0), m.group(1) if m.group(1) else m.group(2)]

    def match_interval(self, s):
        m = self.interval_pattern.search(s)
        if not m:
            return None
        if not m.group(2) and not m.group(4):
            return None
        else:
            return [m.group(0), m.group(1), m.group(3), m.group(2) if m.group(2) else m.group(4)]

    def match(self, text):
        result = {}
        text = text.lower()
        #搜索区间数值表达式, m1 = [ 匹配全文, 左值, 右值, 单位 ]
        #搜索非区间数值表达式, m2 = [ 匹配全文, 单位 ]
        m1 = self.match_interval(text)
        m2 = self.match_single(text)
        if m1:
            value, unit = m1[0], m1[3]
        elif m2:
            value, unit = m2[0], m2[1]
        else:
            value, unit = None, None
        if unit and unit in self.unit2key_map:
            result[ self.unit2key_map[unit] ] = value
        return result
            
            
if __name__=="__main__":
    matcher = SpecialMatcher()
    for k,v in matcher.match(u"200g").items():
        print k, " : ", v

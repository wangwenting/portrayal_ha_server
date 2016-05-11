#!usr/bin/evn python
#-*- coding=utf8 -*-
import sys, json, logging, re, traceback
import elasticsearch
import ConfigParser

class ESClient(object):
    def __init__(self, cfg_filename):
        self.config=ConfigParser.ConfigParser()
        self.cfgParser(cfg_filename)
        self.es=elasticsearch.Elasticsearch([{'host':self.host,'port':self.port}], timeout=self.timeout)
        
        self.symbol={"0":u"\(|\)|（|）|\s", "1":u"[^a-zA-Z0-9\u4e00-\u9fa5\.\+\-]"}
        self.clearre=re.compile(self.symbol["1"])

    def cfgParser(self,cfg_path):
        self.config.read(cfg_path)
        if self.config.has_option("ElasticSearch", "host"):
            self.host=self.config.get("ElasticSearch", "host")
        else:
            print("host 没有设置")
            exit(1)
        if self.config.has_option("ElasticSearch", "port"):
            self.port=self.config.getint("ElasticSearch", "port")
        else:
            print("port 没有设置")
            exit(1)
        if self.config.has_option("ElasticSearch", "timeout"):
            self.timeout=self.config.getint("ElasticSearch", "timeout")
        else:
            print("timeout 没有设置")
            exit(1)
        if self.config.has_option("ElasticSearch", "index_name"):
            self.index_name=self.config.get("ElasticSearch", "index_name")
        else:
            print("index_name 没有设置")
            exit(1)
        if self.config.has_option("ElasticSearch", "type_name"):
            self.type_name=self.config.get("ElasticSearch", "type_name")
        else:
            print("type_name 没有设置")
            exit(1)
        if self.config.has_option("ElasticSearch", "filed_name"):
            self.filed_name=self.config.get("ElasticSearch", "filed_name")
        else:
            print("filed_name 没有设置")
            exit(1)


    def create_index(self, filename):
        filein=open(filename, "r")
        data = filein.readlines()

        actiondict={}
        metadict={}
        metadict["_index"] = self.index_name
        metadict["_type"] = self.type_name
        actiondict["index"]= metadict

        contentdict={}

        body_lst = []
        i = 0
        for item in data:
            content = item.strip().split("\t:")[1]
            dd = json.loads(content)
            contentdict["title"] = dd["name"].replace(u"参数",u"").strip()
            contentdict["attr_str"] = json.dumps({"name":dd["name"],"attr":dd["attr"],"url":dd["url"]},ensure_ascii=False)
            body_lst.append(json.dumps(actiondict))
            body_lst.append(json.dumps(contentdict, ensure_ascii=False))
            #body=body+json.dumps(actiondict)+"\n"+json.dumps(contentdict,ensure_ascii=False)+"\n"
            #print json.dumps(dd,ensure_ascii=False)
            #print body
            i += 1
            if i%1000 == 0:
                try:
                    body = u'\n'.join(body_lst) + u'\n'
                    self.es.bulk(index=self.index_name, doc_type=self.type_name, body=body)
                except Exception, e:
                    logging.error(e)
                    logging.error("数据未写入：%d records", len(body_lst)/2)
                    #logging.error("数据未写入：%s", body.encode('u8'))
                body_lst = []
                print i

        try:
            body = u"\n".join(body_lst) + u"\n"
            print type(body)
            self.es.bulk(index=self.index_name, doc_type=self.type_name, body=body)
        except Exception, e:
            traceback.print_exc()
            logging.error(e)
            logging.error("数据未写入：%d records", len(body_lst)/2)
            #logging.error("数据未写入：%s", body.encode('u8'))
        print "cfs", i

    # 输入：商品标题，string类型
    # 格式：普通文本
    # 输出：产品信息，string类型
    # 格式：json格式
    # 输出：匹配得分，float类型
    # 功能：通过商品标题对商品打标签
    # 匹配失败，返回"{}"
    def commodity2product(self, strTitle):
        resultdict = {}
        strTitle = self.char_code(strTitle.strip())
        strTitle = self.clear(strTitle)
        results = self.es.search(self.index_name, self.type_name, {"query":{"query_string":{"default_field":self.filed_name,"query":strTitle}}})
        #for a in results["hits"]["hits"]:
        #    print a["_score"]
        #    print a["_source"]["title"].encode('u8')
        #    print "*****"        

        if results["hits"]["total"] > 0:
            score=results["hits"]["hits"][0]["_score"]
            resultdict["name"] = results["hits"]["hits"][0]["_source"][self.filed_name]
            resultdict["attr_str"] = json.loads(results["hits"]["hits"][0]["_source"]["attr_str"])["attr"]
            if score > 20:
                return json.dumps(resultdict,ensure_ascii=False)
            else:
                return json.dumps(resultdict,ensure_ascii=False) if self.special_process(strTitle, results["hits"]["hits"][0]["_source"][self.filed_name]) else "{}"
        else:
            return "{}"

    def special_process(self, strTitle, strProductTitle):
        #将strTitle中的非英文字符和数字的其他字符替换为空格，即只保留引文字符和数字
        tmpstr = re.sub(u"[^a-zA-Z0-9]", u" ", strTitle.upper())
        tmplist1 = tmpstr.split()
        #将strProductTitle中的带有括号（包括中文和英文）中的内容替换为空格
        tmp2 = re.sub(u"[\(\uff08][\w\W]*[\)\uff09]", u" ", strProductTitle.upper())
        #将strProductTitle中的非英文字符和数字的其他字符替换为空格，即只保留引文字符和数字
        tmp3 = re.sub(u"[^a-zA-Z0-9]", u" ", tmp2)
        tmplist2 = tmp3.split()

        if len(tmplist2) == 1 and len(set(tmplist2))+len(set(tmplist1)) > len(set(tmplist2).union(set(tmplist1))):
            return True
        elif len(set(tmplist2))+len(set(tmplist1)) > len(set(tmplist2).union(set(tmplist1)))+1:
            return True
        else:
            return False

    def clear(self, text):
        return self.clearre.sub(u" ", text)

    @staticmethod
    def char_code(text):
        if not isinstance(text, unicode):
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                text = text.decode('gbk', 'ignore')
        return text

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s create <data-file>" %sys.argv[0]
        sys.exit()

    es_client = ESClient('elasticsearch.cfg')
    if sys.argv[1] == 'create':
        es_client.create_index(sys.argv[2])

    elif sys.argv[1] == 'search':
        res = es_client.commodity2product(u"三星A817")
        print res


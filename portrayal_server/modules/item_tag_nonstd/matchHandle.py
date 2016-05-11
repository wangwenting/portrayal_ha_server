#encoding=utf-8
import sys
import re
import traceback
import json
reload(sys)
sys.setdefaultencoding("utf-8")

def matchhandle(result, title, catename):
    try:
        if catename == "医疗保健".decode('utf-8'):
            matchpian(result, title)
        if catename == "箱包".decode('utf-8'):
            matchsize(result, title)
        if catename == "出差旅游".decode('utf-8'):
            matchpian(result, title)
        result = filterinclude(result)
    except Exception as e:
        print e
    return result


#match规格:片 -- 医疗保健
#title中包含"片 ",才确定其产品类型是"片"
def matchpian(result, title):
    key = "产品类型".decode("utf-8")
    item = "片".decode("utf-8")
    if title.find(item)==-1 or result.has_key(key)==False or item not in result[key]:
        return result
    else:
        if title.find("片 ".decode("utf-8"))==-1:
            result[key].remove(item)
        if len(result[key])==0:
            result.pop(key)
        

#"男用"->"男"; "女用"->"女" ;"色红"->"红色" -- 所有品类
def matchother(result, title):
    key = "适合人群".decode("utf-8")
    values = []
    if title.find("男用".decode("utf-8"))!=-1:
       values.append("男".decode("utf-8"))
    if title.find("女用".decode("utf-8"))!=-1:
       values.append("女".decode("utf-8"))
    if title.find("孕妇首选".decode("utf-8"))!=-1 or title.find("孕妇零食".decode("utf-8"))!=-1:
       values.append("孕妇".decode("utf-8"))
    if len(values)>0:
        if result.has_key(key):
            result[key] = result[key] + values
        else:
            result[key] = values
    key = "颜色".decode("utf-8")
    values = []
    if title.find("色红".decode("utf-8"))!=-1:
       values.append("红色".decode("utf-8"))
    if len(values)>0:
        if result.has_key(key):
            result[key] = result[key] + values
        else:
            result[key] = values
    
#匹配尺寸标签--箱包
def matchsize(result, title):
    key = "尺寸".decode("utf-8")
    sizelist = ["寸"]
    values = []
    for v in sizelist:
        res = re.findall("\d[\d\/\-]*"+v.decode("utf-8"),title)
        if len(res)>0:
            values += res
    if len(values)>0:
        if result.has_key(key):
            result[key] = result[key] + values
        else:
            result[key] = values

#匹配床型:单人床--出差旅游
def matchbedtype(result, title):
    key = "床型".decode("utf-8")
    houses = ["标准间","标准房","双人房","双人间","双床房","单人间","单人房","三人间","三人房","双标间"]
    values = []
    for v in houses:
        if title.find(v)>=0:
            values.append("单人床".decode("utf-8"))
            break
    if len(values)>0:
        if result.has_key(key):
            result[key] = result[key] + values
        else:
            result[key] = values


#去除包含的属性值，如["玫红色","红色"]转变成["玫红色"]--所有品类
def filterinclude(result):
    res = {}
    for k in result:
        res[k]=[]
        if len(result[k])==1:
            res[k]=result[k]
        else:
            l = result[k]
            for i in range(0,len(l)):
                isadd = True
                for j in range(0,len(l)):
                    if i!=j:
                        if l[j].find(l[i])!=-1:
                            isadd = False
                            break
                if isadd:
                    res[k].append(l[i])
    return res



if __name__=="__main__":
    r={}
    r["适用人群".decode('utf-8')]=["女士".decode('utf-8'),"女".decode('utf-8')]
    print json.dumps(filterinclude(r), ensure_ascii=False)

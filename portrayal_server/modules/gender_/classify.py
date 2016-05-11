# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from wordAnalysis import WordAnalysis
import predicts
import jieba

def cut(string):
    #cuter = WordAnalysis()
    #return cuter.splitWords(string.strip('\n')).split('\t')
    return list(jieba.cut(string.strip()))

def base_classify(context,thres):
    words = cut(context)
    gender = predict.predict_line(' '.join(words),'l1_base_model',thres)
    return gender[0]

def category_classify(line,separate,thres):
    cates = line.split(separate)
    for cate in cates:
        gender = base_classify(cate,thres)
        if str(gender) == str('0'):
            continue
        return gender
   
def test(input_file,thres):
    real = []
    predict = []
    for line in open(input_file):
        chunks = line.strip('\n').split('\t')
        if len(chunks) < 2 or (chunks[1] != '0' and chunks[1] != '1' and chunks[1] != '-1'):
            continue
        real.append(chunks[1])
        _p = category_classify(chunks[0],'$',thres)
        if _p == None:
            _p = '0'
        predict.append(_p)
    return real,predict

def computing(real,predict):
    male_real = 0
    female_real = 0
    p_f = 0
    error = 0
    for i in range(len(real)):
        if real[i] != predict[i]:
            error += 1
        if str(real[i]) == '1':
            male_real += 1
        if str(real[i]) == '-1':
            female_real += 1
            
        if str(predict[i]) != '0':
            p_f += 1
    return (float(male_real + female_real) / len(real)),float(float(error) / len(real)),float(float(p_f) / len(real))
if __name__ == '__main__':
    real,predict = test(sys.argv[1],float(sys.argv[2]))
    real_f, precise, p_f = computing(real,predict)
    print real_f,precise,p_f

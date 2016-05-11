#!usr/bin/python
# coding=utf8

from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn import metrics
import numpy as np
import sys
sys.path.append('/opt/bre/dai.xu/gender/code')
from readfile import *
try:
    import cPickle as pickle
except:
    import pickle

def open_model(model_path):
    fp = open(model_path,'r')
    clf = pickle.load(fp)
    count_vect = pickle.load(fp)
    fp.close()
    return clf,count_vect

def __predict_line__(line, model_path,thres):
    clf,count_vect = open_model(model_path)
    X = count_vect.transform([line])
    predicted = clf.predict_proba(X).tolist()
    return predict_with_threshold(predicted,thres)

def get_data(test_path,has_id,has_gender):
    if has_id and has_gender:
        test_id,test_label,test_data = read_test_data(test_path,has_id,has_gender)
        return test_data,test_id,test_label
    elif has_id:
        test_id,test_data = read_test_data(test_path,has_id,has_gender)
        return test_data,test_id,False
    elif has_gender:
        test_label,test_data = read_test_data(test_path,has_id,has_gender)
        return test_data,False,test_label
    else:
        test_data = read_test_data(test_path,has_id,has_gender)
    return test_data,False,False

def predict_base_model(clf,count_vect,test_data,thres):
    X_test_counts = count_vect.transform(test_data)
    #print 'length of test data : ' + str(len(test_data))
    predicted = clf.predict_proba(X_test_counts)
    predicted = predicted.tolist()
    #print predicted
    predicted = predict_with_threshold(predicted,thres)
    return predicted

def predict_base_rule(test_data,rule_path='./rules'):
    hed,pos,neg = get_gender_rules(rule_path)
    predict_rule = predict_based_rules(test_data,hed,pos,neg)
    return predict_rule

def statistics(predict,label):
    print 'length is:',len(predict)
    predict = np.array(predict)
    label = np.array(label)
    print "The predicted accuracy : "+"%.2f%%" % (100*(np.mean(predict == label)))
    num = 0.0
    for item in predict:
        if item != '0':
            num += 1.0
    print 'proportion of labeled is ' + str(num/float(len(predict)))

    male = 0.0
    female = 0.0
    none = 0.0
    for index in range(len(label)):
        if label[index] == '1': male += 1
        elif label[index] == '-1':  female += 1
        else:   none +=1
    print 'label:male and female and none:',male/len(label),female/len(label),none/len(label)

    _male, _female, _none = 0.0, 0.0, 0.0
    for index in range(len(predict)):
        if predict[index] == '1':   _male += 1
        elif predict[index] == '-1':  _female += 1
        else:   _none += 1
    print _male+_female+_none , len(predict)
    print 'predict:male and female and none:',_male/len(predict),_female/len(predict),_none/len(predict)

def debug_model(model_path):
    model, vacab = open_model(model_path)
    for v in vacab.vocabulary_:
        print v,
    print '\n',len(vacab.vocabulary_)

def debug_rule(test_path,has_id,has_gender):
    test_data,test_id,test_label = get_data(test_path,has_id,has_gender)
    predict = predict_base_rule(test_data, rule_path='./rules')
    if len(predict) != len(test_label):
        print 'length error'
        exit()
    print "The rules predicted accuracy : "+"%.2f%%" % (100*(np.mean(np.array(predict) == np.array(test_label))))
    #for index in range(len(predict)):
    #    print predict[index] + '\t' + test_data[index]
    #exit()
    #print test_label
    right = 0
    length = 0
    error = 0
    for index in range(len(predict)):
        if predict[index] != '0':
            length += 1
            if predict[index] == test_label[index]:
                right += 1
            else:
                error += 1
                print test_data[index],predict[index],test_label[index]
    print 'error:',error
    print 'rules accuracy is:',float(right) / float(length)
    statistics(predict,test_label)

def predict_line(test_data, clf, count_vect, threshold, rule_path='./rules'):
    _predict = predict_base_rule(test_data, rule_path)
    if _predict != '0':
        return _predict
    return predict_base_model(clf,count_vect,test_data,threshold)
    
def predict(test_path,model_path,has_id,has_gender,threshold):
    test_data,test_id,test_label = get_data(test_path,has_id,has_gender)
    clf,count_vect = open_model(model_path)
    predicts = []
    model_change = 0
    predicts = predict_base_model(clf,count_vect,test_data,threshold)
    for index in range(len(predicts)):
        predict = predict_base_rule([test_data[index]],rule_path='./rules')[0]
        if predict != '0':
            predicts[index] = predict
        if predict == '0' and predicts[index] != '0':
            model_change += 1
    print 'model changes:',model_change

    if test_label != False:
        for i in range(len(predicts)):
            if predicts[i] != test_label[i]:
                print test_data[i],predicts[i],test_label[i]
        statistics(predicts,test_label)
    else:
        statistics(predicts,predicts)

    return test_id,predicts

if __name__ =='__main__':

    sys_argc = len(sys.argv)
    has_id = False
    has_gender = False


    test_path = './test_cate.dat'
    model_path = './models/model'
    threshold = 0.0

    if sys.argv[1] == 'debug':
        debug(sys.argv[2])
        exit()

    if sys_argc==1:
        test_path = "./test_cate.dat"
    elif sys_argc==2:
        test_path=sys.argv[1]
    elif sys_argc==3:
        test_path = sys.argv[1]
        has_id = ('True'==sys.argv[2])
    elif sys_argc==4:
        test_path = sys.argv[1]
        has_id = ('True'==sys.argv[2])
        has_gender=('True'==sys.argv[3])
    elif sys_argc==5:
        test_path = sys.argv[1]
        has_id = ('True'==sys.argv[2])
        has_gender=('True'==sys.argv[3])
        model_path = sys.argv[4]
    elif sys_argc==6:
        test_path = sys.argv[1]
        has_id = ('True'==sys.argv[2])
        has_gender=('True'==sys.argv[3])
        model_path = sys.argv[4]
        threshold = float(sys.argv[5])
    else:
        print 'wrong command arguments!'

    #debug_rule(test_path,has_id,has_gender)
    test_ids, predicts = predict(test_path,model_path,has_id,has_gender,threshold)
    #print predicts
    #writer = open('predict_category.dat','w')
    #for i in range(len(test_ids)):
    #    writer.write(test_ids[i] + '\t' + predicts[i] + '\n')
    #writer.close()

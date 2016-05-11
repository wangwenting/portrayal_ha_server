#!usr/bin/python
# -*- coding: utf-8 -*-

import re

def read_test_data(path,has_cid,has_gender):
    cid = list()
    data = list()
    label = list()

    try:
        fp = open(path,'r')
    except IOError:
        print 'could not open file:',path
        return
    line = fp.readline()
    NUM = 0
    while line:
        NUM += 1
        line = line.strip('\n').strip('\t')
        if has_gender and has_cid:
            l = line.split('\t',2)
            if len(l)<=2:
                l2 = 'unknown'
                #print NUM
            else:    
                l2 = l[2]
            cid.append(l[0])
            label.append(l[1])
            data.append(l2)
        elif has_cid:
            l = line.split('\t',1)
            if len(l)<=1:
                l1 = 'unknown'
                #print NUM
            else:
                l1 =l[1]
            cid.append(l[0])
            data.append(l1)
        elif has_gender:
            l = line.split('\t',1)
            if len(l)<=1:
                l1 = 'unknown'
                #print NUM
            else:
                l1 = l[1]
            label.append(l[0])
            data.append(l1)
        else:
            data.append(line)
        line = fp.readline()

    fp.close()
    if has_gender and has_cid:
        return cid,label,data
    elif has_cid:
        return cid,data
    elif has_gender:
        return label,data
    else:
        return data
def occur_all(sample,term_list):
    for pos in range(len(term_list)):
        if sample.find(term_list[pos])==-1:
            return False
    return True

def occur_one(sample,term_list):
    
    if len(term_list)==0:
        return True
    for term in term_list:
        if sample.find(term)!=-1:
            return True
    return False

def get_gender_rules(file):
    
    rules_pos = []
    rules_neg = []
    rules_hed = []
    for line in open(file,'r'):
        rule_pos = []
        rule_neg = []
        l  = line.strip('\n').split('    ')
        if len(l)>1:
            rules_hed.append(l[0])
            for term in l[1:]:
                if term.find('-')!=-1:
                    rule_neg.append(term.replace('-','').replace('{','').replace('}',''))
                else:
                    rule_pos.append(term.replace('{','').replace('}',''))
            rules_pos.append(rule_pos)
            rules_neg.append(rule_neg)

    return rules_hed,rules_pos,rules_neg

def predict_onesample_based_rules(line,rules_hed,rules_pos,rules_neg):
    satisfy_rule = True
    for pos in range(len(rules_hed)):
        satisfy_rule = True
        for rule in rules_pos[pos]:
            rule = rule.strip()
            if not occur_one(line,rule.split(' ')):
                satisfy_rule = False
                break
        if not satisfy_rule:
            continue
        for rule in rules_neg[pos]:
            rule = rule.strip()
            if len(rule) and occur_one(line,rule.split(' ')):
                satisfy_rule = False
                break
        if satisfy_rule:
            if rules_hed[pos] == '男':
                return '1'
            elif rules_hed[pos]=='女':
                return '-1'
            else:
                return '0'
    if not satisfy_rule:
        return '0'

def  predict_based_rules(data,rules_hed,rules_pos,rules_neg):
    
    gender = []
    for sample in data:
        gender.append(predict_onesample_based_rules(sample,rules_hed,rules_pos,rules_neg))
    return gender
'''
def write_table(path):
    hed,pos,neg = get_gender_rules(path)
    conn = MySQLdb.connect('192.168.24.45','bfdroot','qianfendian','word_backup',charset='utf8')
    cur = conn.cursor()
    for i in range(len(pos)):
        sql_content = ''
        if len(pos[i])>1:
            if len(neg[i])==0:
                sql_content = "insert into rule_rule(gender,include,include_attr,exclude_attr) values(%s,%s,%s,%s);" \
                %(hed[i],pos[i][0],pos[i][1],'')
            else:

                sql_content = "insert into rule_rule(gender,include,include_attr,exclude_attr) values(%s,%s,%s);" \
                %(hed[i],pos[i][0],pos[i][1],neg[i][0])
        else:
            if len(neg[i])==0:
                sql_content = "insert into rule_rule(gender,include,include_attr,exclude_attr) values(%s,%s,%s,%s);" \
                %(hed[i],pos[i][0],'','')
            else:
                sql_content = "insert into rule_rule(gender,include,include_attr,exclude_attr) values(%s,%s,%s,%s);" \
                %(hed[i],pos[i][0],'',neg[pos][0])
        cur.execute(sql_content)

write_table('./rules')
'''
def  split_single_word(lin):
    words = ''
    regex=re.compile("(?x) ( [\w-]+ | [\x80-\xff]{3} )")
    for w in regex.split(lin):
        if len(w)==3:
            words += w
            words += ' '
    return words
def read_word_from_source(path):
    data = list()
    label = list()
    try:
        fp = open(path,'r')
    except IOError:
        print 'could not open file:',path
    line = fp.readline()
    nums = 0
    while line:
        line = line.strip('\n')
        line = line.strip('\t')
        l = line.split(' ',1)
        label.append(l[0])
        newline = split_single_word(l[1])
        data.append(newline)
        nums += 1
        line = fp.readline()
    return data,label,nums
def readchange_merged_data(path):
    data=list()
    label=list()
    nums = 0
    k = 0
    m = 0
    try:
        fp = open(path,'r')
    except IOError:
        print 'could not open file:',path
    #line = fp.readline()
    for line in fp:
        line = line.strip('\n')
        l=line.split('\t',2)
        if line.find('男')!=-1 and line.find('女')==-1 and l[1].find('-1')!=-1:
            l[1].replace('-1','1')
            nums += 1
        if line.find('男')==-1 and line.find('女')!=-1 and l[1].find('-1')==-1:
            l[1].replace('1','-1')
            nums += 1

        if l[1]!='-1' and l[1]!='1':
            k += 1
        if len(l)==3:
            data.append(l[2])
            label.append(l[1])
        else:
            m += 1
            continue
        #line = fp.readline()
    fp.close()
    print '非男女数目:',k
    print '不合法数据:',m
    return data,label,nums

def readchange_predicted_data(path,predicted):

    nums = 0
    pos = 0
    fp = open(path,'r')
    line = fp.readline()
    while line:
        if line.find('男')!=-1 and line.find('女')==-1 and predicted[pos]=='-1':
            predicted[pos]='1'
            nums += 1
        if line.find('男')==-1 and line.find('女')!=-1 and predicted[pos]=='1':
            predicted[pos]='-1'
            nums += 1
        pos += 1
        line = fp.readline()

    fp.close()
    return predicted,nums

def print_error_data(path_src,path_dst,predicted):
    fp = open(path_dst,'w')
    pos = 0
    for line in open(path_src,'r'):
        l = line.split('\t',1)
        if predicted[pos]=='1':
            gender = '男'
        elif predicted[pos]=='-1':
            gender = '女'
        else:
            gender = '中性'
        if l[0]!=predicted[pos]:
            newline =  gender + '\t'+line
            fp.write(newline)
        pos += 1
    fp.close()

def print_all_info(path_src,path_dst,predicted):
    fp = open(path_dst,'w')
    pos = 0
    for line in open(path_src,'r'):
        l = line.split('\t')
        if predicted[pos]=='1':
            gender = '1'
        elif predicted[pos]=='-1':
            gender = '-1'
        else:
            gender = '0'
        if len(l)==3:
            newline = l[0]+ '\t'+gender + '\t' +l[2]+ '\n'
        if len(l)==2:
            newline = l[0]+'\t'+gender+'\t'+l[1]+'\n'
        
        if gender =='1' or gender =='-1':
            fp.write(newline)
        pos += 1
    fp.close()

def print_recognized_results(path_src,predicted,has_id,has_gender,path_male,path_female,path_none):
    fpmale = open(path_male,'w')
    fpfemale = open(path_female,'w')
    fpnone = open(path_none,'w')

    pos = 0
    num_male = 0
    num_female = 0
    num_none = 0

    count_male = 0
    count_female = 0
    count_none = 0
    for line in open(path_src,'r'):
        if predicted[pos]=='1':
            gender = '1'
            num_male += 1
        elif predicted[pos]=='-1':
            gender = '-1'
            num_female += 1
        else:
            gender = '0'
            num_none += 1
        ''' 
        l = line.split('\t',2)
        if predicted[pos]=='1' and l[1]=='1':
             count_male += 1
        if predicted[pos] =='-1' and l[1]=='-1':
            count_female += 1
        if predicted[pos]=='0' and l[1]=='0':
            count_none += 1
        '''
        if has_id and has_gender:
            l = line.split('\t',2)
            newline = l[0] +'\t'+ l[1] +'\t'+gender+'\t'+l[2] 
        elif not has_id and not has_gender:
            l = line
            newline = gender + '\t' + l[1]
        
        else:
            l = line.split('\t',1)
            newline = l[0]+'\t'+gender+'\t'+l[1]
         
        if predicted[pos]=='1':
            fpmale.write(newline)
        elif predicted[pos]=='-1':
            fpfemale.write(newline)
        else:
            fpnone.write(newline)
        
        pos += 1
    
        #print pos

    print 'recognized male:',num_male,count_male
    print 'recognized female:',num_female,count_female
    print 'recognized none:', num_none,count_none
    fpmale.close()
    fpfemale.close()
    fpnone.close()
    return num_male,num_female,num_none



def predict_with_threshold(predicted_prob,thres=1.0):
    predicted = []
    for pos in range(len(predicted_prob)):
        if predicted_prob[pos][0] > predicted_prob[pos][1]  and predicted_prob[pos][1]/predicted_prob[pos][0]<=thres:
            predicted.append('-1')
           # print '-1\t' + str(predicted_prob[pos][0])+'\t' + str(predicted_prob[pos][1])
        elif predicted_prob[pos][1] >= predicted_prob[pos][0] and predicted_prob[pos][0]/predicted_prob[pos][1]<=thres:
            predicted.append('1')
            #print '1\t'+str(predicted_prob[pos][0]) + '\t' + str(predicted_prob[pos][1])
        else:
            predicted.append('0')
            #print '0\t'+str(predicted_prob[pos][0]) + '\t' + str(predicted_prob[pos][1])




    return predicted

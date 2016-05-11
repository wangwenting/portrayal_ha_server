#coding=utf8

import MySQLdb
import sys, os, re, json

alg_1 = '192.168.24.45' 
user = 'bfdroot'
passwd = 'qianfendian'
db0 = 'word_backup'

cxn = MySQLdb.connect(host=alg_1, user=user, passwd=passwd, db=db0, charset='utf8')
cxn.autocommit(True)
cur0 = cxn.cursor()

def insert2table(filename, table2):
    sql_in = "insert ignore into %s(word) values(%%s)" % table2
    rows = file2word(filename)
    cur0.executemany(sql_in, rows)

def file2word(filename):
    words = []
    with open(filename, "r") as f:
        for line in f:
            word = line.strip()
            words.append( (word,) )
    return words

def main():
    filename = sys.argv[1]
    table2 = sys.argv[2]
    insert2table(filename, table2)

if __name__ == "__main__":
    main()

cur0.close()
cxn.close()

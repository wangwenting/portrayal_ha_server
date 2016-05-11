# -*- coding: utf-8 -*-
import sys, json, logging, datetime, time, os
from math import pow, log
import cPickle
from operator import attrgetter, itemgetter
#import MySQLdb
import traceback

from classify import Category, ClassifierWrap, MyPipeline

from multiprocessing import Process, Queue
import multiprocessing

cur_dir = os.path.dirname(os.path.abspath(__file__))

alg_test0 = "192.168.24.56"


dat_old = 'out/classif.dat'
dat_yiyao = 'out/classif_yiyao.dat'

clf_old = ClassifierWrap()
clf_yiyao = ClassifierWrap()

clf_old.load(dat_old)
root = clf_old.find_cat([])

cat_id = {}

def get_cat_id(cat):
    name_str = u"$".join(cat.names)
    cat_id[name_str] = cat.id
    for c in cat.children:
        get_cat_id(c)

def output_cat_id():
    filename = sys.argv[1]
    get_cat_id(root)
    print filename, len(cat_id)
    with open(filename, "w") as f:
        for cat, id in cat_id.iteritems():
            line = u"%s\t%s\n" % (cat, id)
            f.write( line.encode("u8") )

def main():
    output_cat_id()

if __name__ == "__main__":
    main()

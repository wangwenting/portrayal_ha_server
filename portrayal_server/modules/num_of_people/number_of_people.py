# -*- coding: utf-8 -*-
import re
import traceback
import logging
from portrayal_server.modules.module import Module

ch_to_num = {
    u'单': 1,
    u'双': 2,
    u'二': 2,
    u'两': 2,
    u'三': 3,
    u'四': 4,
    u'五': 5,
    u'六': 6,
    u'七': 7,
    u'八': 8,
    u'九': 9,
    u'十': 10,
    u'多': 100
}


class NumberOfPeople(Module):

    def __init__(self, context):
        super(NumberOfPeople, self).__init__(context)
        self.pat = re.compile(u'(?:(?P<c>\d+)|(?P<ch>[单双二两三四五六七八九十多]))[人|床]')

    def extract_people(self, text):
        if not isinstance(text, unicode):
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                text = text.decode('gbk', 'ignore')

        m = self.pat.search(text)
        num = 1
        if m:
            if m.group('c'):
                num = int(m.group('c'))
            elif m.group('ch'):
                num = ch_to_num.get(m.group('ch'), None)
            if num > 100:
                num = 1
        if num == 1 and text.find(u'情侣') != -1:
            num = 2
        return num

    def __call__(self, item_base, item_profile):
        try:
            name = item_base.get("name", "")
            item_profile["num_of_people"] = self.extract_people(name)
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("number_of_people: %s", e)
        return {"status": 0}

if __name__ == "__main__":
    plugin = NumberOfPeople("None")
    print(plugin.extract_people(u"二人"))

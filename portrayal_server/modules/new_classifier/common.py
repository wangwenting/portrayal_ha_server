# -*- coding: utf-8 -*-
import re


def extract_sentence(text):            
    text = text.replace(u'斜跨包', u'斜挎包').replace(u'!', u',').\
        replace(u'！', u',').replace(u'。', u',').replace(u'，', u',').\
        replace(u'市场价', u'').replace(u'全国包邮', u'').replace(u'包邮', u'').\
        replace(u'【', u'').replace(u'】', u'').replace(u'[', u'').replace(u']', u'')
    text = re.sub(u'仅[0-9.]*元', u'', text)
    text = re.sub(u'仅售[0-9.]*元', u'', text).replace(u'仅售', u'')
    sentences = text.split(u',')
    if len(sentences) < 4:
        return text
    results = []
    for sentence in sentences:
        results.append(sentence)
        if len(sentence.encode('utf-8')) > 45:
            break
    if (text.find(u'女') != -1 or text.find(u'裙') != -1 or text.find(u'美腿') != -1) and text.find(u'男') == -1:
        results.append(u'女')
    elif text.find(u'男') != -1 and (text.find(u'女') == 1 and text.find(u'裙') == -1 and text.find(u'美腿') == -1 ):
        results.append(u'男')
    return u' '.join(results)

#!/usr/bin/env python

import sys
import json
import urllib2
import md5
import random
import httplib
import urllib

"""
dict - Chinese/English Translation
@author jianvhen
@date   2018-05-28
"""


class Dict:

    appKey = '0163ab68a66042e5'
    secretKey = 'cMFWpEj6jXZQCOolQkUB0Wsc4WBnvzds'
    httpClient = None
    myurl = '/api'
    fromLang = 'EN'
    toLang = 'zh-CHS'
    content = None

    def __init__(self, argv):
        if len(argv) < 1:
            print "need one argument"
            sys.exit(0)

        q = urllib.quote(argv[0])
        salt = random.randint(1, 65536)
        sign = self.appKey+q+str(salt)+self.secretKey
        m1 = md5.new()
        m1.update(sign)
        sign = m1.hexdigest()
        api = self.myurl+'?appKey='+self.appKey+'&from='+self.fromLang+'&to='+self.toLang+'&salt='+str(salt)+'&sign='+sign+'&q='

        if len(argv) == 1:
            self.api = api + urllib.quote(argv[0])
            self.translate()
        else:
            print 'only need one argument'

    def translate(self):
        httpClient = httplib.HTTPConnection('openapi.youdao.com')
        httpClient.request('GET', self.api)
        self.content = json.loads(httpClient.getresponse().read())
        self.parse()

    def parse(self):
        code = int(self.content['errorCode'])
        if code == 0:  # Success
            try:
                u = self.content['basic']['us-phonetic']
                e = self.content['basic']['uk-phonetic']
                explains = self.content['basic']['explains']
            except KeyError:
                u = 'None'
                e = 'None'
                explains = 'None'
            print '\033[1;31m################################### \033[0m'
            print '\033[1;31m# \033[0m', self.content['query'], self.content['translation'][0], '(U:', u, 'E:', e, ')'
            if explains != 'None':
                for i in range(0, len(explains)):
                    print '\033[1;31m# \033[0m', explains[i]
            else:
                print '\033[1;31m# \033[0m Explains None'
            print '\033[1;31m################################### \033[0m'
        elif code == 20:  # Text to long
            print 'WORD TO LONG'
        elif code == 30:  # Trans error
            print 'TRANSLATE ERROR'
        elif code == 40:  # Don't support this language
            print 'CAN\'T SUPPORT THIS LANGUAGE'
        elif code == 50:  # Key failed
            print 'KEY FAILED'
        elif code == 60:  # Don't have this word
            print 'DO\'T HAVE THIS WORD'

if __name__ == '__main__':
    Dict(sys.argv[1:])

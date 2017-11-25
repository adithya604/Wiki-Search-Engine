#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.sax
import helperFunctions as hf
from time import time
from collections import defaultdict
import collections
import json
import sys

#sys.setdefaultencoding('utf8')

indexDict = defaultdict(str)

#if len(sys.argv) < 


class WikiParser(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.isDocId = False
        self.docId = ""
        self.isTitle = False
        self.title = defaultdict(int)
        self.titleName = ""
        self.isText = False
        self.references = defaultdict(int)
        self.externalLinks = defaultdict(int)
        self.categories = defaultdict(int)
        self.infobox = defaultdict(int)
        self.body = defaultdict(int)
        self.text = ""
        self.path = []
        self.parent = ""
        self.docCount = 0

    def getParent(self):
        if len(self.path) == 0:
            return  None
        else:
            return self.path[-1]

    def startElement(self, name, attrs):
        self.parent = self.getParent()

        if name == "id" and self.parent == "page":
            self.isDocId = True
            #sys.stdout.write('<%s> <%s>\n' %(name, self.parent))
            self.docCount = self.docCount + 1
            
        if name == "title":
            self.isTitle = True
        if name == 'text':
            self.isText = True
        self.path.append(name)

    def characters(self, content):
        if self.isDocId:
            self.docId = content
            #print(content)
        if self.isTitle:
            self.titleName += content
        if self.isText:
            self.text += content

    def endElement(self, name):
        if name == "id" and self.parent == "page":
            self.isDocId = False

        if name == "title":
            self.title = hf.parseTitle(self.titleName)
            self.isTitle = False

        if name == 'text':
            self.references, self.externalLinks, \
                        self.categories, self.infobox, self.body = hf.parseText(self.text)
            self.isText = False

        if name == 'page':
            print(self.docId)
            print("title ", self.title)
            '''print("references", self.references)
            print("external links ", self.externalLinks)
            print("Categories ", self.categories)
            print("Infobox Content ", self.infobox)
            print("Body : ",self.body)
'''
            indexer(self.docId, self.title, self.body, self.infobox, self.references, self.externalLinks, self.categories)

            self.docId = ""
            self.title.clear()# = defaultdict(int)
            self.titleName = ""
            self.references.clear() # = defaultdict(int)
            self.externalLinks.clear()# = defaultdict(int)
            self.categories.clear()# = defaultdict(int)
            self.infobox.clear()# = defaultdict(int)
            self.body.clear()# = defaultdict(int)
            self.text = ""

        self.path.pop()
        self.parent = ""



    def endDocument(self):
        global indexDict
        print("No of Documents present ", self.docCount)
        print("\nIndexed data:")
        indexDict = collections.OrderedDict(sorted(indexDict.items()))
        outputFile = 'output.txt'
        #outputFile = sys.argv[2]
        #json.dump(indexDict, open(sys.argv[2], 'w'))
        with open(outputFile, 'w') as fp:
        	for key in indexDict:
        		fp.write(key+ "-"+ ", ".join(indexDict[key])+ "\n")



def indexer(docId, title,body, infobox, references, external_links, categories):
    global indexDict
    #print(list(body.keys()))
    #print((infobox.keys()))
    all_keys = list(body.keys())+list(infobox.keys())+list(references.keys())+list(external_links.keys())+list(categories.keys())
    all_keys = list(set(all_keys))


    for key in all_keys:
        strr = 'd'+str(docId)+':'
        if title[key] >= 1:
            strr += 't'+str(title[key])
        if body[key] >= 1:
            strr += 'b'+str(body[key])
        if infobox[key] >= 1:
            strr += 'i'+str(infobox[key])
        if categories[key] >= 1:
            strr += 'c'+str(categories[key])
        if references[key] >= 1:
            strr += 'r'+str(references[key])
        if external_links[key] >= 1:
            strr += 'e'+str(external_links[key])

        strr = 'd'+str(docId)+'t'+str(title[key])+'b'+str(body[key])+'i'+str(infobox[key])+\
                'c'+str(categories[key])+'r'+str(references[key])+'e'+str(external_links[key])
        #print(indexDict[key])
        if key in indexDict:
            indexDict[key].append(strr)
        else:
            indexDict[key] = [strr]


fileName = "../data/wiki-search-small.xml"
#fileName = "../data/enwiki-20170820-pages-articles15.xml-p9244803p9518046"
#fileName = sys.argv[1]

t1 = time()
xml.sax.parse(open(fileName, 'r'), WikiParser())
t2 = time()
print("parsing time is ", str(round(t2-t1, 3)), "sec")

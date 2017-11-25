#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.sax
import helperFunctions as hf
from time import time
from collections import defaultdict
import collections
import heapq
import math
import json
import sys

indexDict = defaultdict(str)
outputFileIndex = 0
noOutputFiles = 0
noDocs = 0
secondary_index_offset = []
secondary_index_offset.append(0)

title_ptr = open('big_files/id_title.txt', 'w')
title_offset = []
title_offset.append(0)

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

            #print("title ", self.title)
            '''print("references", self.references)
            print("external links ", self.externalLinks)
            print("Categories ", self.categories)
            print("Infobox Content ", self.infobox)
            print("Body : ",self.body)
'''
            stringg = str(self.docId)+"--"+str(self.titleName)+"\n"
            ll = len(title_offset)
            title_ptr.write(stringg)
            title_offset.append(title_offset[ll-1]+len(stringg))

            indexer(self.docId, self.title, self.body, self.infobox, self.references,
                    self.externalLinks, self.categories)

            self.docId = ""
            self.titleName = ""
            self.references.clear()
            self.externalLinks.clear()
            self.categories.clear()
            self.infobox.clear()
            self.body.clear()
            self.title.clear()
            self.text = ""
            try:
                global noDocs
                noDocs += 1



                global indexDict, outputFileIndex
                outputFileIndex += 1

                if outputFileIndex%1000 == 0:
                    global noOutputFiles
                    print("\n\n --------- Completed   ", outputFileIndex)
                    outputFile = "big_output/output_"+str(noOutputFiles)+".txt"

                    writeToFile(indexDict, outputFile)

                    indexDict.clear()
                    noOutputFiles += 1
            except:
                pass

        self.path.pop()
        self.parent = ""



    def endDocument(self):
        try:
            global indexDict, noOutputFiles
            ## Writing left over block of files into new output file
            indexDict = collections.OrderedDict(sorted(indexDict.items()))
            outputFile = "big_output/output_" + str(noOutputFiles) + ".txt"
            writeToFile(indexDict, outputFile)
            indexDict.clear()
            print("Written files/id-title.txt\n")
            ## Writing completed

            title_ptr.close()
        except:
            pass

        '''global indexDict
        print("No of Documents present ", self.docCount)
        print("\nIndexed data:")
        indexDict = collections.OrderedDict(sorted(indexDict.items()))
        outputFile = 'output/abcd.txt'
        #outputFile = sys.argv[2]
        #json.dump(indexDict, open(sys.argv[2], 'w'))
        with open(outputFile, 'w') as fp:
        	for key in indexDict:
        		fp.write(key+ "-"+ " ".join(indexDict[key])+ "\n")'''


def writeToFile(indexDict, outputFile):
    try:
        indexDict = collections.OrderedDict(sorted(indexDict.items()))
        with open(outputFile, 'w') as fp:
            for key in indexDict:
                fp.write(key + "-" + " ".join(indexDict[key]) + "\n")
        indexDict.clear()
        print("Written local inverted index file :", outputFile)
    except:
        pass

def indexer(docId, title,body, infobox, references, external_links, categories):
    global indexDict

    all_keys = list(body.keys())+list(infobox.keys())+list(references.keys())+list(external_links.keys())+list(categories.keys())
    all_keys = list(set(all_keys))

    vocSize = len(all_keys)

    for key in all_keys:
        tf = title[key] + body[key] + infobox[key] + categories[key] + references[key] + external_links[key]
        if vocSize > 0:
            tf = round(tf/float(vocSize), 4) ## Rounded term frequency


        strr = str(docId)+':'+ str(tf)+":" # docId at start of posting entry
        try:
            if title[key] >= 1:
                #strr += 't'+str("{0:.4f}".format(round(title[key]/float(len(title)), 4)))
                #strr += 't' + str("{3d}".format(title[key]))
                strr += 't' + str(title[key])
        except:
            pass
        try:
            if body[key] >= 1:
                #strr += 'b'+str("{0:.4f}".format(round(body[key]/float(len(body)), 4)))
                #strr += 'b' + str("{3d}".format(body[key]))
                strr += 'b' + str(body[key])
        except:
            pass
        try:
            if infobox[key] >= 1:
                #strr += 'i'+str("{0:.4f}".format(round(infobox[key]/float(len(infobox)), 4)))
                #strr += 'i' + str("{3d}".format(infobox[key]))
                strr += 'i' + str(infobox[key])
        except:
            pass
        try:
            if categories[key] >= 1:
                #strr += 'c'+str("{0:.4f}".format(round(categories[key]/float(len(categories)), 4)))
                #strr += 'c' + str("{3d}".format(categories[key]))
                strr += 'c' + str(categories[key])
        except:
            pass
        try:
            if references[key] >= 1:
                #strr += 'r'+str("{0:.4f}".format(round(references[key]/float(len(references)), 4)))
                #strr += 'r' + str("{3d}".format(references[key]))
                strr += 'r' + str(references[key])
        except:
            pass
        try:
            if external_links[key] >= 1:
                #strr += 'e'+str("{0:.4f}".format(round(external_links[key]/float(len(external_links)), 4)))
                #strr += 'e' + str("{3d}".format(external_links[key]))
                strr += 'e' + str(external_links[key])
        except:
            pass

        if key in indexDict:
            indexDict[key].append(strr)
        else:
            indexDict[key] = [strr]

def mergeFiles():
    #print("HELLOOO")
    #try:
        global noOutputFiles, noDocs, secondary_index_offset
        #print ("my no docs", noDocs)
        isFileProcessed = [0]*(noOutputFiles+1)
        filePointers = {}
        words = {}
        heap = []
        vocList = open("big_files/vocabulary_list.txt", 'w')
        for i in range(noOutputFiles+1):
            fileName =  "big_output/output_"+str(i)+".txt"

            filePointers[i] = open(fileName, 'r')
            words[i] = filePointers[i].readline().strip().split('-') #words[0] = key; words[1] = posting list
            words[i][0] = words[i][0].strip()

            if words[i][0] not in heap:
                heapq.heappush(heap, words[i][0])

            isFileProcessed[i] = 1

        data = defaultdict(list)

        key_cnt = 0 ## no of keys <-> vocabulary

        no_indices_per_file = 1000

        file_no = 0 ## No of primary index files <-> No of lines in secondary index

        sec_ind = open('big_output/secondary_index.txt', 'w')
        while any(isFileProcessed) == 1:
            top = heapq.heappop(heap)
            vocList.write(top+"\n")
            key_cnt += 1
            for i in range(noOutputFiles+1):
                if isFileProcessed[i] and words[i][0] == top:
                    data[top].extend(words[i][1].split())

                    k = filePointers[i].readline().strip()
                    if k == "":
                        filePointers[i].close()
                        isFileProcessed[i] = 0
                        #os.remove("big_output/output_"+str(i)+".txt")
                    else:
                        words[i] = k.split('-')
                        words[i][0] =words[i][0].strip()
                        if words[i][0] not in heap:
                            heapq.heappush(heap, words[i][0])

            if key_cnt % no_indices_per_file == 0:
                file_no = int(key_cnt/no_indices_per_file)
                start = 0
                with open("big_output/index"+str(file_no)+".txt", 'w') as fptr:
                    #with open("big_files/index_offset"+str(file_no)+".txt", 'w') as f_ind:

                        #off = 0
                        for key in sorted(data.keys()):
                            if start == 0:
                                start_key = key
                                start = 1
                            df = len(data[key])
                            try:
                                idf = round(math.log(noDocs / float(df)), 4)  # inverse document frequency
                                dt = key + ":" + str(idf)+ "-" + " ".join(data[key])+"\n"
                                fptr.write(dt)

                                # off += len(dt)
                                #f_ind.write(" " + str(len(dt)))
                            except:
                                pass



                print("Written output/index"+str(file_no)+".txt")

                end_key = key

                strr = start_key+":"+end_key+"-"+str(file_no)+"-"+str(len(data))+"\n"
                sec_ind.write(strr)

                secondary_index_offset.append(len(strr))

                data.clear()

        file_no += 1
        with open("big_output/index" + str(file_no) + ".txt", 'w') as fptr:
            #with open("big_files/index_offset" + str(file_no) + ".txt", 'w') as f_ind:
                start = 0
                #off = 0
                for key in sorted(data.keys()):
                    if start == 0:
                        start_key = key
                        start = 1
                    df = len(data[key])
                    idf = round(math.log(noDocs / float(df)), 4) # inverse document frequency
                    dt = key + ":" + str(idf) + "-" + " ".join(data[key]) + "\n"
                    fptr.write(dt)

                    #off += len(dt)
                    #f_ind.write(" " + str(len(dt)))

        print("Written output/index" + str(file_no) + ".txt")

        end_key = key

        strr = start_key + ":" + end_key + "-" + str(file_no) + "-" + str(len(data)) + "\n"
        sec_ind.write(strr)
        secondary_index_offset.append(len(strr))



        print("Written Secondary index file output/secondary_index.txt")
        sec_ind.close()
        print("Written Vocabulary List files/vocabulary_list.txt")
        vocList.close()

        return key_cnt, file_no
    #except:
    #    pass

#fileName = "../data/enwiki-latest-pages-articles-multistream.xml"
fileName = "../data/wiki-search-small.xml"
#fileName = "../data/enwiki-20170820-pages-articles15.xml-p9244803p9518046"
#fileName = sys.argv[1]

t1 = time()
xml.sax.parse(open(fileName, 'r'), WikiParser())



#### Multiple local inverted index files created by this time
print("\nMultiple local inverted index files created by this time\n")
print(noOutputFiles)

vocSize, noOfFiles = mergeFiles()
print(vocSize, noOfFiles)

metadata = {}
metadata["vocabulary_size"] = vocSize
metadata["no_of_index_files"] = noOfFiles
metadata['secondary_index_offset'] = secondary_index_offset
metadata['no_of_docs'] = noDocs
metadata['title_offsets'] = title_offset

with open("big_files/metadata.json" , 'w') as fptr:
    json.dump(metadata, fptr, sort_keys=True)

#print(secondary_index_offset)

t2 = time()
print("Index creation time is ", str(round(t2-t1, 3)), "sec")



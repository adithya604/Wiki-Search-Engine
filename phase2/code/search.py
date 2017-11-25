from  time import  time
from nltk.corpus import stopwords
from collections import defaultdict
import Stemmer # for PyStemmer
import string
import re
import json
import operator

stop = set(stopwords.words('english'))
ps = Stemmer.Stemmer('english')

stopWordsDict = defaultdict(int)
for word in stop:
    stopWordsDict[word] = 1

metadata = {}
with open("big_files/metadata.json", 'r') as fptr:
    metadata = json.load(fptr)

def tokenizeText(text1):
    spacesReg = re.compile(u"[\s\u0020\u00a0\u1680\u180e\u202f\u205f\u3000\u2000-\u200a]+")
    text1 = spacesReg.sub(" ", text1).strip()
    text1 = re.sub('[:|\\|/|=|?|!|~|`|!|@|#|$|%|^|&|*|(||)|_+.\\|-|{|}|\[|\]|;|\"|\'|<|>|,|]',' ',text1)
    text1 = re.sub(r'-(-+)|/(/+)',' ',text1)
    text1 = re.sub(' \S ',' ',text1)
    text1 = text1.split()
    return text1

def isStopWord(word):
    word = word.strip()
    t1 = len(word)
    word = ''.join(filter(lambda x: x in string.printable, word))
    t2 = len(word)
    if t1 == t2 and stopWordsDict[word] != 1 and len(word) > 1 and 'http' not in word:
        return False
    return True

def stemmedWord(word):
    return ps.stemWord(word)

        #global metadata
        #high = metadata['no_of_index_files']
        #low = 0
        #line_offset = metadata['secondary_index_offset']

    #with open('big_output/secondary_index.txt', 'r') as f:


# f.seek(sum(line_offset[:mid]))
# line = f.readline().strip()


# Returns File index and no of lines in the File from secondary index
def getFileIndex(term):

        lines = open('big_output/secondary_index.txt', 'r').readlines()
        low = 0
        high = len(lines)-1
        while low < high:
            mid = int(low + (high-low)/2)
            line = lines[mid].strip()

            terms = line.split('-')
            ranges = terms[0].strip().split(':')
            start = ranges[0]
            end = ranges[1]
            fileNo = terms[1]
            #fileLen = terms[2]
            #print(start, end,str(low), str(high), fileNo, fileLen)

            if term >= start and term <= end:
                return fileNo
            elif term < start:# and term < end:
                high = mid
            elif term > end:
                low = mid + 1

        return None

    #print(term, fileIndex, noLines)
    #file_offset = ""
    #with open("big_files/index_offset"+fileIndex+".txt", 'r')as f:
    #    file_offset = f.readline().strip().split()
    #    file_offset = list(map(int, file_offset)) ## offsets are stored as difference from prev line not from first

    #low = 0
    #high = int(noLines)
    #with open("big_output/index"+fileIndex+".txt", 'r') as f:

#       f.seek(sum(file_offset[:mid]))  ## as offsets are stored as difference from prev line, we sum all offsets
#  to get total offset from 0th position to start of 'mid' line
#        line = f.readline().strip().split('-')
# print(lines[mid])

def getPreprocessedTokens(text): ## get stemmed tokens of text
    text = tokenizeText(text)
    ln = len(text)
    stemmed_list = []
    for i in range(ln):
        if isStopWord(text[i]) == False:
            stemmed_list.append(stemmedWord(text[i]))
    #print(stemmed_list)
    return stemmed_list

def getTitleNames(docid):
    with open('big_files/id_title.txt', 'r') as idt:
        for line in idt:
            line = line.strip().split("--")
            if line[0] == docid:
                return line[1]
    return None

def getScores(finalDict):
    scores = defaultdict(float)
    for token in finalDict:
        for docid in finalDict[token]:
            scores[docid] += finalDict[token][docid]

    scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    return scores

def getTitle(docid):
    global metadata
    no_titles = metadata['no_of_docs']
    title_offsets = metadata['title_offsets']
    print(len(title_offsets))
    low = 0
    high = no_titles
    print(no_titles)
    with open('big_files/id_title.txt', 'r') as idt:
        while low < high:
            mid = int(low + (high-low)/2)
            print(mid)
            print(title_offsets[mid])

            idt.seek(title_offsets[mid])

            line = idt.readline().strip()
            try:
                doc, title = line.split('--')
            except:
                line = idt.readline().strip()
                doc, title = line.split('--')
            if docid == doc:
                return title
            elif docid < doc:
                high = mid
            else:
                low = mid+1
        return None

def processPostingList(idf, listt, field= "NA"):
    postList = listt.strip().split()
    postListDict = defaultdict(float)
    if field == 'NA':
        for item in postList:
            sp = item.split(':')
            postListDict[sp[0]] = float(sp[1])*float(idf)
    else:
        for item in postList:
            if field in list(item):
                sp = item.split(':')
                ind = item.index(field)
                ind += 1
                strr = ""
                postListDict[sp[0]] = float(item[ind+1:ind+7])
    if not postListDict:
        return None
    return postListDict


def processFieldQueries(text):
    listt = re.split(r'([t|b|c|e|i]:)',text)
    finalDict = {}
    if listt[0] != "":
        query = getPreprocessedTokens(listt[0])
        processSimpleQuery(query)
    else:
        listt = listt[1:]
        for i in range(0, len(listt), 2):
            finalDict = {}
            tokens = getPreprocessedTokens(listt[i+1].strip())
            #print(tokens)
            for token in tokens:
                fileIndex = getFileIndex(token)
                #print("fileIndex is ", fileIndex, token)
                if fileIndex is not None:
                    #print(listt[0][0])
                    idf, postingList = getPostingList(token, fileIndex)
                    if postingList is not None:
                        postingList =  processPostingList(idf, postingList, listt[i][0])
                        if postingList is not None:
                            finalDict[token] = postingList
            #print(finalDict)
            #finalDict = dict(finalDict)
            #print(finalDict.keys())
            if len(finalDict) > 0:
                printResults(finalDict)
            else:
                processSimpleQuery(tokens)


def getPostingList(term, fileIndex):
    lines = open("big_output/index"+fileIndex+".txt", 'r').readlines()
    low = 0
    high = len(lines)-1
    while low < high:
            mid = int(low+(high-low)/2)

            line = lines[mid].strip().split("-")
            dict_key, idf = line[0].split(':')
            if dict_key == term:
                return idf, line[1]
            elif term < dict_key:
                high = mid
            else:
                low = mid+1

    return None, None

def printResults(dictt):
    scores = getScores(dictt)
    titles = []
    for item in scores:
        titles.append(getTitleNames(item[0]))
    print("\nList of top 10 titles :")
    if len(titles) < 10:
        for title in titles:
            print(title)
    else:
        for i in range(10):
            print(titles[i])


def processSimpleQuery(tokens):
    finalDict = defaultdict(defaultdict)
    for token in tokens:
        fileIndex = getFileIndex(token)
        if fileIndex is not None:
            idf, postingList= getPostingList(token, fileIndex)
            if postingList is not None:
                postingList = processPostingList(idf, postingList)
                finalDict[token] = postingList

    # print(query+":")
    printResults(finalDict)


def main():

    cnt = 1

    while True:
        query = input("\nQ"+str(cnt)+" : ")
        t1 = time()
        if re.search(r'[t|b|c|e|i]:', query):
            processFieldQueries(query)
        else:
            tokens = getPreprocessedTokens(query)
            processSimpleQuery(tokens)


        t2 = time()

        print("Query Processing time for Q"+str(cnt)+" is ", str(round(t2 - t1, 10)), "sec")

        cnt += 1


main()
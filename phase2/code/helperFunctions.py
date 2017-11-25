#!/usr/bin/python
# -*- coding: utf-8 -*-


from collections import Counter
import string
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import defaultdict
import Stemmer # for PyStemmer
import re
import sys

ascii = set(string.printable)

#sys.setdefaultencoding('utf8')

stop = set(stopwords.words('english'))
#ps = SnowballStemmer('english')
#ps = PorterStemmer('english')
ps = Stemmer.Stemmer('english')

stopWordsDict = defaultdict(int)
for word in stop:
    stopWordsDict[word] = 1

punctuations = list('!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~0123456789–®')

cnt = 0

def parseText(text):
    referencesText = ""
    externalLinkText = ""
    categoriesText = ""
    infoBoxText = ""
    bodyText = ""

    #text.decode('utf-8').strip()
    #text = unicode(text, errors='ignore')

    text = text.replace('\'', '')
    text = text.replace('.', ' ')
    text = text.replace('[', ' ')
    text = text.replace(']', ' ')
    '''text = text.replace(',', ' ')
    text = text.replace('-', ' ')
text = text.replace('_', ' ')
text = text.replace(':', ' ')
text = text.replace(';', ' ')
text = text.replace('"', ' ')'''

    text = text.lower().split('\n')
    i=0
    leng = len(text)
    global cnt
    while i < leng:
        try:
            ## Extracting categories - next two if's for two types of categories
            if "[[category" in text[i]:
                categories = text[i].split(':')
                if len(categories) > 1:
                    categoriesText += " " + categories[1]
            elif "[[:category" in text[i]:
                temp = text[i]
                no_categories = text[i].count("[[:category")
                for _ in range(no_categories):
                    temp1 = temp.split("[[:category", 1)
                    temp2 = temp1[1].split("]]", 1)
                    categoriesText += " " + temp2[0][1:]
                    temp = temp2[1]

            ## Extracting InfoBox contents
            ## Two types of infoboxes -- '{{infobox' and '{{ infobox' --- two if's below
            elif '{{infobox' in text[i]:
                counter = 0
                infoSplit = text[i].split('{{infobox')
                if len(infoSplit) > 1:
                    infoBoxText += " " + infoSplit[1]
                while True:
                    counter = counter + text[i].count("{{")
                    counter = counter - text[i].count("}}")
                    if counter <= 0:
                        break
                    i = i+1
                    infoBoxText += " " + text[i]

            elif '{{ infobox' in text[i]:
                counter = 0
                infoSplit = text[i].split('{{infobox')
                if len(infoSplit) > 1:
                    infoBoxText += " " + infoSplit[1]
                while True:
                    counter = counter + text[i].count("{{")
                    counter = counter - text[i].count("}}")
                    if counter <= 0:
                        break
                    i = i + 1
                    infoBoxText += " " + text[i]

            ## Extracting information(titles,....) from references section
            elif "==references==" in text[i] or "== references ==" in text[i] \
                    or "==references ==" in text[i] or "== references==" in text[i] :

                i = i+1 # Going to next string to ==References==
                while i+1 < leng:
                    flag = 0
                    if (text[i] == "" and "==" in text[i+1]) or \
                            (text[i].endswith('}}') and text[i+1] == ""):
                        flag = 1
                        break

                    if 'title' in text[i] or '?title' in text[i]:
                        values = text[i].split('title')
                        title = ""

                        for k in values[1]:
                            if k == '|': # processing till '|' after splitting by 'title'
                                break
                            title = title + k

                        #print(title) ## general form of title  is " = This is TITLE"
                        title = title.strip() # removes spaces before and after
                        title = title[1:] # removes = at the start of title
                        title = title.strip() # removes spaces if any present between = and first character of title
                        #print(title) # now title is "This is TITLE"

                        referencesText = referencesText + " " + title
                    i = i+1

                    if flag == 1:
                        if 'title' in text[i] or '?title' in text[i]:
                            values = text[i].split('title')
                            title = ""

                            for k in values[1]:
                                if k == '|': # processing till '|' after splitting by 'title'
                                    break
                                title = title + k

                            #print(title) ## general form of title  is " = This is TITLE"
                            title = title.strip() # removes spaces before and after
                            title = title[1:] # removes = at the start of title
                            title = title.strip() # removes spaces if any present between = and first character of title
                            #print(title) # now title is "This is TITLE"

                            referencesText = referencesText + " " + title

            elif '==external links==' in text[i] or '== external links ==' in text[i] or \
                            '==external links ==' in text[i] or '== external links==' in text[i]:
                i += 1

                while i+1 < leng:
                    flag = 0
                    if (text[i] == "" and text[i+1].startswith("{{") or
                            (text[i] == "" and text[i+1].startswith("[[category"))):
                        flag = 1
                        break
            ### Form of text : * [http://www.severusalexander.com/Severus Alexander] a site devoted to this emperor
            ### Extracted Info : Alexander] a site devoted to this emperor
                    text[i] = text[i].strip()
                    if text[i].startswith('* [') or text[i].startswith('*[') \
                            or text[i].startswith('**[') or text[i].startswith('** ['):
                        text[i] = text[i][3:]
                        text[i] = text[i].split(' ', 1) # splitting text[i] starting from http: and
                                                        # taking the 2nd string ignoring 1st one which is url
                        if len(text[i]) > 1:
                            text[i] = text[i][1]
                        else:
                            text[i] = text[i][0]

                        externalLinkText += " " + text[i]
                    elif 'title' in text[i] or '?title' in text[i]:
                        values = text[i].split('title')
                        title = ""

                        for k in values[1]:
                            if k == '|': # processing till '|' after splitting by 'title'
                                break
                            title = title + k

                        #print(title) ## general form of title  is " = This is TITLE"
                        title = title.strip() # removes spaces before and after
                        title = title[1:] # removes = at the start of title
                        title = title.strip() # removes spaces if any present between = and first character of title
                        #print(title) # now title is "This is TITLE"

                        externalLinkText += " " + title
                    if flag == 1:
                        text[i] = text[i].strip()
                        if text[i].startswith('* [') or text[i].startswith('*[') \
                                or text[i].startswith('**[') or text[i].startswith('** ['):
                            text[i] = text[i][3:]
                            text[i] = text[i].split(' ', 1)  # splitting text[i] starting from http: and
                            # taking the 2nd string ignoring 1st one which is url
                            if len(text[i]) > 1:
                                text[i] = text[i][1]
                            else:
                                text[i] = text[i][0]

                            externalLinkText += " " + text[i]
                        elif 'title' in text[i] or '?title' in text[i]:
                            values = text[i].split('title')
                            title = ""

                            for k in values[1]:
                                if k == '|':  # processing till '|' after splitting by 'title'
                                    break
                                title = title + k

                            # print(title) ## general form of title  is " = This is TITLE"
                            title = title.strip()  # removes spaces before and after
                            title = title[1:]  # removes = at the start of title
                            title = title.strip()  # removes spaces if any present between = and first character of title
                            # print(title) # now title is "This is TITLE"

                            externalLinkText += " " + title

                    i += 1
            else:
                bodyText += " " + text[i]

            i += 1
        except:
            pass

    text[:] = []

    #return getTermFreqDictionary(referencesText), getTermFreqDictionary(externalLinkText), getTermFreqDictionary(categoriesText), \
    #       getTermFreqDictionary(infoBoxText), getTermFreqDictionary(bodyText)

    return getFreq(referencesText), getFreq(externalLinkText), \
           getFreq(categoriesText), getFreq(infoBoxText), getFreq(bodyText)

def tokenise(text1):
    spacesReg = re.compile(u"[\s\u0020\u00a0\u1680\u180e\u202f\u205f\u3000\u2000-\u200a]+")
    text1 = spacesReg.sub(" ", text1).strip()
    text1 = re.sub('[:|\\|/|=|?|!|~|`|!|@|#|$|%|^|&|*|(||)|_+.\\|-|{|}|\[|\]|;|\"|\'|<|>|,|]',' ',text1)
    text1 = re.sub(r'-(-+)|/(/+)',' ',text1)
    text1 = re.sub(' \S ',' ',text1)
    text1 = text1.split()
    return text1

def getFreq(text):
    try:
        k = getN(text)
        text = text[0:k]

        #text = tokenise(text)
        text = re.findall(" [\w]+ ", text)
        #text = word_tokenize(text)
        #content = [ps.stem(word) for word in text if stopWordsDict[word]!=1 and len(word)>3 and 'http' not in word]
        content = []
        for word in text:
            word = word.strip()
            t1 = len(word)
            word = ''.join(filter(lambda x:x in string.printable, word))
            t2 = len(word)

            if t1 == t2 and stopWordsDict[word] != 1 and len(word)>3 and 'http' not in word:
                content.append(ps.stemWord(word))

        text[:] = []

        freq = defaultdict(int)
        for key in content:
            freq[key] += 1
        
        content[:] = []

        return freq
    except:
        pass

def getTermFreqDictionary(text):
    try:
        k = getN(text)
        text = text[0:k]
        # Removing punctuation marks

        
        text = text.replace('&nbsp', ' ')
        wordList = text.strip().split()
        #print(wordList)

        text = []
        # Stemming and stop word removal
        if len(wordList) > 0:
            for word in wordList:
                word = word.strip()
                #print(word)
                if 'http' in word:
                    continue
                for i in punctuations:
                    if i in word:
                        word = word.replace(i, ' ')

                words = word.strip().split()
                for word1 in words:
                    word1 = word1.strip()
                    t1 = len(word1)
                    word1 = ''.join(filter(lambda x: x in string.printable, word1))
                    t2 = len(word1)

                    if t1 == t2 and stopWordsDict[word1] != 1 and len(word1) > 3:
                        text.append(ps.stemWord(word1))

        freq = defaultdict(int)
        for key in text:
            freq[key] += 1
        return freq
    except:
            pass

def parseTitle(content):
    try:
        global stop, ps
        # Some titles are like 'AmericanTourist', the below line is to process it
        leng = len(content)
        title = ""

        if content.isupper(): # No change in content if it is uppercase -- eg DBMS, AMERICAN TOURIST
            title = content
        else: # Some titles are like 'AmericanTourist', the below for is to process
              # it to 'American Tourist' when upper case letter is not the last letter
            for i in range(leng):
                if content[i].isupper() and i != leng-1:
                    title = title + " " + content[i]
                else:
                    title = title + content[i]

        # stripping spaces, converting to lower and then splitting the string into words
        wordList = title.strip().lower().split()

        # stripping punctuation marks around all the words in wordList and forming list
        title = []
        for word in wordList:
            word = word.strip(string.punctuation)
            if stopWordsDict[word]!=1 and len(word)>3:
                title.append(ps.stemWord(word))

        wordList[:] = []
        
        freq = defaultdict(int)
        for key in title:
            freq[key] += 1
        # prints Frequency of words in content
        return  freq
    except:
            pass

def getN(text):
    return int(len(text))
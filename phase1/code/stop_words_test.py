from nltk.corpus import stopwords
from nltk import PorterStemmer

stri = "sachin is a cricketer"

stop = set(stopwords.words('english'))
ps = PorterStemmer()

for i in stri.split():
    if i not in stop:
        print(i)
        print(ps.stem(i))
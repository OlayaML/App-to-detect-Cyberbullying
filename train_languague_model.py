'''
@author: olayamoranlevas
'''

'''    IMPORT LIBRARY   '''

from numpy import vstack
from numpy import array
from pickle import dump
from keras.utils import to_categorical
from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Embedding

'''    FUNCTIONS    '''

#load doc into memory
def load_doc(filename):
    # open the file as read only
    file = open(filename, 'r')
    # read all text
    text = file.read()
    # close the file
    file.close()
    return text

'''    LOAD CLEAN DATASET    '''

filename = 'ESPformspring_cleandata.csv'
doc = load_doc(filename)
lines = doc.split('\n')
lines.pop(0)
lines.pop(12158)

data = []
strlabel = []

for line in lines:
    Data_Label = line.split('|')
    
    i = 0
    for d in Data_Label:
        if i == 0:
            data.append(d)
            i = i + 1
        else:
            strlabel.append(d)


label = []

for elem in strlabel:
    if (elem == '0.0' or elem == '1.0'):
        elem.split('.')
        label.append(int(elem[0]))

'''    ENCODE DATA    '''

# integer encode sequences of words
tokenizer = Tokenizer()
tokenizer.fit_on_texts(data)
tokendata = tokenizer.texts_to_sequences(data)

#maxdata_length = 0
#for listElem in tokendata:
#    if (maxdata_length < len(listElem)):
#        maxdata_length = len(listElem)
#print(maxdata_length)

nitem = 0
for item in tokendata:
    nWord = len(item)
    blank = [50]*(598-nWord)
    item = item + blank
    tokendata[nitem] = item
    nitem = nitem +1

# vocabulary size
vocab_size = len(tokenizer.word_index) + 1

''' SEQUENCE INPUTS AND LABEL OUTPUT  '''
# now that we have encoded the input sequences, 
# we need to separate them into input (X) and output (y) elements.

tokendata = array(tokendata)

#X = array([array(xi) for xi in tokendata])
#X = vstack(X)
X = tokendata
y = to_categorical(array(label), num_classes=2)
maxdata_length = X.shape[1]


'''    FIT MODEL   '''

# define model
model = Sequential()
model.add(Embedding(vocab_size, 50, input_length=maxdata_length))
model.add(LSTM(100, return_sequences=True))
model.add(LSTM(100))
model.add(Dense(100, activation='relu'))
model.add(Dense(2, activation='softmax'))
print(model.summary())

# compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# fit model
model.fit(X, y, batch_size=128, epochs=100)

'''    SAVE MODEL  '''

# save the model to file
model.save('model.h5')

# save the tokenizer
dump(tokenizer, open('tokenizer.pkl', 'wb'))
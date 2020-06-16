'''
@author: olayamoranlevas
'''
from keras.utils.np_utils import to_categorical

'''    IMPORT LIBRARY   '''

from numpy import array
from pickle import dump
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

data_list = []
label_list = []

for line in lines:
    Data_Label = line.split('|')
    
    i = 0
    for data in Data_Label:
        if i == 0:
            data_list.append(data)
            i = i + 1
        else:
            label_list.append(data)


'''    ENCODE DATA    '''

# integer encode sequences of words
tokenizer = Tokenizer()
tokenizer.fit_on_texts(data_list)
tokendata_list = tokenizer.texts_to_sequences(data_list)

#tokenizer.fit_on_texts(label_list)
#tokenlabel_list = tokenizer.texts_to_sequences(label_list)

# vocabulary size
vocab_size = len(tokenizer.word_index) + 1

intlabel_list = []

for elem in label_list:
    if (elem == '0.0' or elem == '1.0'):
        elem.split('.')
        intlabel_list.append(int(elem[0]))

''' SEQUENCE INPUTS AND LABEL OUTPUT  '''
# now that we have encoded the input sequences, 
# we need to separate them into input (X) and output (y) elements.

listOftokendata_lists = array(tokendata_list)
X = listOftokendata_lists
y = to_categorical(array(intlabel_list), num_classes=2)


maxdata_length = 0
for listElem in listOftokendata_lists:
    if (maxdata_length < len(listElem)):
        maxdata_length = len(listElem)

'''    FIT MODEL   '''

# define model
model = Sequential()
model.add(Embedding(vocab_size, 50, input_length=1))
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

'''
@author: olayamoranlevas
'''
from keras.layers.wrappers import Bidirectional
from sklearn.externals._arff import DENSE
from keras.layers.convolutional import Convolution2D
from keras.layers.pooling import MaxPool1D
from cffi.ffiplatform import flatten

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
    data_list.append(Data_Label[0])
    label_list.append(Data_Label[1])

'''    ENCODE DATASET    '''

# integer encode sequences of words
tokenizer = Tokenizer()
tokenizer.fit_on_texts(data_list)
tokendata_list = tokenizer.texts_to_sequences(data_list)

# vocabulary size
vocab_size = len(tokenizer.word_index) + 1

''' SEQUENCE INPUTS AND LABEL OUTPUT  '''
# now that we have encoded the input sequences, 
# we need to separate them into input (X) and output (y) elements.

listOftokendata_lists = array(tokendata_list)
listOflabel_lists = array(label_list)
X = listOftokendata_lists
y = listOflabel_lists

maxdata_length = 0
for listElem in listOftokendata_lists:
    if (maxdata_length < len(listElem)):
        maxdata_length = len(listElem)

print(maxdata_length)
    
'''    FIT MODEL   '''

# define model
model = Sequential()
model.add(Embedding(vocab_size, input_length=maxdata_length))
model.add(Convolution2D(f=3,k=4))
model.add(MaxPool1D(p=5))
model.add(flatten())
model.add(Dense(n=10))
model.add(Dense)


#model.add(Embedding(vocab_size, 50, name="embedding"))
#model.add(Bidirectional(LSTM(100, unit_forget_bias=True, name="lstm")))
#model.add(Dense(vocab_size, activation = 'softmax', name="dense"))

#model.add(LSTM(100, return_sequences=True))
#model.add(LSTM(100))
#model.add(Dense(100, activation='relu'))
#model.add(Dense(vocab_size, activation='softmax'))
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

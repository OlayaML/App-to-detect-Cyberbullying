'''
@author: olayamoranlevas
'''

'''    IMPORT LIBRARY   '''
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

# dataset = loadtxt('ESPformspring_cleandata.csv', delimiter='|', skiprows=1)

in_filename = 'ESPformspring_cleandata.csv'
doc = load_doc(in_filename)
lines = doc.split('\n')

data_list = []
label_list = []

for line in lines:
    Data_Label = line.split('|')
    
    i = 0
    for data in Data_Label:
        if i == 0:
            data_list.append(data)
            i = i+1
        else:
            label_list.append(data)
    
print(data_list)
print(label_list)



'''    ENCODE DATASET    '''

# integer encode sequences of words
tokenizer = Tokenizer()
tokenizer.fit_on_texts(data_list)
sequences = tokenizer.texts_to_sequences(data_list)

# vocabulary size
vocab_size = len(tokenizer.word_index) + 1

''' SEQUENCE INPUTS AND LABEL OUTPUT  '''
# now that we have encoded the input sequences, 
# we need to separate them into input (X) and output (y) elements.
X = data_list
y = label_list

seq_length = X.shape[1]

'''    FIT MODEL   '''

# define model
model = Sequential()
model.add(Embedding(vocab_size, 50, input_length=seq_length))
model.add(LSTM(100, return_sequences=True))
model.add(LSTM(100))
model.add(Dense(100, activation='relu'))
model.add(Dense(vocab_size, activation='softmax'))
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

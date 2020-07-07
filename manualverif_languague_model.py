'''
@author: olayamoranlevas
'''

'''    IMPORT LIBRARY   '''

import itertools
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from numpy import arange, newaxis
from numpy import array
from numpy import random
from pickle import load
from keras.models import load_model
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split

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

def plot_confusion_matrix(cm, classes, normalize=False, title = 'Confusion matrix'):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting 'normmalize = True'.
    """
    
    plt.imshow(cm, interpolation='nearest')
    plt.title(title)
    plt.colorbar()
    tick_marks = arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    
    if normalize:
        cm = cm.astype('float') / cm.sum(axis = 1) [:, newaxis]
        print("Normalized confusion matrix")
    
    else:
        print('Confusion matrix, without normalization')
    
    print(cm)
    
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment = "center",
                 color = "white" if cm[i, j] > thresh else "black")
        
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
        
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

# load the tokenizer
tokenizer = load(open('tokenizer.pkl', 'rb'))

# integer encode sequences of words
tokenizer.fit_on_texts(data)
tokendata = tokenizer.texts_to_sequences(data)

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

X = tokendata
y = to_categorical(array(label), num_classes=2)
maxdata_length = X.shape[1]

'''    LOAD MODEL    '''

# load the model
model = load_model('model.h5')

'''    EVALUATE MODEL   '''
# fix random seed for reproducibility
seed = 7
random.seed(seed)

# split into 67% for train and 33% for test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=seed)

print(X_test)
print(y_test)
# Fit the model

model.fit(X_train, y_train, validation_data=(X_test,y_test), epochs=10, batch_size=10)

"""    CONFUSION MATRIX    """

y_pred = model.predict(X_test)

print(y_pred)

cm_plot_labels = ['no_ciberbullying', 'ciberbullying']
cm = confusion_matrix(y_test.argmax(axis=1), y_pred.argmax(axis=1))
plot_confusion_matrix(cm, cm_plot_labels, title='Confusion Matrix')

'''
@author: olayamoranlevas
'''

'''    IMPORT LIBRARY   '''
import csv

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

combined = zip(data, label)

'''    FIND CIBERBULLYING MESSAGES AND CREATING SYNTHETIC DATA  '''

cyber_mess = []
cont = 0

for da, la in zip(data,label):
    if la == 1:
        cyber_mess.append(da)
        cont = cont + 1

newin = [1]*cont

syntheticdata = data
syntheticlabel = label

j = 0
while j < 4:
    syntheticdata = syntheticdata + cyber_mess
    syntheticlabel = syntheticlabel + newin
    j = j+1


print(syntheticdata)
print(len(syntheticdata))
print(syntheticlabel)
print(len(syntheticlabel))


# COMBINE THEM TO CREATE CLEANDATA.CSV
combined = zip(syntheticdata, syntheticlabel)


'''    CREATE CLEANDATA.CSV   '''

with open('ESPformspring_syntheticdata.csv', 'w', newline='') as myFile:
    writer = csv.writer(myFile, delimiter='|')
    writer.writerow(['SpanishData', 'BullyingLabel'])
    writer.writerows(combined)

print("Writing ESPformspring_syntheticdata.csv complete")


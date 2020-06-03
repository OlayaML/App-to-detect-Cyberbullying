'''
@author: olayamoranlevas
'''

'''    IMPORT LIBRARY   '''
import pandas as pd
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from google.cloud import translate_v2 as translate
import string
import csv

''' FUNCTIONS '''
def translate_text(text):  
    translate_client = translate.Client()
        
    try:
        translation = translate_client.translate(text, source_language='en', target_language='es')
        
    except:
        print("------> Se ha producido un fallo de conexion")
        return translate_text(text)

    return translation['translatedText']

'''    VIEW DATA   '''
# Read data from file 'fromspring_data.csv' 
# df = pd.read_csv("formspring_data.csv", sep='\t')
# View Data
# pd.set_option('display.max_columns', 100)  # The maximum amount of columns to display
# df.info()
# df.shape
# df.columns
# df.describe()
# print (df.head(),"\n")

# Understand missing values
# df.isnull().any()
# print("Percent of null values:")
# print(df.isnull().sum()/df.shape[0], "\n")  # Percent of null values
# print("Percent that are full:")
# print(pd.notnull(df).sum()/df.shape[0], "\n")  # Percent that are full

'''    MANIPULATION   '''
mdf = pd.read_csv("formspring_data.csv", sep='\t', usecols=['post', 'severity1', 'severity2', 'severity3'], na_values=['None', 'n/a0', '0`','o','`0','N/a'])

# To change the column name
mdf.rename(index=str,columns={'post':'Data'}, inplace=True)

#Delete rows with NaN values
mdf = mdf.dropna()

# Column Creation
mdf['Bullying'] = 1.0
mdf['NotBullying'] = 0.0

def get_column_label(mdf):
    if mdf['severity1'] != mdf['NotBullying']:
        return mdf['Bullying']
    elif mdf['severity2'] != mdf['NotBullying']:
        return mdf['Bullying']
    elif mdf['severity3'] != mdf['NotBullying']:
        return mdf['Bullying']
    else:
        return mdf['NotBullying']

mdf['Label'] = mdf.apply(get_column_label, axis = 1)

#Remove unnecessary columns to clean the data
unnecesary_cols_to_drop = ['severity1',
                           'severity2',
                           'severity3',
                           'Bullying',
                           'NotBullying']

clean_mdf = mdf.drop(unnecesary_cols_to_drop, axis=1)

# pd.set_option('display.max_columns', 100)
# clean_mdf.info()
# clean_mdf.shape
# clean_mdf.columns
# clean_mdf.describe()
# print (clean_mdf.head(25),"\n")


'''    PREPROCESING STEPS   '''

# TOKENIZE WORDS AND LABELS INTO LISTS

Data_list = []
Labels_list = []

for row in clean_mdf['Data']:
    
    # TOKENIZE WORDS
    words = word_tokenize(row)
    
    # CASE CONVERSION AND REMOVAL OF PUNCTUATION MARKS
    clean_words = [word.lower() for word in words if word not in set(string.punctuation)]
    
    # REMOVAL STOP WORDS
    characters_to_remove = ["haha","039","''","``","#","rt","https","â€™","â€œ","â€�","\u200b","--","n't","'s","...","//t.c", "q", ":)", ":(","<3","<br>","br"]
    clean_words = [word for word in clean_words if word not in set(stopwords.words('english'))]
    clean_words = [word for word in clean_words if word not in set(characters_to_remove)]
    
    # TRANSLATE THE DATASET TO SPANISH LANGUAGE
    
    transclean_words = []
    
    for word in clean_words:
        translated_word = translate_text(word)
        transclean_words.append(translated_word.lower())
    
    myData = " ".join(transclean_words)
    Data_list.append(myData)
    print(myData)
    
for myLabel in clean_mdf['Label']:
    
    Labels_list.append(myLabel)

# COMBINE THEM TO CREATE CLEANDATA.CSV
combined = zip(Data_list, Labels_list)


'''    CREATE CLEANDATA.CSV   '''

with open('ESPformspring_cleandata.csv', 'w', newline='') as myFile:
    writer = csv.writer(myFile, delimiter='|')
    writer.writerow(['SpanishData', 'BullyingLabel'])
    writer.writerows(combined)

print("Writing ESPformspring_cleandata.csv complete")

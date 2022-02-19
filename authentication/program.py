

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
# os.environ["CUDA_VISIBLE_DEVICES"]="-1,0"    
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())


import pandas as pd
import tensorflow

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

# from keras.utils import np_utils
# from hyperopt import Trials, STATUS_OK, tpe
# from hyperas import optim
# from hyperas.distributions import choice, uniform



import warnings 
warnings.filterwarnings("ignore")

length=20

df= pd.read_excel("Final_Dataset.xlsx")
count = df['Property'].value_counts() 
print(count) 
tokenizer = Tokenizer(lower=False)
tokenizer.fit_on_texts(df['Sequence'])
word2integer = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(df['Sequence'])
maximum_length=max(len(s) for s in sequences)
minimum_length=min(len(s) for s in sequences)


model_1 = tf.keras.models.load_model('model_1.h5')
# model_2 = tf.keras.models.load_model('model_2.h5')
# model_3 = tf.keras.models.load_model('model_3.h5')
# model_4 = tf.keras.models.load_model('model_4.h5')
# model_5 = tf.keras.models.load_model('model_5.h5')


import pandas as pd
from Bio.SeqIO import parse 

filename="Staphylococcus_warneri"
df_sequences=pd.DataFrame()
file = open("Staphylococcus_warneri.fasta") 
records = parse(file, "fasta") 
ll=0
for record in records: 
    ll=ll+1
    df_sequences=df_sequences.append({'Description': str(record.description),'string_values': str(record.seq)}, ignore_index=True) # Store protein sequences into dataframe 


df_sequences


A=length
B=length
dataframe=pd.DataFrame()

for ii in range(A,B+1):
    Length=ii
    for aa in range(df_sequences.shape[0]): 
        String_6LZG=df_sequences['string_values'].iloc[aa]
        for i in range(0,len(String_6LZG)):
            if(len(String_6LZG[i:i+Length:1])==Length):
                dataframe=dataframe.append({'Sequence':" ".join(String_6LZG[i:i+Length:1])}, ignore_index=True)
                

print("No of Sequences from fasta file: {}" .format(ll))
print("No of subsequences of length betweeen A={} and B={} stored in excel={}".format(A,B,dataframe.shape[0]))                
dataframe

# Consider sequences which contains 20 Proteinogenic and remove others

df=pd.DataFrame()

def search(value):
    Proteinogenic ="ACDEFGHIKLMNPQRSTVWY "
    if (Proteinogenic.find(value) == -1):
        return(-1)
    else:
        return(0)
    
for i in range(0,dataframe.shape[0]):
    ans=0
    for j in dataframe.Sequence[i]:
        ans=ans+search(j)
    if(ans==0):
         df=df.append(dataframe.loc[i],ignore_index=True)


df



sequences = tokenizer.texts_to_sequences(df['Sequence'])
data = pad_sequences(sequences, maxlen=maximum_length)




predict_prob = model_1.predict(data, verbose = 2)
check_df = pd.DataFrame(list(zip(df.Sequence.values,
predict_prob )), columns = ['Sequence',
'Prediction Probability'])

Model_1 = check_df.copy()


# predict_prob = model_2.predict(data, verbose = 2)
# check_df = pd.DataFrame(list(zip(df.Sequence.values,
# predict_prob )), columns = ['Sequence',
# 'Prediction Probability'])


# Model_2 = check_df.copy()

# predict_prob = model_3.predict(data, verbose = 2)
# check_df = pd.DataFrame(list(zip(df.Sequence.values,
# predict_prob )), columns = ['Sequence',
# 'Prediction Probability'])


# Model_3 = check_df.copy()

# predict_prob = model_4.predict(data, verbose = 2)
# check_df = pd.DataFrame(list(zip(df.Sequence.values,
# predict_prob )), columns = ['Sequence',
# 'Prediction Probability'])


# Model_4 = check_df.copy()


# predict_prob = model_5.predict(data, verbose = 2)
# check_df = pd.DataFrame(list(zip(df.Sequence.values,
# predict_prob )), columns = ['Sequence',
# 'Prediction Probability'])


# Model_5 = check_df.copy()

Final=pd.DataFrame(columns = ['Sequence',
'Prediction Probability'])

for i in range(0,Model_1.shape[0]):

    # P_2=Model_2['Prediction Probability'].values[i]
    # P_3=Model_3['Prediction Probability'].values[i]
    # P_4=Model_4['Prediction Probability'].values[i]
    # P_5=Model_5['Prediction Probability'].values[i]
    
    # P=(P_5+P_4)/2
    
    # Model_1['Prediction Probability'].values[i]=P
    Final=Final.append(Model_1.iloc[i], ignore_index = True)

# Creating a column Prediction
Final['Prediction'] =1

# Updating the value of column Prediction 
for i in range(0,Final.shape[0]):
    if(Final['Prediction Probability'].values[i]>=0.5):
        Final['Prediction'].values[i]=1
    else:
        Final['Prediction'].values[i]=0

print(Final)

Final.to_excel(filename+"Ans"+".xlsx", header=True, index=False )






def predict_prob(length,filename):
    import pandas as pd
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import tensorflow as tf
    from tensorflow.python.client import device_lib
    import pandas as pd
    import tensorflow
    from keras.preprocessing.text import Tokenizer
    from keras.preprocessing.sequence import pad_sequences
    import warnings
    
    warnings.filterwarnings("ignore")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_1 = tf.keras.models.load_model(BASE_DIR+"/authentication/model_1.h5")
    
    df = pd.read_excel(BASE_DIR+"/authentication/Final_Dataset.xlsx")
    count = df['Property'].value_counts()
    print(count)
    tokenizer = Tokenizer(lower=False)
    tokenizer.fit_on_texts(df['Sequence'])
    word2integer = tokenizer.word_index
    sequences = tokenizer.texts_to_sequences(df['Sequence'])
    maximum_length = max(len(s) for s in sequences)
    minimum_length = min(len(s) for s in sequences)

    import pandas as pd
    from Bio.SeqIO import parse

    df_sequences = pd.DataFrame()
    file = open(BASE_DIR+'/'+filename)
    print(BASE_DIR+'/'+filename)

    records = parse(file, "fasta")

    ll = 0
    for record in records:
        ll = ll+1

        df_sequences = df_sequences.append({'Description': str(record.description), 
                                            'string_values': str(record.seq)}, 
                                        ignore_index=True)

    dataframe = pd.DataFrame()

    Length = int(length)
    for aa in range(df_sequences.shape[0]):
        String_6LZG = df_sequences['string_values'].iloc[aa]
        for j in range(0, len(String_6LZG)):

            if(len(String_6LZG[j:j+Length:1]) == Length):
                dataframe = dataframe.append({'Sequence': " ".join(String_6LZG[j:j+Length:1])}, 
                                            ignore_index=True)

    print("No of Sequences from fasta file: {}" .format(ll))

    dataframe

    df = pd.DataFrame()

    def search(value):
        Proteinogenic = "ACDEFGHIKLMNPQRSTVWY "
        if (Proteinogenic.find(value) == -1):
            return(-1)
        else:
            return(0)

    for i in range(0, dataframe.shape[0]):
        ans = 0
        for j in dataframe.Sequence[i]:
            ans = ans+search(j)
        if(ans == 0):
            df = df.append(dataframe.loc[i], ignore_index=True)

    df

    sequences = tokenizer.texts_to_sequences(df['Sequence'])
    data = pad_sequences(sequences, maxlen=maximum_length)

    predict_prob = model_1.predict(data, verbose=2)
    check_df = pd.DataFrame(list(zip(df.Sequence.values,
                                    predict_prob)), columns=['Sequence',
                                                            'Prediction_Probability'])

    Model_1 = check_df.copy()

    Final = pd.DataFrame(columns=['Sequence',
                                'Prediction_Probability'])

    for i in range(0, Model_1.shape[0]):

        Final = Final.append(Model_1.iloc[i], ignore_index=True)

    Final['Prediction'] = 1

    for i in range(0, Final.shape[0]):
        if(Final['Prediction_Probability'].values[i] >= 0.5):
            Final['Prediction'].values[i] = 1
        else:
            Final['Prediction'].values[i] = 0
            
    file.close()
            
    return Final

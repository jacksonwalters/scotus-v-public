from tensorflow import keras
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
#from load_public_data import anes_codebook

#load a CNN binary classifier which is trained on political text data
if __name__ == "__main__":
    #load labeled data
    project_path = '/Users/jacksonwalters/Documents/GitHub/scotus-v-public/'
    data_path = 'data/training/all_labeled_tweets.txt'
    file_path = project_path + data_path
    df = pd.read_csv(file_path, names=['sentence', 'label'], sep='\t')
    sentences = df['sentence'].values
    y = df['label'].values  #tweet sentence sentiment labels. 0 = negative, 1 = positive
    #split the sentences into training data and test data
    sentences_train, sentences_test, y_train, y_test = train_test_split(sentences, y, test_size=0.25, random_state=1000)
    #build vectorizer and set padding param
    tokenizer = Tokenizer(num_words=5000)
    tokenizer.fit_on_texts(sentences_train)
    vocab_size = len(tokenizer.word_index) + 1
    maxlen = 100

    #load the model
    model = keras.models.load_model('cnn_model')

    #get predictions for some example sentences
    examples = ["fake news","mike pence","witch hunt","law and order","health care","kamala harris"]
    X_ex_sent = tokenizer.texts_to_sequences(examples)
    X_ex_sent = pad_sequences(X_ex_sent, padding='post', maxlen=maxlen)
    predictions = model.predict(X_ex_sent)
    pred_dict = {examples[i]:predictions[i][0] for i in range(len(examples))}
    print(pred_dict)

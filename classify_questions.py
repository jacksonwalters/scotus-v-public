from tensorflow import keras
from load_public_data import anes_codebook

#place number into 3 classes {-1,0,1} based sign or if close to zero
def classify(q):
    return 0 if abs(q) <= .1 else q/abs(q)

#PLACEHOLDER. use Keras text classifier
#https://github.com/tensorflow/docs/blob/master/site/en/tutorials/keras/text_classification_with_hub.ipynb
#would need to upload formatted data for political bias classification
if __name__ == "__main__":
    model = keras.models.load_model('keras_model') #load the trained CNN text classifier
    examples = ["This movie is great.","This movie is alright.","This movie is bad."] #some examples for IMBD data
    preds = model.predict(examples) #get numeric predictions
    print([classify(pred[0]) for pred in preds]) #print classified results
    #PLACEHOLDER. 'example' for classification of ANES questions
    codebook_df = anes_codebook()
    questions = list(codebook_df["question"])
    preds = model.predict(questions[:10])
    print([classify(pred[0]) for pred in preds])

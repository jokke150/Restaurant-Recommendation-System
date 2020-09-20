import pickle

from keras.models import load_model



def ident_speech_act(model, label_encoder, text):
    prediction = model.predict(text)
    speech_act = label_encoder.inverse_transform(prediction)
    return speech_act

if __name__ == '__main__':
    # load model
    model = load_model('speech_act_model.h5')

    # load label encoder
    infile = open('label_encoder.pickle','rb')
    label_encoder = pickle.load(infile)
    infile.close()

    # how to predict: TODO: Does mot work currently
    speech_act = ident_speech_act(model, label_encoder, 'hindi food is okay'.split())
    print(speech_act)

import pickle

from learners.neural_net import predict_nn, load_nn

if __name__ == '__main__':
    tokenizer, model, label_encoder = load_nn()
    speech_act = predict_nn('hindi food is okay', tokenizer, model, label_encoder)
    print(speech_act)



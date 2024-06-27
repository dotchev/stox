import pickle

def save_file(symbol, data):
    fname = 'data/' + symbol
    with open(fname, 'wb') as file:
        pickle.dump(data, file)

def load_file(fname):
    with open(fname, 'rb') as file:
        return pickle.load(file)
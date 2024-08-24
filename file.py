import pickle
import os
import json

option_leverage_dir = 'data/option_leverage'

def save_file(symbol, data):
    fname = 'data/' + symbol
    with open(fname, 'wb') as file:
        pickle.dump(data, file)

def load_file(fname):
    with open(fname, 'rb') as file:
        return pickle.load(file)
    
def save_option_leverage(symbol, data):
    os.makedirs(option_leverage_dir, exist_ok=True)
    with open(f'{option_leverage_dir}/{symbol}.json', 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)

def load_all_option_leverage():
    result = {}
    for fname in os.listdir(option_leverage_dir):
        if not fname.endswith('.json'):
            continue
        symbol = fname.removesuffix('.json')
        with open(option_leverage_dir + '/' + fname, 'r') as file:
            data = json.load(file)

        # Convert keys from strings to numbers
        data = {int(key): value for key, value in data.items()}

        result[symbol] = data
    
    return result

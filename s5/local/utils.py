
import os
import re
import json
import random
from itertools import chain
from collections import Counter
from imblearn.over_sampling import RandomOverSampler



def load_phone_symbol_table(filename):
    #print("load_phone_symbol_table")
    if not os.path.isfile(filename):
        return None, None
    int2sym = {}
    sym2int = {}
    with open(filename, 'r') as f:
        for line in f:
            sym, idx = line.strip('\n').split(' ')
            idx = int(idx)
            int2sym[idx] = sym
            sym2int[sym] = idx
    return sym2int, int2sym


def load_human_scores(filename, floor=0.1):
    with open(filename) as f:
        info = json.load(f)
    score_of = {}
    phone_of = {}
    for utt in info:
        phone_num = 0
        for word in info[utt]['words']:
            #print(word)
            assert len(word['phones']) == len(word['phones-accuracy'])
            for i, phone in enumerate(word['phones']):
                key = f'{utt}.{phone_num}'
                phone_num += 1
                phone_of[key] = phone
                #score_of[key] = round_score(word['phones-accuracy'][i], floor)
                #print("warning : socres round !!!")
                score_of[key] = word['phones-accuracy'][i]
    return score_of, phone_of


def balanced_sampling(x, y):
    sampler = RandomOverSampler()
    return sampler.fit_resample(x, y)



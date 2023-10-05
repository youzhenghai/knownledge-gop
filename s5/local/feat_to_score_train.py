# This script phone-level SVC model .
import sys
import argparse
import pickle
import kaldi_io
import numpy as np
import random
from concurrent.futures import ProcessPoolExecutor
from sklearn.svm import SVC  # <-- Change from SVR to SVC
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, GridSearchCV
from utils import (load_phone_symbol_table,
                   load_human_scores,
                   add_more_negative_data)



def get_args():
    parser = argparse.ArgumentParser(
        description='Train a simple polynomial regression model to convert '
                    'gop into human expert score',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--phone_symbol_table', type=str, default='',
                        help='Phone symbol table, used for detect unmatch '
                             'feature and labels')
    parser.add_argument('--nj', type=int, default=1, help='Job number')
    parser.add_argument('feature_scp',
                        help='Input gop-based feature file, in Kaldi scp')
    parser.add_argument('human_scoring_json',
                        help='Input human scores file, in JSON format')
    parser.add_argument('model', help='Output the model file')
    sys.stderr.write(' '.join(sys.argv) + "\n")
    args = parser.parse_args()
    return args

class RandomClassifier:
    def fit(self, *args, **kwargs):
        pass

    def predict(self, X):
        return [random.choice([0, 1]) for _ in range(len(X))]


def train_model_for_phone(label_feat_pairs, ph):
    weights = {0: 3, 1: 1}  
    #model = SVC() 
    model = SVC(class_weight=weights)
    labels, feats = list(zip(*label_feat_pairs))
    labels = np.array(labels)  
    feats = np.array(feats).reshape(-1, len(feats[0]))
    print(f"fitting '{ph}' model ")

    try:
        # grid_search.fit(X_train, y_train)
        model.fit(feats, labels)
   
    except Exception as e:
        print(f"Error processing phoneme {ph}: {e}")
        model = RandomClassifier()
        # If training errors , then use a random classifier
        return model

    
    return model


def main():
    args = get_args()

    # Phone symbol table
    _, phone_int2sym = load_phone_symbol_table(args.phone_symbol_table)

    # Human expert scores
    score_of, phone_of = load_human_scores(args.human_scoring_json, floor=1)

    # Prepare training data
    train_data_of = {}
    for ph_key, feat in kaldi_io.read_vec_flt_scp(args.feature_scp):
        if ph_key not in score_of:
            print(f'Warning: no human score for {ph_key}')
            continue
        ph = int(feat[0])
        if phone_int2sym is not None:
            if phone_int2sym[ph] != phone_of[ph_key]:
                print(f'feat train {ph_key} Unmatch feat & scores : {phone_int2sym[ph]} <--> {phone_of[ph_key]} ')
                continue
        score = score_of[ph_key]
        train_data_of.setdefault(ph, []).append((score, feat[1:]))

    # Train models
    with ProcessPoolExecutor(args.nj) as ex:
        future_to_model = [(ph, ex.submit(train_model_for_phone, pairs, ph))
                        for ph, pairs in train_data_of.items()]
        model_of = {ph: future.result() for ph, future in future_to_model if future.result() is not None}

    # Write to file
    with open(args.model, 'wb') as f:
        pickle.dump(model_of, f)


if __name__ == "__main__":
    main()

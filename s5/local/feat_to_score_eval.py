# This script does phone-level pronunciation scoring in SVC by GOP features .

import sys
import argparse
import pickle
import kaldi_io
import numpy as np
import random
from utils import load_phone_symbol_table

ini_flag = None

class RandomClassifier:
    def fit(self, *args, **kwargs):
        pass

    def predict(self, X):
        return [random.choice([0, 1]) for _ in range(len(X))]

def get_args():
    parser = argparse.ArgumentParser(
        description='Phone-level scoring.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('model', help='Input the model file')
    parser.add_argument('--phone_symbol_table', type=str, default='',
                        help='Phone symbol table, used for detect unmatch '
                             'feature and labels')
    parser.add_argument('feature_scp',
                        help='Input gop-based feature file, in Kaldi scp')
    parser.add_argument('output', help='Output the predicted file')
    sys.stderr.write(' '.join(sys.argv) + "\n")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    # Phone symbol table
    _, phone_int2sym = load_phone_symbol_table(args.phone_symbol_table)

    with open(args.model, 'rb') as f:
        model_of = pickle.load(f)

    feats_for_phone = {}
    idxs_for_phone = {}
    for ph_key, feat in kaldi_io.read_vec_flt_scp(args.feature_scp):
        ph = int(feat[0])
        feats_for_phone.setdefault(ph, []).append(feat[1:])
        idxs_for_phone.setdefault(ph, []).append(ph_key)

    with open(args.output, 'wt') as f:
        for ph in feats_for_phone:
            feats = np.array(feats_for_phone[ph])
            try:
                labels = model_of[ph].predict(feats)
            except KeyError:
                print(f"Training does not include phone ID {ph}, or key err, skipping this phone")
                continue
            for ph_key, label in zip(idxs_for_phone[ph], labels):
                f.write(f'{ph_key}\t{label}\t{ph}\n')

if __name__ == "__main__":
    main()

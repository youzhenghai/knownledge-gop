# This script draw PR diagram
import sys
import shutil
import os
import argparse
import pickle
import kaldi_io
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from utils import load_phone_symbol_table, load_human_scores, balanced_sampling


def get_args():
    parser = argparse.ArgumentParser(
        description='Train a simple polynomial regression model to convert '
                    'gop into human expert score',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--phone_symbol_table', type=str, default='',
                        help='Phone symbol table, used for detect unmatch '
                             'feature and labels.')
    parser.add_argument('--nj', type=int, default=1, help='Job number')
    parser.add_argument('gop_scp', help='Input gop file, in Kaldi scp')

    parser.add_argument('human_scoring_json',
                        help='Input human scores file, in JSON format')
    parser.add_argument('save_scp', help='save')
    parser.add_argument('--ph_need', nargs='+', type=int, default=[101], help='ph feats to save')

    sys.stderr.write(' '.join(sys.argv) + "\n")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    # Phone symbol table
    _, phone_int2sym = load_phone_symbol_table(args.phone_symbol_table)
    #print(phone_int2sym)
    # Human expert scores
    score_of, phone_of = load_human_scores(args.human_scoring_json, floor=1)

    # Prepare training data
    train_data_of = {}
    test_data_of = {}
    phone_number = len(phone_int2sym)
    print(str(2*phone_number))

    #output_file = open("key_gop.txt", "w")
    for key, gops in kaldi_io.read_post_scp(args.gop_scp):
        for i, [(ph, gop)] in enumerate(gops):
            #print(phone_int2sym[ph])
            
            ph_key = f'{key}.{i}'
            if ph_key not in score_of:
                print(f'Warning: no human score for {ph_key}')
                continue
            if phone_int2sym is not None and phone_int2sym[ph] != phone_of[ph_key]:
                print(f'{ph_key} train gop Unmatch: {phone_int2sym[ph]} <--> {phone_of[ph_key]} ')
                #print(ph_key)
                continue
            score = score_of[ph_key]
            train_data_of.setdefault(ph, []).append((score, gop))

    output_dir_train = args.save_scp    
    output_dir_feats = "feats_" + args.save_scp 

    if os.path.exists(output_dir_train):
        shutil.rmtree(output_dir_train)
        print("The output_dir_train has been deleted successfully!")
    
    if os.path.exists(output_dir_feats):
        shutil.rmtree(output_dir_feats)
        print("The output_dir_train has been deleted successfully!")
        
    os.makedirs(output_dir_train, exist_ok=True)  
    os.makedirs(output_dir_feats, exist_ok=True)  


    for ph_tr, gop_data in train_data_of.items():
        filename = os.path.join(output_dir_train, f"{ph_tr}_data.txt")  
        with open(filename, 'w') as file:
            for score_, gop_ in gop_data:
                gop_ = np.exp(gop_)
                file.write(f"{gop_}\t{score_}\n")
    
   

    # for ph_te, features in train_data_of_feats.items():
    #     if ph_te in args.ph_need:
    #         filename_te = os.path.join(output_dir_feats, f"{ph_te}_feats.txt")  
            
    #         with open(filename_te, 'w') as file:
    #             for score_t, feat in features:
    #                 lpps = feat[:phone_number]
    #                 lprs = feat[phone_number:]
    #                 file.write(f"score: {score_t}\tlpp: {lpps[ph_te]}\tlppmax: {np.max(lpps)}\tlppslen: {len(lpps)}\tlprslen: {len(lprs)}\tlpps: {lpps}\tlprs: {lprs}\n")




if __name__ == "__main__":
    main()

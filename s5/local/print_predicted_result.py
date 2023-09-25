
# This script compares the predicted output and the label and prints the result.

import sys
import argparse
import numpy as np
from sklearn import metrics
from utils import load_human_scores, load_phone_symbol_table

#shengmus = ['b','p','d','t','g','k','f','h','x','sh','r','s','z','c','zh','ch','j','q','m','n','l','*']
#yunmus = ['a','o','e','i','ii','iii','u','v','er','ai','ei','ao','ou','iu','ia','ie','ua','uo','ve','iao','uai','an','ang','ian','uan','un','ui','van','en','eng','in','ing','vn','iang','uang','ong','iong','*']


def get_args():
    parser = argparse.ArgumentParser(
        description='Phone-level scoring.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--write', type=str, default='/dev/null',
                        help='Write a result file')
    parser.add_argument('--phone_symbol_table', type=str, default='',
                        help='Phone symbol table, used for detect unmatch '
                             'feature and labels')
    parser.add_argument('human_scoring_json',
                        help='Input human scores file, in JSON format')
    parser.add_argument('predicted', help='The input predicted file')
    sys.stderr.write(' '.join(sys.argv) + "\n")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    score_of, phone_of = load_human_scores(args.human_scoring_json, floor=1)
    _, phone_int2sym = load_phone_symbol_table(args.phone_symbol_table)

    #y_true_ini = []
    #y_pred_ini = []
    #y_true_vow = []
    #y_pred_vow = []
    y_true = []
    y_pred = []

    #word_true = []
    #word_pred = []

    with open(args.predicted, 'rt') as f, open(args.write, 'wt') as fw:
        for line in f:
            fields = line.strip('\n').split('\t')
            if len(fields) == 4:
                key, label, ph, gop_exp = fields
                gop_exp = float(gop_exp)          
            elif len(fields) == 3:
                key, label, ph = fields
                    
            else:
                print("Invalid input format")            
            ph = int(ph)
            score = float(label)      

            if key not in score_of:
                print(f'Warning: no human score for {key}')
                continue
            if phone_int2sym is not None and phone_int2sym[ph] != phone_of[key]:
                print(f'predicted Unmatch: {phone_int2sym[ph]} <--> {phone_of[key]} ')
                continue
            if score_of[key] == 0 or score_of[key] == 1:
                #print(int(score_of[key]))
                # if (phone_of[key][-1]).isdigit(): 
                #     y_true_vow.append(score_of[key])
                #     y_pred_vow.append(score)
                # else :
                #     y_true_ini.append(score_of[key])
                #     y_pred_ini.append(score)
                y_true.append(score_of[key])
                y_pred.append(score)

                fw.write(f'{key}\t{ph}\t{score_of[key]:.1f}\t{score:.1f}\n')
            elif score_of[key] == 0.5:  # Improve the accuracy of scores
                pass
            else:
                print("human scores err")

    print("ALL:")
    #print(f'CE (Log): {metrics.log_loss(y_true, prob_pos):.2f}')
    print(f'Corr: {np.corrcoef(y_true, y_pred)[0][1]:.2f}')
    print(metrics.classification_report(y_true, y_pred))


    # print("initial:")
    # #print(f'CE (Log): {metrics.log_loss(y_true_ini, y_pred_ini):.2f}')
    # print(f'Corr: {np.corrcoef(y_true_ini, y_pred_ini)[0][1]:.2f}')
    # print(metrics.classification_report(y_true_ini, y_pred_ini))

    # print("vowel:")
    # #print(f'CE (Log): {metrics.log_loss(y_true_vow, y_pred_vow):.2f}')
    # print(f'Corr: {np.corrcoef(y_true_vow, y_pred_vow)[0][1]:.2f}')
    # print(metrics.classification_report(y_true_vow, y_pred_vow))

    # detect_y_true = [1 - val for val in y_true]
    # detect_y_pred = [1 - val for val in y_pred]

    # tn, fp, fn, tp = metrics.confusion_matrix(detect_y_true, detect_y_pred).ravel()

    # # Calculate TPR and FPR
    # tpr = tp / (tp + fn)
    # fpr = fp / (fp + tn)

    # print("TPR (Sensitivity):", tpr)
    # print("FPR (1 - Specificity):", fpr)

    # #  Roc_ Curve to obtain FPR, TPR, threshold
    # fpr_values, tpr_values, thresholds = metrics.roc_curve(detect_y_true, detect_y_pred)

    # print("FPR values from roc_curve:", fpr_values)
    # print("TPR values from roc_curve:", tpr_values)


if __name__ == "__main__":
    main()

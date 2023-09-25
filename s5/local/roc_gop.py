import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc,precision_recall_curve
from utils import load_phone_symbol_table, load_human_scores, balanced_sampling
import argparse
parser = argparse.ArgumentParser(description='data_folder')
parser.add_argument('path', help='Input path')
# parser.add_argument('--phone-symbol-table', type=str, default='',
#                         help='Phone symbol table, used for detect unmatch '
#                              'feature and labels.')
args = parser.parse_args()
data_folder = args.path


# # Phone symbol table
# _, phone_int2sym = load_phone_symbol_table(args.phone_symbol_table)


all_y_true = []
all_y_scores = []
zero_counts = {}

bad_radio_counts = {}  

log_folder = os.path.join(data_folder, "log")
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_file_path = os.path.join(log_folder, "all_error_log")
sys.stderr = open(log_file_path, 'w')



for filename in os.listdir(data_folder):
    if filename.endswith(".txt"):
        ph = int(filename.split("_")[0])  
        file_path = os.path.join(data_folder, filename)

        data = np.loadtxt(file_path)
        # Check if the data file has only one line and reshape data 
        if data.ndim == 1:
            data = data.reshape(1, -1)
        if data.ndim == 0:       
            print("warning err write in " + filename)

        y_scores = data[:, 0]
        #y_scores = np.exp(y_scores)
        y_true = data[:, 1]

        # # 统计scores为0的计数和0的个数
        # zero_count = np.sum(y_true == 0)
        # bad_count = np.sum(y_scores < theshold_my)
        # bad_radio_count = bad_count/(np.size(y_scores)
        # zero_counts[ph] = zero_count
        # bad_radio_counts[ph] = bad_radio_count

        all_y_true.extend(y_true)
        all_y_scores.extend(y_scores)

all_y_true = np.array(all_y_true)
all_y_scores = np.array(all_y_scores)
assert len(all_y_true) == len(all_y_scores)

# permuted_indices = np.random.permutation(len(all_y_true))
# all_y_true = all_y_true[permuted_indices]
# all_y_scores = all_y_scores[permuted_indices]

#Scores check
#all_y_scores = np.exp(all_y_scores)
out_of_range = np.any((all_y_scores < 0) | (all_y_scores> 1))
#err_ph = filename
# If out_of_range is True, it means there are values not in the range [0, 1]
if out_of_range:
    print(filename)
    print("err There are values in all_y_scores_exp that are not in the range [0, 1].")
    sys.exit()
# #print(args.exp)
# if args.exp:
#     #all_y_scores = np.exp(all_y_scores )
#     out_of_range = np.any((all_y_scores < 0) | (all_y_scores> 1))
#     # If out_of_range is True, it means there are values not in the range [0, 1]
#     if out_of_range:
#         print("err There are values in all_y_scores_exp that are not in the range [0, 1].")
#         print(out_of_range)
#         sys.exit()
# else:
#     all_y_scores = np.clip(all_y_scores, 0, 1)

all_zero_ratio = np.mean(all_y_true == 0)
all_zero_count = np.sum(all_y_true == 0)
#all_zero_count = sum(zero_counts.values())
all_min_score = np.min(all_y_scores)
#my_zero_FNR = all_zero_count / len(all_y_ture)

# Exchange sample labels and corresponding y_scores value
# In MD  incorrect pronunciation is positive , correct pronunciation is negative
all_y_true = 1 - all_y_true
all_y_scores = 1 - all_y_scores
# Calculate the false positive rate, true positive rate, and threshold of the ROC curve
fpr, tpr, thresholds = roc_curve(all_y_true, all_y_scores)
# Calculate Area Under Curve (AUC)
roc_auc = auc(fpr, tpr)

# Find the index for the optimal threshold point
youden_index = np.argmax(tpr - fpr)
best_threshold = thresholds[youden_index]
best_fpr = fpr[youden_index]
best_tpr = tpr[youden_index]




# PR （Precision）（Recall）
precision, recall, thresholds_pr = precision_recall_curve(all_y_true, all_y_scores)
# precision index
index = np.abs(precision - 0.28).argmin()

required_recall = recall[index]

if index < len(thresholds_pr):
    required_precision = precision[index]
    required_threshold = thresholds_pr[index]
    required_recall = recall[index]
else:
    required_threshold = "Not Available"

print(f"required_threshold: {required_threshold} ,{required_precision} , {required_recall}")
roc_index = np.abs(thresholds - required_threshold).argmin()

# Find the closest precision index
index2 = np.abs(recall - 0.61).argmin()
required_recall2 = recall[index2]
if index2 < len(thresholds_pr):
    required_precision2 = precision[index2]
    required_threshold2 = thresholds_pr[index2]
    required_recall2 = recall[index2]
else:
    required_threshold2 = "Not Available"

print(f"required_threshold2: {required_threshold2} ,{required_precision2} , {required_recall2}")
roc_index2 = np.abs(thresholds - required_threshold2).argmin()



pr_auc = auc(recall, precision)
f1_scores = 2 * (precision * recall) / (precision + recall)
best_threshold_pr_index = np.argmax(f1_scores)
best_threshold_pr = thresholds_pr[best_threshold_pr_index]
best_precision = precision[best_threshold_pr_index]
best_recall = recall[best_threshold_pr_index]

print(f"my need  {best_precision},{best_recall}.{f1_scores[best_threshold_pr_index]},{best_threshold_pr}")

# draw ROC

plt.figure(figsize=(10, 7))  
plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve')
plt.scatter(0.03 ,  0.16,  color='black', label ="SVM(Random)",s=50)
plt.scatter(0.13, 0.53,  color='red',label = "SVM(Knowledge)", s=50)
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')

plt.xlim([0.0, 0.8])
plt.ylim([0.0, 0.8])
plt.xlabel('False Positive Rate', fontsize=24)  
plt.ylabel('True Positive Rate', fontsize=24)  

plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

plt.legend(loc="lower right", fontsize=22)  


save_path = os.path.join(data_folder, "ROC.png")
plt.savefig(save_path)
plt.close()


# draw PR
plt.figure(figsize=(10, 7))  
plt.scatter( 0.18,0.23 ,  color='black', label ="SVM(Random)",s=50,marker='x')
plt.scatter( 0.527, 0.203,  color='red',label = "SVM(Knowledge)", s=50,marker='^')
plt.scatter( 0.43, 0.14,  color='navy',label = "ERN(0.01)", s=50)
plt.plot([0, 1], [all_zero_ratio, all_zero_ratio], linestyle='--', color='gray', lw=2,label='Random')
plt.plot(recall , precision,color='green', lw=2, label='GOP PR curve')

plt.xlim([0.0, 0.95])
plt.ylim([0.0, 0.95])
plt.ylabel('Precision', fontsize=24)
plt.xlabel('Recall', fontsize=24)
plt.legend(loc="upper right", fontsize=22)

plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

save_path_pr = os.path.join(data_folder, "PR_new.pdf")
plt.savefig(save_path_pr)
plt.close()

sorted_zero_counts = sorted(zero_counts.items(),key=lambda d: d[1], reverse=True)
#print(sorted_zero_counts)
# with open(os.path.join(data_folder, "a_ph_zero"), "w") as f:
#     #f.write(f"my_zero_FNR : {my_zero_FNR}\n")
#     for ph, zero_count in sorted_zero_counts:
#         all_zero_ratio = zero_count / all_zero_count
#         f.write(f"Phoneme {phone_int2sym[ph]}: Zero Count = {zero_count}, Zero Ratio = {all_zero_ratio}\n")


# sorted_bad_radio_counts = sorted(bad_radio_counts.items(),key=lambda d: d[1], reverse=True)
# #print(sorted_zero_counts)
# with open(os.path.join(data_folder, "scores_bad"), "w") as f:
#     for bad_ph, temp_bad_radio_count in sorted_bad_radio_counts:
#         f.write(f"Phoneme {phone_int2sym[bad_ph]}: Bad Ratio = {temp_bad_radio_count}\n")

# print("For ROC curve at best threshold:")
# print(f"Best Threshold: {best_threshold:.2f}")
# print(f"FPR: {best_fpr:.2f}")
# print(f"TPR: {best_tpr:.2f}")


# print("For PR curve at best threshold:")
# print(f"Best Threshold: {best_threshold_pr:.2f}")
# print(f"Precision: {best_precision:.2f}")
# print(f"Recall: {best_recall:.2f}")


sys.stderr = sys.__stderr__


if os.stat(log_file_path).st_size == 0:
    
    os.remove(log_file_path)


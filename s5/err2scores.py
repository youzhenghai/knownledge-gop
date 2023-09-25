import json
nested_dict = {}

import argparse

parser = argparse.ArgumentParser(description='data_folder')
parser.add_argument('input_path', help='Input path')
parser.add_argument('scores_path', help='Input path')
parser.add_argument('output_path', help='output path')
parser.add_argument('phone_path', help='path path')
args = parser.parse_args()


pos_scores_path = args.input_path
scores_path = args.scores_path
output_path = args.output_path
phone_path = args.phone_path   # pure-phone


phone_dict = {}
with open(phone_path, 'r') as file:
    lines = file.readlines()
    for line in lines:
        line_data = line.split()
        phone_id = line_data[1]
        if phone_id not in phone_dict:
            phone_dict[phone_id] = []
        phone_dict[phone_id].append(line_data[0])

with open(pos_scores_path, "r") as file:
    for line in file:
        data = line.strip()

        sentence_index = data.split()[0]

        pos_data = data.replace(sentence_index, "").strip().split("pos:")

        inner_dict = {}

        for pos in pos_data[1:]:
            pos_values = pos.strip().split()
            pos_num = int(pos_values[0])
            ph = int(pos_values[1])
            next_ph = int(pos_values[2])
            inner_dict[pos_num] = {"ph": ph, "next_ph": next_ph}

        nested_dict[sentence_index] = inner_dict
with open(scores_path, "r") as file:
    scores_dict = json.load(file)

phone_accuracy_sum = 0

for sentence_index, pos_dict in nested_dict.items():
    if sentence_index in scores_dict:
        
        for pos_num, values in pos_dict.items():
            iter = -1
            
            for word in scores_dict[sentence_index]['words']:
                iter += 1
                #print(pos_num)
                phone_accuracy = scores_dict[sentence_index]['words'][iter]['phones-accuracy']
                #print("here: " + sentence_index + " " + word['text'] ) 
                #phone_accuracy_sum += len(phone_accuracy)                
                if len(phone_accuracy)  <= pos_num:                   
                    pos_num -= len(phone_accuracy)                  
                else:
                    #print("change: " + sentence_index + " " + word['text'] ) 
                    #print(pos_num)
                    #print(scores_dict[sentence_index]['words'][iter]['phones-accuracy'])
                    scores_dict[sentence_index]['words'][iter]['phones-accuracy'][pos_num] = 0
                    scores_dict[sentence_index]['words'][iter]['phones'][pos_num] = str(phone_dict[str(values["next_ph"])]).strip("['']")
                    #print(scores_dict[sentence_index]['words'][iter]['phones-accuracy'])
                    break
#print(phone_list)\

# if os.path.exists(output_path + "/scores.json"):
#         shutil.rmtree(output_dir_feats)
#         print("The scores.json has been deleted successfully!")

with open(output_path +"/ali_err_scores.json", "w", encoding="utf-8") as file:
    json.dump(scores_dict, file, ensure_ascii=False, indent=4)

    


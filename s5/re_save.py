import json


with open('data/local/result_merge_modified.json', 'r', encoding='utf8') as f:
    data = json.load(f)


with open('data/local/scores.json', 'r', encoding='utf8') as f:
    another_data = json.load(f)


modified_data = {}

for key, value in data.items():
    if key in another_data:
        for i, word in enumerate(value['words']):
            for j, acc in enumerate(word['accuracy']):
                if another_data[key]['words'][i]['phones'][j][-1] == "5":
                    continue

                if acc >= 3:
                    another_data[key]['words'][i]['phones-accuracy'][j] = 1
                elif acc <= 1:
                    another_data[key]['words'][i]['phones-accuracy'][j] = 0
                else:

                    ####   scores maybe round
                    #print("scores err")
                    another_data[key]['words'][i]['phones-accuracy'][j] = 0.5

     
        modified_data[key] = another_data[key]


with open('data/local/scores_modified.json', 'w', encoding='utf8') as f:
    json.dump(modified_data, f, ensure_ascii=False, indent=4)

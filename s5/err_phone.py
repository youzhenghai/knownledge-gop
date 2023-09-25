import os
import sys
import random
import json

import argparse

parser = argparse.ArgumentParser(description='data_folder')
parser.add_argument('input_path', help='Input path')
parser.add_argument('output_path', help='output path')
parser.add_argument('output_all_path', help='output path')
parser.add_argument('phone_path', help='path path')
parser.add_argument('--seed', type=int, default=1453, help='seed')
args = parser.parse_args()


random.seed(args.seed)

# 指定 json 数据文件所在目录
data_directory = args.input_path

# 创建保存 替换后 的 ali-phone 数据的目录
output_directory = args.output_path
os.makedirs(output_directory, exist_ok=True)


pos_scores_path = args.output_all_path
phone_path = args.phone_path 

 #创建保存pos_cur和音素替换信息的文件
pos_scores_file = open(pos_scores_path, 'w')




# 读取phone.txt文件，构建phone_id替换字典
phone_dict = {}
with open(phone_path, 'r') as file:
    lines = file.readlines()
    for line in lines[72:]:
        line_data = line.split()
        phone_id = line_data[1]
        if phone_id not in phone_dict:
            phone_dict[phone_id] = []
        phone_dict[phone_id].append(line_data[0])



# 遍历目录下的文件
for filename in os.listdir(data_directory):
    if filename.startswith('ali-phone-json.'):
        # 构造文件路径
        file_path = os.path.join(data_directory, filename)

        # 保存处理后的数据到同名文件
        output_filename = filename.replace('ali-phone-json.', 'ali-phone.')
        output_file_path = os.path.join(output_directory, output_filename)

        # 处理文件数据
        with open(file_path, 'r') as file:
            # 读取文件内容
            data = json.load(file)

        # 对嵌套字典进行随机替换
        with open(output_file_path, 'w') as output_file:
            for sentence_id, sentence_data in data.items():
                # 创建一个列表用于记录pos_cur和音素替换信息
                pos_scores = []
                write_line = sentence_id + " "
                pos_none_count = -1

                next_ph = None
                before_ph = None

                for i, (_, pos_data) in enumerate(sentence_data.items()):
                    lim = random.random()
                    if i + 1 < len(sentence_data):
                        next_pos_data = list(sentence_data.values())[i + 1]                   
                    #print(lim)
                    if 'ph' in pos_data and 'count' in pos_data:
                        ph = pos_data['ph']
                        next_ph = next_pos_data['ph']
                        count = pos_data['count']
                        if ph != '1':
                            if lim < 0.10:
                                pos_none_count += 1
                                random_phone_id = random.choice([phone_id for phone_id in phone_dict.keys() if phone_id not in [ph,before_ph,next_ph]])
                                if random_phone_id == ph or random_phone_id == before_ph:
                                    print("random ph err")
                                    sys.exit()
                                pos_scores.append((pos_none_count, ph, random_phone_id))  # 记录pos_cur和音素替换信息
                                #print(sentence_id + " " + str(pos_none_count) + " "+ str(phone_dict[ph]) + "->" + str(phone_dict[random_phone_id]))
                                pos_data['ph'] = random_phone_id
                                before_ph  = random_phone_id
                            elif lim >=0.10:
                                pos_none_count += 1      
                                before_ph  = ph                   
                            else:
                                print("ph = 1 lim err")
                            
                        elif ph == '1':
                            before_ph  = 1 
                            pass  # 不替换音素，保持为1
                        else:
                            print("ph random err" + " lim:"+ str(lim) + " ph:"+ ph)
                    else:
                        print("ph or count err")
                    write_line += ( pos_data['ph'] + " ")*count
                    #write_line += " "
                
                output_file.write(write_line + '\n')

                # 将pos_cur和音素替换信息写入文件
                pos_scores_file.write(f"{sentence_id} ")
                for pos_score in pos_scores:
                    pos_scores_file.write(f"pos: {pos_score[0]} {pos_score[1]} {pos_score[2]} ")
                pos_scores_file.write("\n")

        
 # 关闭pos_scores文件
pos_scores_file.close()





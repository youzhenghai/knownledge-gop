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
parser.add_argument('ini_path', help='ini err path')
parser.add_argument('vow_path', help='vow err mat path')
parser.add_argument('err_path', help='confusion mat path')  # 限制所需训练的PH 测试用不需要
parser.add_argument('count_ph_path', help='test ph count')   # 测试用不需要
parser.add_argument('--seed', type=int, default=1453, help='seed') 
args = parser.parse_args()


random.seed(args.seed)
zh_count = 0
plus_err = 2
random_err_up = 0.10

# def seeded_random(ph):
#     # 使用 ph 作为种子来产生一个确定的随机序列
#     r = random.Random(ph)
#     return r.random()

# 指定 json 数据文件所在目录
data_directory = args.input_path

# 创建保存 替换后 的 ali-phone 数据的目录
output_directory = args.output_path
os.makedirs(output_directory, exist_ok=True)


pos_scores_path = args.output_all_path
phone_path = args.phone_path 

 #创建保存pos_cur和音素替换信息的文件
pos_scores_file = open(pos_scores_path, 'w')

ini_dict = {}
vow_dict = {}
err_dict = {}
with open(args.ini_path, "r") as file:
    ini_dict = json.load(file)

with open(args.vow_path, "r") as file:
    vow_dict = json.load(file)

with open(args.err_path, "r") as file:
    err_dict = json.load(file)

with open(args.count_ph_path, "r") as file:
    count_ph_dict = json.load(file)


mat_dict = {}

tone_dict = {"1": {"2": 0.03, "3": 0.006, "4": 0.017}, "2": {"1": 0.012, "3": 0.043, "4": 0.008},"3": {"1": 0.01, "2": 0.06, "4": 0.02},"4": {"1": 0.019, "2": 0.03, "3": 0.007},"5": {"1": 0.01,  "4": 0.02}}

# 读取phone.txt文件，构建phone_id替换字典
phone_dict = {}
phone_id_dict = {}
with open(phone_path, 'r') as file:
    lines = file.readlines()
    for line in lines[72:]:
        line_data = line.split()
        phone_id = line_data[1]
        phone_sym = line_data[0]
        if phone_id not in phone_dict:
            phone_dict[phone_id] = []
        phone_dict[phone_id].append(phone_sym)
        if phone_sym not in phone_id_dict:
            phone_id_dict[phone_sym] = []
        phone_id_dict[phone_sym].append(phone_id)

# 为err_dict.keys()转化为数字
err_keys_as_numbers = []

for key in err_dict.keys():
    # 这里我假设phone_id_dict[key]返回的是一个数字列表，我只取第一个数字
    if key in phone_id_dict:
        err_keys_as_numbers.append(str(phone_id_dict[key][0]))

# 为count_ph_dict.keys()转化为数字
count_ph_dict_number = []

for key in count_ph_dict.keys():
    # 这里我假设phone_id_dict[key]返回的是一个数字列表，我只取第一个数字
    if key in phone_id_dict:
        count_ph_dict_number.append(str(phone_id_dict[key][0]))

#print(phone_id_dict)

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
            all_ph_count = 0
            all_zero_count = 0
            for sentence_id, sentence_data in data.items():
                # 创建一个列表用于记录pos_cur和音素替换信息
                pos_scores = []
                write_line = sentence_id + " "
                pos_none_count = -1
                next_ph = None              
                before_ph = None           
                for i, (_, pos_data) in enumerate(sentence_data.items()):                   
                    if i + 1 < len(sentence_data):
                        next_pos_data = list(sentence_data.values())[i + 1]                   
                    #print(lim)
                    if 'ph' in pos_data and 'count' in pos_data:
                        ph = pos_data['ph']
                        #ph_flag = -1
                        # lim = seeded_random(ph)
                        # tone_lim = seeded_random(ph)
                        # random_lim = seeded_random(ph)
                        lim = random.random()
                        tone_lim = random.random()
                        random_lim = random.random()                      
                        # if ph in count_ph_dict_number and random.random() < 0.2:
                        #     lim = 100
                        #     tone_lim = 100
                        #     random_lim = 10                            
                        next_ph = next_pos_data['ph']
                        count = pos_data['count']
                        if ph != '1':
                            pos_none_count += 1                           
                            #tone err
                            tone = None
                            sum_tone_err  =  0
                            change_flag = 0
                            ph_sym = str(phone_dict[ph]).strip("['']")
                            #print(ph_sym)                            
                            if ph_sym[-1].isdigit():
                                tone = ph_sym[-1]
                                mat_dict = vow_dict
                                #ph_flag = 1                           
                                symbol = ph_sym[:-1]
                                #print(symbol)                  
                                for i, (change_tone, tone_prob) in enumerate(tone_dict[tone].items()):                         
                                    if tone_lim < sum_tone_err :  
                                                                      
                                        tone = change_tone
                                        #if symbol == 'iz':
                                        #    tone = tone
                                        change_flag = 1
                                        break
                                    sum_tone_err += (tone_prob * (int(plus_err/2)+1))
                            else :
                                tone = ""
                                mat_dict = ini_dict
                                #ph_flag = 2
                                symbol = ph_sym                           
                            #no tone phone err
                            sum_err_p = 0   
                            if symbol in mat_dict:                     
                                for i, (err_phone, err_p) in enumerate(mat_dict[symbol].items()):
                                    #if err_phone == 'spn':
                                    #    change_phone_id_temp  = '2'
                                    #else:
                                    #不同于新疆数据的，且没法有对应关系的特殊音素情况，在概率下直接转换为对应错误
                                    if err_phone == "iz" :
                                        change_phone_id_temp = str(phone_id_dict[ str(err_phone) + str(4)]).strip("['']")  
                                    elif err_phone == "er" and tone == "1":    
                                        change_phone_id_temp = str(phone_id_dict[ str(err_phone) + str(3)]).strip("['']")
                                    # elif err_phone == "ueng" and tone == "1":    
                                    #     change_phone_id_temp = str(phone_id_dict[ str(err_phone) + str(3)]).strip("['']")    
                                    else:    
                                        change_phone_id_temp  = str(phone_id_dict[ str(err_phone) + str(tone)]).strip("['']")  
                                    if  change_phone_id_temp == before_ph or change_phone_id_temp == next_ph:
                                        continue
                                    if lim < sum_err_p:
                                        symbol = err_phone                                                             
                                        change_flag = 1
                                        break
                                    sum_err_p += (err_p*plus_err)                           
                            change_phone_id = None
                            if change_flag == 1:
                                if symbol == 'iz':
                                    change_phone_id = str(phone_id_dict[ str(symbol) + str(4)]).strip("['']") 
                                elif err_phone == "er" and tone == "1":    
                                    change_phone_id_temp = str(phone_id_dict[ str(err_phone) + str(3)]).strip("['']")   
                                else:
                                    change_phone_id  = str(phone_id_dict[ str(symbol) + str(tone)]).strip("['']")  
                                if change_phone_id == before_ph  or change_phone_id == next_ph or change_phone_id == ph:
                                    change_phone_id  = random.choice([phone_id for phone_id in err_keys_as_numbers if phone_id not in [ph,before_ph,next_ph]])
                                    #print(f'mat warning : change_phone_id == before_ph  or change_phone_id == next_ph change_id:{change_phone_id} ,before_ph:{before_ph},next_ph:{next_ph}')
                                    #sys.exit()
                                before_ph  = change_phone_id                                
                                #print(sentence_id + " " + str(pos_none_count) + " "+ str(phone_dict[ph]) + "->" + str(phone_dict[change_phone_id])) 
                                if change_phone_id:
                                    all_zero_count += 1
                                    pos_scores.append((pos_none_count, ph,change_phone_id))  
                                    pos_data['ph'] = change_phone_id                               
                            #random err
                            elif change_flag == 0:
                                if random_lim < random_err_up:
                                    #change_phone_id = random.choice([phone_id for phone_id in phone_dict.keys() if phone_id not in [ph,before_ph,next_ph]])
                                    change_phone_id = random.choice([phone_id for phone_id in err_keys_as_numbers if phone_id not in [ph,before_ph,next_ph]])
                                    if change_phone_id == before_ph  or change_phone_id == next_ph or change_phone_id == ph:
                                        #print(f'random warning : change_phone_id == before_ph  or change_phone_id == next_ph change_id:{change_phone_id} ,before_ph:{before_ph},next_ph:{next_ph}')
                                        sys.exit()
                                    before_ph  = change_phone_id                                   
                                    #print(sentence_id + " " + str(pos_none_count) + " "+ str(phone_dict[ph]) + "->" + str(phone_dict[change_phone_id])) 
                                    if change_phone_id:
                                        all_zero_count += 1
                                        pos_scores.append((pos_none_count, ph,change_phone_id))  
                                        pos_data['ph'] = str(change_phone_id)
                                else:    
                                    before_ph  = ph
                            else:
                                print("change id err")     
                            if change_phone_id in err_keys_as_numbers:
                                err_dict[phone_dict[change_phone_id][0]] -= 1               
                            # if lim < 0.1:
                            #     pos_none_count += 1
                            #     random_phone_id = random.choice([phone_id for phone_id in phone_dict.keys() if phone_id not in [ph,before_ph,next_ph]])
                            #     if random_phone_id == ph or random_phone_id == before_ph:
                            #         print("random ph err")
                            #         sys.exit()
                            #     pos_scores.append((pos_none_count, ph, random_phone_id))  # 记录pos_cur和音素替换信息
                            #     print(sentence_id + " " + str(pos_none_count) + " "+ str(phone_dict[ph]) + "->" + str(phone_dict[random_phone_id]))
                            #     pos_data['ph'] = random_phone_id
                            #     before_ph  = random_phone_id
                            # elif lim >=0.1:
                            #     pos_none_count += 1      
                            #     before_ph  = ph                   
                            # else:
                            #     print("ph = 1 lim err")                           
                        elif ph == '1':
                            before_ph  = '1' 
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
                all_ph_count += (pos_none_count + 1)
 # 关闭pos_scores文件
pos_scores_file.close()
print("phone no err list:")
print(err_dict)
#print(zh_count)
# for err_ph,change_value in err_dict.items():
#     if int(change_value) > -100:
#         print(err_ph)

#print(f'all_ph_count: {all_ph_count} , all_zero_count: {all_zero_count}')





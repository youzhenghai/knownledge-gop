import os
import json

import argparse

parser = argparse.ArgumentParser(description='data_folder')
parser.add_argument('input_path', help='Input path')
parser.add_argument('output_path', help='output path')
args = parser.parse_args()


# 指定 解压后ali-phone文件所在目录
data_directory = args.input_path

# 创建保存处理 的 对齐ph和帧数 json数据的目录
output_directory = args.output_path
os.makedirs(output_directory, exist_ok=True)

# 遍历目录下的文件
for filename in os.listdir(data_directory):
    if filename.startswith('ali-phone.'):
        # 构造文件路径
        file_path = os.path.join(data_directory, filename)

        # 处理文件数据
        with open(file_path, 'r') as file:
            # 读取文件内容
            lines = file.readlines()

            # 进行数据处理操作
            data = {}

            for line in lines:
                line_data = line.split()
                sentence_id = (line_data[0])
                numbers = line_data[1:]
                #print(sentence_id)

                if sentence_id not in data:
                    data[sentence_id] = {}
                else:
                    print("sentence data repeat")

                current_number = None
                pos_cur = 0
                for next_number in numbers:
                    #if next_number == '1':
                    #    pass
                    if next_number == current_number:
                        #print("here")
                        data[sentence_id][pos_cur]['count'] += 1
                    elif next_number != current_number:
                        pos_cur += 1
                        data[sentence_id][pos_cur] = {}
                        data[sentence_id][pos_cur]['ph'] = next_number
                        data[sentence_id][pos_cur]['count'] = 1
                    else:
                        print("ali err")
                    current_number = next_number

        # 保存处理后的数据到同名文件
        output_filename = filename.replace('ali-phone.', 'ali-phone-json.')
        output_file_path = os.path.join(output_directory, output_filename )

        with open(output_file_path, 'w') as output_file:
            # 将数据保存为JSON文件
            json.dump(data, output_file)

import os
import json

import argparse

parser = argparse.ArgumentParser(description='data_folder')
parser.add_argument('input_path', help='Input path')
parser.add_argument('output_path', help='output path')
args = parser.parse_args()



data_directory = args.input_path

# ali-phone  to json
output_directory = args.output_path
os.makedirs(output_directory, exist_ok=True)


for filename in os.listdir(data_directory):
    if filename.startswith('ali-phone.'):
        
        file_path = os.path.join(data_directory, filename)      
        with open(file_path, 'r') as file:         
            lines = file.readlines()
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

        output_filename = filename.replace('ali-phone.', 'ali-phone-json.')
        output_file_path = os.path.join(output_directory, output_filename )

        with open(output_file_path, 'w') as output_file:
            json.dump(data, output_file)

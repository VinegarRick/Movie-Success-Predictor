import sys
import csv
import ast

if len(sys.argv) < 2:
	print("Usage: python metadata_and_credits_combiner.py {0-2}")
	exit()

USER_ID = sys.argv[1]

if USER_ID.isdigit():
	USER_ID = int(USER_ID)
else:
	print("Input a number please")
	exit()

if USER_ID < 0 or USER_ID > 2:
	print("Invalid input")
	exit()

FILE_NAME = 'movies_metadata.csv'

# count number of lines
num_lines = 0
with open(FILE_NAME, 'r', encoding='utf-8') as csvfile:
	reader = csv.reader(csvfile)
	for r in reader:
		num_lines += 1

# calculate offsets
OFFSET_BEGIN = int(num_lines * 1.0 / 3 * USER_ID)
OFFSET_END = 0
if USER_ID != 2:
	OFFSET_END = int(num_lines * 1.0 / 3 * (USER_ID + 1))
else:
	OFFSET_END = num_lines


credits_dict = {}
n = 0
with open("assignment2_cast.json") as cast_file:
	for line in cast_file:
		d = ast.literal_eval(line)
		credits_dict[d['id']] = d


out_file = open("assignment2_dataset_with_cast_" + str(OFFSET_BEGIN) + "to" + str(OFFSET_END) + ".json", 'w')
with open("assignment2_dataset_" + str(OFFSET_BEGIN) + "to" + str(OFFSET_END) + ".json") as metadata_file:
	for line in metadata_file:
		d = ast.literal_eval(line)
		if d['id'] in credits_dict:
			d['cast'] = credits_dict[d['id']]['cast']
			d['director'] = credits_dict[d['id']]['director']
			out_file.write(str(d) + '\n')
		else:
			print("ERROR: could not find id!")
			exit()

out_file.close()

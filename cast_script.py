import ast
import csv

def modifyDataVal(dataDict):
	dataDict['id'] = int(dataDict['id'])

	raw_cast_list = ast.literal_eval(dataDict['cast'])
	cast_list = []
	for c in raw_cast_list:
		cast_list.append(c['name'])
	dataDict['cast'] = cast_list

	raw_crew_list = ast.literal_eval(dataDict['crew'])
	director_name = ''
	candidates = [c for c in raw_crew_list if c['job'].lower() == 'director']
	if len(candidates) > 0:
		director_name = candidates[0]['name']
	else:
		print("Error: could not find director!")
		director_name = "UNKNOWN"

	dataDict['director'] = director_name
	del dataDict['crew']


headersArry = []
header = True
out_file = open('assignment2_cast.json', 'w')
with open('credits.csv') as csvfile:
	reader = csv.reader(csvfile)
	n = 0
	for row in reader:
		print(n)
		if header:
			for i in range(len(row)):
				headersArry.append(row[i])
			header = False
			continue
		else:
			dataDict = {}
			for i in range(len(headersArry)):
				dataDict[headersArry[i]] = row[i]
			modifyDataVal(dataDict)
			out_file.write(str(dataDict) + '\n')
		n += 1

out_file.close()

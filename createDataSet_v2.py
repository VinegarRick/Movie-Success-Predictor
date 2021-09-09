import sys
import csv
from imdb import IMDb
import json
import ast
import re
#from itertools import izip

ia = IMDb()

# cutoff offsets
# 8967
# 10916

# TODO
# check if gross (worldwide) is roughly equal to revenue - budget
# if no worldwide, check if US gross is roughly equal
# merge director and cast data
# keywords (maybe)


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
	print("Number out of range")
	exit()

FILE_NAME = 'movies_metadata.csv'

# count number of lines
num_lines = 0
with open(FILE_NAME, 'r', encoding='utf-8') as csvfile:
	reader = csv.reader(csvfile)
	for r in reader:
		num_lines += 1

print("Num lines: " + str(num_lines))

# calculate offsets
OFFSET_BEGIN = int(num_lines * 1.0 / 3 * USER_ID)
OFFSET_END = 0
if USER_ID != 2:
	OFFSET_END = int(num_lines * 1.0 / 3 * (USER_ID + 1))
else:
	OFFSET_END = num_lines

intHeaders = ['budget','id','revenue','vote_count']
floatHeaders = ['popularity','runtime','vote_average']
#boolHeaders = ['adult','video']  # LOLLL, this was a coincidence

def testfloat(val):
	try:
		float(val)
	except ValueError:
		return False
	return True

def convertToProperType(val,header):
	#print(header + ": " + str(val))
	if header in intHeaders and val.isdigit():
		return int(val)
	elif header in floatHeaders and testfloat(val):  # check if float before converting
		return float(val)
	else:
		return val


def findGreatest(candidates, replaceStr):
	greatest = 0
	for i in range(len(candidates)):
		revenueStr = candidates[i].lower().replace(',','').replace(replaceStr,'')
		revenueStr = revenueStr[1:]
		if revenueStr.isdigit():
			revenueVal = int(revenueStr)
			if revenueVal > greatest:
				greatest = revenueVal
	return greatest


keys_to_delete = ['adult','homepage','poster_path','video']

# applies necessary conversions/simplifications to data value
def modifyDataVal(dataDict):
	# delete unneeded keys
	for k in keys_to_delete:
		del dataDict[k]

	if dataDict['belongs_to_collection'] != '':
		dataDict['belongs_to_collection'] = ast.literal_eval(dataDict['belongs_to_collection'])['name']

	keys = ['genres','production_companies','production_countries','spoken_languages']
	for k in keys:
		if dataDict[k] != '':
			raw_genre_list = ast.literal_eval(dataDict[k])
			genre_list = []
			for g in raw_genre_list:
				genre_list.append(g['name'])
			dataDict[k] = genre_list

	if dataDict['imdb_id'] == '':
		return

	dataDict['imdb_id'] = dataDict['imdb_id'][2:]  # get rid of 'tt' at the beginning

	# fill in missing revenue and budget info
	#if dataDict['revenue'] == 0 or dataDict['budget'] == 0:
	if True:
		movie = ia.get_movie(dataDict['imdb_id'])
		ia.update(movie, 'business')
		keys = movie.infoset2keys['business']

		if True:
			if 'gross' in keys:
				print("revenue info available")
				print(movie.get('gross'))
				candidates = [g for g in movie.get('gross') if g.lower().endswith(' (worldwide)')]
				if len(candidates) > 0:  # take worldwide gross as revenue
					print("Taking worldwide")
					greatest = findGreatest(candidates, ' (worldwide)')
					dataDict['revenue'] = greatest
					print(greatest)
				else:  # attempt to take worldwide most recent
					candidates = [g for g in movie.get('gross') if '(worldwide)' in g.lower()]
					if len(candidates) > 0:
						print("Taking worldwide most recent")
						for g in candidates:
							revenueStr = g.split()[0].replace(',','')
							revenueStr = revenueStr[1:]
							if revenueStr.isdigit():
								revenueVal = int(revenueStr)
								dataDict['revenue'] = revenueVal
								print(revenueVal)
								break
					else:  # attempt to takes total USA revenue
						candidates = [g for g in movie.get('gross') if g.endswith(' (USA)') or g.lower().endswith(' (non-usa)')]
						if len(candidates) > 0:  # take USA gross as revenue
							print("Taking USA total + (non-USA if there is any)")

							usa_cands = [c for c in candidates if c.endswith(' (USA)')]
							total = findGreatest(usa_cands, ' (usa)')

							non_usa_cands = [c for c in candidates if c.lower().endswith(' (non-usa)')]
							total += findGreatest(non_usa_cands, ' (non-usa)')

							dataDict['revenue'] = total
							print(total)
						else:  # neither USA or worldwide total gross found, use most recent entry (i.e. the first entry in the list)
							print("Taking USA most recent")
							for g in movie.get('gross'):
								if '(USA)' in g:
									revenueStr = g.split()[0].replace(',','')
									revenueStr = revenueStr[1:]
									if revenueStr.isdigit():
										revenueVal = int(revenueStr)
										dataDict['revenue'] = revenueVal
										print(revenueVal)
										break

		if True:
			if 'budget' in keys:
				print("budget info available")
				budgetStr = ''.join(movie.get('budget'))
				print(movie.get('budget'))
				#budget = budget.split()[0]
				budgetStr = budgetStr.split()[0].replace(',', '')
				#if budget[0] == '$':
				currency = budgetStr[0]
				budgetStr = budgetStr[1:]
				if budgetStr.isdigit():
					budgetVal = int(budgetStr)
					if currency == '£':  # convert pound to dollars
						budgetVal = int(1.35 * budgetVal)
						print("pound converted")
					if currency == '$' or currency == '£':  # only use dollar or pound values
						print(budgetVal)
						dataDict['budget'] = budgetVal
						print("budget replaced!")


def parseData(fname):
	headersArry = []
	header = True
	out_file = open("assignment2_dataset_" + str(OFFSET_BEGIN) + "to" + str(OFFSET_END) + ".json", "w")
	with open(fname, 'r') as csvfile:
		#reader = csv.reader(csvfile, delimiter=',')
		reader = csv.reader(csvfile)
		n = 0
		for row in reader:
			print(n)
			if header:
				for i in range(len(row)):
					headersArry.append(row[i])
				header = False
				continue
			elif n >= OFFSET_BEGIN and n < OFFSET_END:
				if len(row) == len(headersArry):
					dataDict = {}
					for i in range(len(row)):
						dataDict[headersArry[i]] = convertToProperType(row[i],headersArry[i])
					if 'production_countries' in dataDict and 'United States of America' in dataDict['production_countries']:
						modifyDataVal(dataDict)
						out_file.write(str(dataDict) + '\n')
					#exit()
			n += 1

	out_file.close()


print("Reading data...")
parseData(FILE_NAME)
print("done")

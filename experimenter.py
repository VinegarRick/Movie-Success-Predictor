import ast
import csv
from imdb import IMDb

# ['airing', 'akas', 'alternate versions', 'awards', 'business', 'connections', 'crazy credits', 'critic reviews', 'episodes', 'episodes cast', 'episodes rating', 'external reviews', 'faqs', 'full credits', 'goofs', 'guests', 'keywords', 'literature', 'locations', 'main', 'misc sites', 'news', 'official sites', 'parents guide', 'photo sites', 'plot', 'quotes', 'recommendations', 'release dates', 'release info', 'sound clips', 'soundtrack', 'synopsis', 'taglines', 'technical', 'trivia', 'tv schedule', 'video clips', 'vote details']

ia = IMDb()

CATEGORY = 'business'
n = 0

for l in open('datasets_dir/assignment2_dataset.json'):
	d = ast.literal_eval(l)

	movie = ia.get_movie(d['imdb_id'])
	ia.update(movie, CATEGORY)

	keys = movie.infoset2keys[CATEGORY]

	print(n)
	print(d['production_countries'])
	print("Revenue: " + str(d['revenue']))
	print("Budget: " + str(d['budget']))
	print("Expected: " + str(d['revenue'] - d['budget']))
	print("Actual: " + str(movie.get('gross')))

	if n > 40:
		exit()

	n += 1

	#ia.update(movie, 'main')

exit()

count = 0
header = True
with open('movies_metadata.csv') as csvfile:
	reader = csv.reader(csvfile)
	for row in reader:
		if header:
			header = False
		elif len(row) > 13:
			country_list = ast.literal_eval(row[13])
			if type(country_list) is list:
				country_list = [c['name'] for c in country_list]
				print(country_list)
				if 'United States of America' in country_list:
					count += 1

print("count = " + str(count))

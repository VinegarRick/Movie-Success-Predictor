import ast
import itertools
import numpy
import random
import re
import nltk
from collections import defaultdict
from collections import Counter
from sklearn.metrics import mean_squared_error
from sklearn import linear_model
from sklearn import svm
from datetime import date
from nltk.corpus import stopwords
from itertools import combinations
from random import shuffle

def readFile(f):
    for l in open(f):
        yield ast.literal_eval(l)

def feature(datum):
    feature = [1]
    #feature = []
    appendFeatureGenre(feature, datum['genres'])
    #appendReleaseDate(feature, datum['release_date'])
    #feature.append(datum['budget'])
    #feature.append(datum['runtime'] > 90)
    feature.append(int(datum['belongs_to_collection'] != ''))
    #appendForeignLanguage(feature, datum['spoken_languages']) #can't use with normalized weight with current implementation of similarity
    #appendDirector(feature, datum['director'])
    appendFeatureCompany(feature, datum['production_companies'])
    appendCommonWords(feature, datum['overview'].lower())
    #appendPopularDirector(feature, datum['director'])
    #appendPopularCompany(feature, datum['production_companies'])
    #appendDirectorScore(feature, datum['director'])
    #appendCompanyScore(feature, datum['production_companies'])
    appendPopularCast(feature, datum['cast'])

    #appendSimilarity(feature)
    #appendSimilarityScore(feature)

    return feature

def featureForSimilarity(datum):
    feature = [1]
    appendFeatureGenre(feature, datum['genres'])
    #appendReleaseDate(feature, datum['release_date'])
    #feature.append(datum['budget'])
    #feature.append(datum['runtime'] > 90)
    feature.append(int(datum['belongs_to_collection'] != ''))
    #appendForeignLanguage(feature, datum['spoken_languages'])
    #appendDirector(feature, datum['director'])
    appendFeatureCompany(feature, datum['production_companies'])
    appendCommonWords(feature, datum['overview'].lower())
    #appendPopularDirector(feature, datum['director'])
    #appendPopularCompany(feature, datum['production_companies'])
    #appendDirectorScore(feature, datum['director'])
    #appendCompanyScore(feature, datum['production_companies'])
    appendPopularCast(feature, datum['cast'])

def appendPopularCast(feature, data_cast):
    for count,actor in bestCast:
        if actor in data_cast:
            feature.append(1)
        else:
            feature.append(0)

def appendCompanyScore(feature, data_companies):
    highestScore = 0.0
    notSeen = True
    for company in data_companies:
        if company in companyScores:
            notSeen = False

    if notSeen:
        feature.append(0)
        return

    for company in data_companies:
        if company not in companyScores:
            continue
        companyScore = companyScores[company]
        if companyScore > highestScore:
            highestScore = companyScore

    feature.append(highestScore)

def appendDirectorScore(feature, data_director):
    if data_director in directorScores:
        feature.append(directorScores[data_director])
    else:
        feature.append(0)

def appendPopularCompany(feature, data_companies):
    for company in data_companies:
        if company in bestCompanies:
            feature.append(1)
            return

    feature.append(0)

def appendPopularDirector(feature, data_director):
    if data_director in bestDirectors:
        feature.append(1)
    else:
        feature.append(0)

def appendCommonWords(feature, data_overview):
    wordVector = [0] * 2000
    words = re.sub('[^a-z\ \']+', " ", data_overview)
    for w in list(words.split()):
        if w in commonWords:
            #wordVector[commonWords.index(w)] += 1
            wordVector[commonWords.index(w)] = 1

    feature += wordVector

"""def appendFeatureGenre(feature, data_genres):
    if not data_genres:
        feature.append(0)
        return

    data_genres.sort()
    genres = tuple(data_genres)
    feature.append(genreDict[genres])"""

def appendFeatureGenre(feature, data_genres):
    for genre, key in sorted(genreDict.items()):
        if genre in data_genres:
            feature.append(1)
        else:
            feature.append(0)

def appendReleaseDate(feature, data_release_date):
    begin_date = date(1970, 1, 1)
    date_split = data_release_date.split('-')
    end_date = date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
    delta = end_date - begin_date
    feature.append(delta.days)

def appendForeignLanguage(feature, data_spoken_languages):
    if len(data_spoken_languages) == 1 and data_spoken_languages[0] == 'English':
        feature.append(0)
    else:
        feature.append(1)

def appendDirector(feature, data_director):
    #feature.append(directorDict[director])
    #directors = data_director.split(',')
    #if len(directors) > 1:
        #print(len(directors))
    #    print(directors)

    #feature.append(directorDict[data_director])

    for director, key in sorted(directorDict.items()):
        if director in data_director:
            feature.append(1)
        else:
            feature.append(0)

def appendFeatureCompany(feature, companies):
    for company, key in sorted(companyDict.items()):
        if company in companies:
            feature.append(1)
        else:
            feature.append(0)

def appendSimilarityScore(feature):
    highestScore = 0
    for featureVector in mostProfitableMovies:
        score = 0
        numZeroes = 0
        for i in len(feature):
            if feature[i] == featureVector[i] and feature[i] != 0:
                score += 1
            elif feature[i] == featureVector[i] and feature[i] == 0:  
                numZeroes += 1
        score /= (len(feature) - numZeroes)
        if score > highestScore:
            highestScore = score

    feature.append(highestScore)

def appendSimilarity(feature):
    highestScore = 0
    for featureVector in mostProfitableMovies:
        score = 0
        numZeroes = 0
        for i in len(feature):
            if feature[i] == featureVector[i] and feature[i] != 0:
                score += 1
            elif feature[i] == featureVector[i] and feature[i] == 0:
                numZeroes += 1
        score /= (len(feature) - numZeroes)
        if score > highestScore:
            highestScore = score

    # need to play around with threshold
    if highestScore > 0.5:
        feature.append(1)
    else:
        feature.append(0)

def getMostProfitableMovies(data):
    profitRatio = defaultdict(float)
    mostProfitableMoviesFeatures = []
    for m in data:
        ratio = m['revenue'] * 1.0 / m['budget']
        profitRatio[m['title']] = ratio

    mostProfitableMovies = []
    profitRatio = Counter(profitRatio)
    # need to play around with threshold
    for k in profitRatio.most_common(100):
        mostProfitableMovies.append(k)

    for m in data:
        if m['title'] in mostProfitableMovies:
            mostProfitableMoviesFeatures.append(featureForSimilarity(m))

    return mostProfitableMoviesFeatures


def getBestCompanies(data):
    profitRatioByCompany = defaultdict(float)
    numMoviesByCompany = defaultdict(int)
    for m in data:
        companies = m['production_companies']
        for company in companies:
            profitRatioByCompany[company] += m['revenue'] / m['budget']
            numMoviesByCompany[company] += 1

    for company in profitRatioByCompany:
        profitRatioByCompany[company] /= numMoviesByCompany[company]

    bestCompanies = []
    profitRatioByCompany = Counter(profitRatioByCompany)
    # need to play around with threshold
    for k in profitRatioByCompany.most_common(750):
        bestCompanies.append(k)

    return bestCompanies

def getCompanyScores(data):
    companyScores = defaultdict(float)
    numMoviesByCompany = defaultdict(int)
    for m in data:
        companies = m['production_companies']
        for company in companies:
            numMoviesByCompany[company] += 1
            if m['revenue'] > (2.5 * m['budget']):
                companyScores[company] += 1

    for company in companyScores:
        companyScores[company] /= numMoviesByCompany[company]

    return companyScores

def getDirectorScores(data):
    directorScores = defaultdict(float)
    numMoviesByDirector = defaultdict(int)
    for m in data:
        numMoviesByDirector[m['director']] += 1
        if m['revenue'] > (2.5 * m['budget']):
            directorScores[m['director']] += 1

    for director in directorScores:
        directorScores[director] /= numMoviesByDirector[director]

    return directorScores

def getBestDirectors(data):
    numProfitableMoviesByDirector = defaultdict(int)
    for m in data:
        if m['revenue'] > (2.5 * m['budget']):
            numProfitableMoviesByDirector[m['director']] += 1

    bestDirectors = []
    numProfitableMoviesByDirector = Counter(numProfitableMoviesByDirector)
    # need to play around with threshold
    for k in numProfitableMoviesByDirector.most_common(500):
        bestDirectors.append(k)

    return bestDirectors

def getCommonWords(data):
    #nltk.download('stopwords')
    #stopwordsList = set(stopwords.words('english'))
    wordCount = defaultdict(int)
    profitableWordCount = defaultdict(int)
    for r in data:
        overview = r['overview'].lower()
        words = re.sub('[^a-z\ \']+', " ", overview)
        for w in list(words.split()):
            #if w not in stopwordsList:
            wordCount[w] += 1

    wordCount = Counter(wordCount)
    mostCommonWords = {}
    # need to play around with threshold
    for k, v in wordCount.most_common(20000):
        mostCommonWords[k] = v

    for r in data:
        overview = r['overview'].lower()
        words = re.sub('[^a-z\ \']+', " ", overview)
        for w in list(words.split()):
            if w in mostCommonWords:
                if r['revenue'] > (2.5 * r['budget']):
                    profitableWordCount[w] += 1

    wordFrequency = {}
    for w in mostCommonWords:
        wordFrequency[w] = mostCommonWords[w] / sum(mostCommonWords.values())

    profitableWordFrequency = defaultdict(float)

    for w in mostCommonWords:
        profitableWordFrequency[w] = profitableWordCount[w] / sum(profitableWordCount.values())

    relativeFrequency = defaultdict(float)

    for w in mostCommonWords:
        relativeFrequency[w] = profitableWordFrequency[w] - wordFrequency[w]

    profitableWords = []
    relativeFreqs = Counter(relativeFrequency)
    # need to play around with threshold
    for k, v in relativeFreqs.most_common(2000):
        profitableWords.append(k)

    #print(profitableWords)

    return profitableWords

def createDirectorSet(data):
    directorSet = set()
    for datum in data:
        directorSet |= set([datum['director']])

    return directorSet

def createDirectorDict(data):
    directorList = list(createDirectorSet(data))
    directorList.sort()
    directorDict = dict()
    index = 0

    for director in directorList:
        directorDict[director] = index
        index += 1

    return directorDict

def createCompanySet(data):
	companySet = set()
	for datum in data:
		companySet |= set(datum['production_companies'])
	return companySet

def createCompanyDict(data):
	companyList = list(createCompanySet(data))
	companyList.sort()
	companyDict = dict()
	index = 0
	for company in companyList:
		companyDict[company] = index
		index += 1

	return companyDict

def createGenreSet(data):
    genreSet = set()
    for datum in data:
        genreSet |= set(datum['genres'])

    return genreSet

"""def createGenreDict(genreSet):
    genreList = list(createGenreSet(data))
    genreList.sort()
    genreDict = dict()
    index = 1

    for n in range(len(genreList) + 1):
        for subset in combinations(genreList, n):
            genreDict[subset] = index
            index += 1

    return genreDict"""

def createGenreDict(data):
    genreList = list(createGenreSet(data))
    genreList.sort()
    genreDict = dict()
    index = 0
    for genre in genreList:
        genreDict[genre] = index
        index += 1

    return genreDict


def getBestCast(data):
    actorsDict = defaultdict(int)
    
    for datum in data:
        cast = datum['cast']
        for actor in cast:
            actorsDict[actor] += 1
    
    actorsList = []
    for actor,count in actorsDict.iteritems():
        actorsList.append((count,actor))
    
    actorsList.sort()
    actorsList.reverse()
    
    sumOfAllActors = sum([count for count,actor in actorsList])
    
    popularActorsList = []
    sumSoFar = 0
    threshold = sumOfAllActors*1.0/20
    
    for count,actor in actorsList:
        if sumSoFar > threshold:
            return popularActorsList
        sumSoFar += count
        popularActorsList.append((count,actor))
    
    return actorsList


print("Reading data...")
data = list(readFile("assignment2_dataset_final.json"))
#data = [x for x in data if x['budget'] != 0 and x['revenue'] != 0]
data = [x for x in data if x['budget'] != 0 and x['revenue'] != 0 and x['genres'] != [] and x['production_companies'] != []]
print("Done.")

shuffle(data)

#trainingSet = data
#trainingSet = data[:len(data) // 2]
#validationSet = data[len(data) // 2:]
trainingSet = data[:3056]
validationSet = data[3056:]

genreDict = createGenreDict(data)
directorDict = createDirectorDict(trainingSet)
companyDict = createCompanyDict(trainingSet)
commonWords = getCommonWords(trainingSet)

bestDirectors = getBestDirectors(trainingSet)
bestCompanies = getBestCompanies(trainingSet)
directorScores = getDirectorScores(trainingSet)
companyScores = getCompanyScores(trainingSet)
bestCast = getBestCast(trainingSet)
mostProfitableMovies = getMostProfitableMovies(trainingSet)

print("Creating sets...")
X_train = [feature(d) for d in trainingSet]
y_train = [d['revenue'] > (2.5 * d['budget']) for d in trainingSet]

X_valid = [feature(d) for d in validationSet]
y_valid = [d['revenue'] > (2.5 * d['budget']) for d in validationSet]
print("Done.")

print("Training...")
#clf = linear_model.Ridge(1.0, fit_intercept=False)
clf = svm.LinearSVC(C=0.1)
clf.fit(X_train, y_train)
theta = clf.coef_
print("Done training.")

#print(theta[0])

print("Performing predictions on validation set...")
predictions = clf.predict(X_valid)
print("Done predicting.")

#for prediction in predictions:
#    print(prediction)

accuracy = [x == y for x,y in zip(predictions, y_valid)]
print('Accuracy: ' + str(sum(accuracy)*1.0 / len(accuracy)))

#validationAccuracy = mean_squared_error(y_valid, predictions)
#print("MSE: %f" % validationAccuracy)

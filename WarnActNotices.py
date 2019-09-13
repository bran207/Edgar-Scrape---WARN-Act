import EdgarAPI
import numpy as np
import re
import xlwings
import csv

api = EdgarAPI.EdgarAPI()

cikDatabaseFilePath = 'CIK_Databasev2.csv'
postiveMatchesFilePath = 'PositiveMatches.csv'


exactMatches = ["jobs will be eliminated",
                "downsize",
                "downsizing",
                "employee headcount reductions",
                "employee related costs",
                "employee-related costs",
                "headcount reductions",
                "separation-related expenses",
                "separation related expenses",
                "severance",
                "staff reduction",
                "layoff",
                "termination benefits",
                "termination-related benefits",
                "termination related benefits"
                ]

CollactedMatches = {
                    "rationaliz": ['workforce','employ','headcount'],
                    "reduc": ['employ','headcount','workforce','force','labor','headcount','staff','levels','global workforce'],
                    "terminat": ['employ','workforce'],
                    "workforce": ['resturctur','reduc'],
                    "restructur": ['workforce','employ','labor']
                    }


def mainProgram():
    CIKDatabase = loadCIKDatabase()
    for CIK in CIKDatabase:
        allEightKs = api.returnCompanies8ks(CIK)
        for eightK in allEightKs:
            eightKData = api.getIndivdual8KData(eightK['Document Link'])
            if eightKData:
                textFileContents = eightKData['Text File Contents']
                if isATextMatch(textFileContents):
                    containsServerance = bool('severance' in textFileContents)
                    occurancesOfChangeInControl = textFileContents.count("change in control") + textFileContents.count("change of control")
                    logEntry(CIK,eightK['Date'],eightKData['periodOfReport'],"https://www.sec.gov" + eightK['Document Link'],eightKData['EXNineNineOneExists'],eightKData['9.01 Exists'],eightKData['2.05 Exists'],eightKData['NumberOfItems'],eightKData['numberOfDocuments'],eightKData['Document Size'],eightKData['5.02 Exists'],containsServerance,occurancesOfChangeInControl,eightKData['7.01 Exists'])
        markAsCompleted(CIK)

def isATextMatch(textFileContents):
    for term in exactMatches:
        if term in textFileContents:
            print(term)
            return True

    for term in CollactedMatches.keys():
        if term in textFileContents:
            potentialSentences = withinThreeWordsResults(term,textFileContents)
            for sentence in potentialSentences:
                for secondTerm in CollactedMatches[term]:
                    if secondTerm in sentence:
                        return True
    return False



def logEntry(cik,filingDate,periodDate,eightKLink,nineNineOne,nineZeroOne,twoZeroFive,numberItems,maxDocuments,fileSize,fiveZeroTwo,containsServerance,occurancesOfChangeInControl,sevenZeroOne):
    with open(postiveMatchesFilePath, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([cik,filingDate,periodDate,eightKLink,nineNineOne,nineZeroOne,twoZeroFive,numberItems,maxDocuments,fileSize,fiveZeroTwo,containsServerance,occurancesOfChangeInControl,sevenZeroOne])




def loadCIKDatabase():
    with open(cikDatabaseFilePath, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        your_list = list(reader)
        results = []
        for line in your_list:
#            print(line)
            if line[8] == 'FALSE':
                results.append(line[0])
    return results

def loadRawDatabase():
    with open(cikDatabaseFilePath, 'r') as f:
        reader = csv.reader(f)
        your_list = list(reader)
    return your_list

def sentencesWithTerm(word,text):
    result = [sentence + '.' for sentence in text.split('.') if word in sentence]
    return result

def withinThreeWordsResults(word,text):
    results = []
    startNumber = [0]
    for sentence in text.split(word):
        occurance = text.find(word,startNumber[len(startNumber)-1]+1)
        if occurance not in startNumber and occurance != -1:
            if startNumber == [0]:
                startNumber = [occurance]
            else:
                startNumber.append(occurance)
    for occurance in startNumber:
        closeWords = getThreeWordsBefore(text,occurance) + getThreeWordsAfter(text,occurance)
        results.append(closeWords)
    return results


def getThreeWordsBefore(text,occurance):
    counter = 0
    num = 0
    startNumber = 0
    endNumber = 0
    try:
        while True:
            if text[occurance-num] == " ":
                counter += 1
            num += 1
            if counter == 4:
                return text[occurance-num+2:occurance]
    except:
        return "N/A"

def getThreeWordsAfter(text,occurance):
    counter = 0
    num = 0
    startNumber = 0
    endNumber = 0
    try:
        while True:
            if text[occurance+num] == " ":
                counter += 1
            num += 1
            if counter == 4:
                return text[occurance:occurance+num]
    except:
        return "N/A"




def markAsCompleted(cik):
    originalDatabase = loadRawDatabase()
    newDatabase = []
    for row in originalDatabase:
        if row[0] == cik:
            row[8] = True
        newDatabase.append(row)

    with open(cikDatabaseFilePath, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(newDatabase)


def testFunc():
    CIKDatabase = loadCIKDatabase()
    for CIK in CIKDatabase:
        print(CIK)
        allEightKs = api.returnCompanies8ks(CIK)
        for eightK in allEightKs:
            if CIK not in eightK['Document Link']:
                print(CIK)
                for item in allEightKs:
                    print(item)
                return CIK


if __name__ == "__main__":
    mainProgram()


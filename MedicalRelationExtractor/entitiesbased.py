#AUTHOR: RAHUL VERMA and SPIRO RAZIS
import sys
import pprint
import numpy
from sklearn import svm
from sklearn import linear_model
import time

start_time = time.time()

numpy.set_printoptions(threshold=numpy.nan)

def parseTextViaPMCID(textFile, pmcidFeatureList, uniqueWordsDictionary,lim):
    
    if textFile.startswith("randomBeni"):
        print("beneficial")
        fileType = "beneficial".encode('utf-8')
    elif textFile.startswith("randomHarm"):
        print("harmful")
        fileType = "harmful".encode('utf-8')
    else:
        if textFile.startswith("b"):
            fileType = "beneficial".encode('utf-8')
        else:
            fileType = "harmful".encode('utf-8')

    limit = 0 
    entryCount       = 0
    disease          = ""
    causeOrTreatment = ""
    relation         = ""
    newEntry = False    
    lindex = 0
    
    with open(textFile, "r") as openedTextFile:
        for line in openedTextFile:
            lindex+=1
            if line.startswith("pmcid   : "): #it's the idNumber
                entryCount += 1
                newEntry = True
            elif line.startswith("sentence: "): #it's a sentence
                pass
                  
            elif line.startswith("entities: "): #it's the two in a relationship
                disease = line[11:line.index(",")].lower().encode('utf-8')
                causeOrTreatment = line[(line.index(",")+2):-2].lower().encode('utf-8')
                if disease not in uniqueWordsDictionary:
                    if limit < lim:
                        uniqueWordsDictionary[disease] = {}
                if causeOrTreatment not in uniqueWordsDictionary:
                    if limit < lim:
                        uniqueWordsDictionary[causeOrTreatment] = {}
            elif line.startswith("offsets : "): #the position of the entities
                pass
            elif line.startswith("relation: "): #the actual relationship
                relation = line[10:-1].lower().encode('utf-8')                   
            else:             
                if line.startswith("\n") and (newEntry == True):
                    pmcidFeatureList.append([disease, causeOrTreatment, relation, fileType])
                    disease          = ""
                    causeOrTreatment = ""
                    relation         = ""
                    newEntry = False
                    limit += 1
                else:
                    print("invalid line: %s" %(line))
                    print(textFile,lindex)
                    sys.exit(2)

    return (pmcidFeatureList, entryCount, uniqueWordsDictionary)


def printFeatureWithCellValue(numpyRow, featureRow):
    for index, feature in enumerate(featureRow):
        print("%s: %d" %(feature, numpyRow[index]))
    print("harmfulOrBeneficial: %d" %(numpyRow[-1]))
    return

def printFeaturesWithValuesEqualOne(numpyRow, featureRow):
    for index, feature in enumerate(featureRow):
        if numpyRow[index] == 1:
            print("%s: %d" %(feature, numpyRow[index]))
    print("harmfulOrBeneficial: %d" %(numpyRow[-1]))
    return

def main(argv):
    #Python3 training.py beneficial.txt harmful.txt
    if len(argv) != 3:
        print("invalid number of arguments")
        sys.exit(2)
    
    #two separate lists because don't know how many entries in each, so dividing one list will be difficult
    pmcidBeneficialData = []
    pmcidHarmfulData = []
    uniqueWordsDictionary = {}
    
    (pmcidBeneficialData, beneficialCount, uniqueWordsDictionary)    = parseTextViaPMCID(argv[1], pmcidBeneficialData, uniqueWordsDictionary,10356)
    (pmcidHarmfulData, harmfulCount, uniqueWordsDictionary)       = parseTextViaPMCID(argv[2], pmcidHarmfulData, uniqueWordsDictionary,9797)
    benprec = 10356/beneficialCount
    harmprec = 9797/harmfulCount

    uniqueFeaturesArray = numpy.empty(shape = (1, len(uniqueWordsDictionary)), dtype="S128")
    #place the dictionary words into the array
    for index, feature in enumerate(uniqueWordsDictionary):
        uniqueFeaturesArray[0, index] = feature
        
    uniqueFeaturesArray.sort()

    
    
    #now to create the three individual arrays    
    numFeatures = len(uniqueWordsDictionary) + 1  #plus 1 for harmful or beneficial
    
    #from 20 to 80%:
    #beneficial60Percent = int(beneficialCount * 0.6)
    beneficial80Percent = int(beneficialCount * benprec)-1
    beneficial20Percent = int(beneficialCount - beneficial80Percent)
    
    #harmful60Percent    = int(harmfulCount * 0.6)
    harmful80Percent    = int(harmfulCount * harmprec)-1
    harmful20Percent    = int(harmfulCount - harmful80Percent)

    #shape = (rows, columns)    
    trainArray = numpy.empty(shape=((beneficial80Percent + harmful80Percent), numFeatures), dtype=numpy.int8) #Default is numpy.float64
    testArray   = numpy.empty(shape=((beneficial20Percent + harmful20Percent), numFeatures), dtype=numpy.int8)
    #
    
    #training data
    for entry in range(0, beneficial80Percent):
        #for each entry, find the index of the given feature
        for index, feature in enumerate(pmcidBeneficialData[entry]):
            if index < 2:
                #get the index of the given feature
                featureColumn = numpy.searchsorted(uniqueFeaturesArray[0], feature)
                if uniqueFeaturesArray[0][featureColumn] == feature:
                    trainArray[entry, featureColumn] = 1
                else: print("trainArray: incorrect beneficial feature match"); sys.exit(0)
            else: break 
        trainArray[entry, -1] = 1
        
    for entry in range(0, harmful80Percent):
        for index, feature in enumerate(pmcidHarmfulData[entry]):
            if index < 2:
                trainingEntry = entry + beneficial80Percent
                #get the index of the given feature
                featureColumn = numpy.searchsorted(uniqueFeaturesArray[0], feature)
                #set it to 1
                if uniqueFeaturesArray[0][featureColumn] == feature:
                    trainArray[trainingEntry, featureColumn] = 1
                else: print("trainArray: incorrect harmful feature match"); sys.exit(0)
            else: break #beneficialOrHarmful column remains 0

    
    #test data
    for entry in range(0, beneficial20Percent):
        dataEntry = entry + beneficial80Percent #finding next beneficial entry, starting from 60% until 80%        
        for index, feature in enumerate(pmcidBeneficialData[dataEntry]):
            if index < 2:
                for featureColumn in range(0,len(uniqueFeaturesArray[0])):
                    if uniqueFeaturesArray[0][featureColumn] == feature:
                        testArray[entry, featureColumn] = 1
            else: break #index == 3 and the column should remain 0
        testArray[entry, -1] = 1 
    for entry in range(0, harmful20Percent):
        dataEntry = entry + harmful80Percent # finding the next harmful entry starting from 60% until 80%
        for index, feature in enumerate(pmcidHarmfulData[dataEntry]):
            if index < 2:
                devEntry  = entry + beneficial20Percent #because the prior data entered ended with beneficial20Percent
                for featureColumn in range(0,len(uniqueFeaturesArray[0])):
                    if uniqueFeaturesArray[0][featureColumn] == feature:
                        testArray[devEntry, featureColumn] = 1
            else: break #index == 3 and column should remain 0
              
    
    
    ###########################################CLASSIFICATION SECTION#############################################################
    
    #Here we set up our list for support vectors and our  list for classes.
    #We will setup lists to hold our support vectors our classes.
    supportVectorsL = []
    classesListL = []

    for row in trainArray:
        y1 = row[len(row)-1]
        supportVectorsL.append(row[:-1])
        classesListL.append(y1)
    #Here we initialize our Linear classifier
    supportVectors = numpy.asarray(supportVectorsL)
    classesList = numpy.asarray(classesListL)
    #Here we try out the linear regresion stuff
    classifier = linear_model.LogisticRegression()
    classifier.fit(supportVectors,classesList)
    ############Test our sets through our logisitc model##################
    print("--------------------LOGISTIC------------------------")
    logistic(classifier,testArray,"TEST")

    print("--------------------SVM------------------------")
    #Here we set up the svm
    classifier = svm.SVC()
    classifier.fit(supportVectors,classesList)
    classifier.kernel="linear"
    ############Test our sets through our SVM model##################
    SVC(classifier,testArray,"TEST")

    
    
    
    sys.exit(0)

def SVC(classifier, testArray,t):
    testpredictionarray = []
    for row in testArray:
        predictionvector = row[:-1]
        if 1 in predictionvector:
            predictionvector = [predictionvector]
            prediction = classifier.predict(predictionvector)
            pre = int(prediction[0])
        else:
            pre = -1
        testpredictionarray.append(pre)
    totalAccuray(testArray,testpredictionarray,t)
    featAccuracy(testArray,testpredictionarray,t,1)
    featAccuracy(testArray,testpredictionarray,t,2)

def logistic(classifier, testArray,t):
    testpredictionarray = []
    for row in testArray:
        predictionvector = row[:-1]
        if 1 in predictionvector:
            predictionvector = [predictionvector]
            prediction = classifier.predict(predictionvector)
            pre = int(prediction[0])
        else:
            pre = -1
        testpredictionarray.append(pre)
    totalAccuray(testArray,testpredictionarray,t)
    featAccuracy(testArray,testpredictionarray,t,1)
    featAccuracy(testArray,testpredictionarray,t,2)


def totalAccuray(testArray,testpredictionarray,t):
    testcounter = 0
    #here we test for accuracy in the test set results.
    for x in range(0,len(testArray)):
        t1= testArray[x][len(testArray[x])-1]
        t1 = int(t1)
        if t1 == testpredictionarray[x]:
            testcounter = testcounter + 1
    accuracy= testcounter/len(testArray)   
    print(t+" set accuracy = " + str(accuracy))        

def featAccuracy(testArray,testpredictionarray,t,y):
    actual = 0
    testcounter = 0
    for x in range(0,len(testArray)):
        l = list(testArray[x])
        c = l.count(1)
        if c == y:
            actual+=1
            t1= testArray[x][len(testArray[x])-1]
            t1 = int(t1)
            if t1 == testpredictionarray[x]:
                testcounter = testcounter + 1
    try:
        accuracy= testcounter/actual
    except ZeroDivisionError:
        print(t+" set accuracy for only "+str(y)+" feature vectors = UNDEFINED")
        return
    
    print(t+" set accuracy for only "+str(y)+" feature vectors = " + str(accuracy))        



main(sys.argv)

#
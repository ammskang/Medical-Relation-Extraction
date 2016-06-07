#AUTHOR: RAHUL VERMA and SPIRO RAZIS
import sys
import re
import pprint
import numpy
from sklearn import svm
from sklearn import linear_model
import time
from random import shuffle

start_time = time.time()

numpy.set_printoptions(threshold=numpy.nan)

def parseTextViaPMCID(textFile, pmcidFeatureList, uniqueWordsDictionary,lim):
    
    if textFile.startswith("beneficial"):
        #print("beneficial")
        fileType = "beneficial".encode('utf-8')
    elif textFile.startswith("harmful"):
        #print("harmful")
        fileType = "harmful".encode('utf-8')
    else:
        #print("invalid file name")
        sys.exit(2)
    limit = 0 
    entryCount       = 0
    disease          = ""
    causeOrTreatment = ""
    relation         = ""
    newEntry = False    
    
    
    with open(textFile, "r") as openedTextFile:
        for line in openedTextFile:
            if limit < lim:
                if line.startswith("pmcid   : "): #it's the idNumber
                    entryCount += 1
                    newEntry = True
                elif line.startswith("sentence: "): #it's a sentence
                    pass
                      
                elif line.startswith("entities: "): #it's the two in a relationship
                    disease = line[11:line.index(",")].lower().encode('utf-8')
                    causeOrTreatment = line[(line.index(",")+2):-2].lower().encode('utf-8')
                    
                    #add disease and cause/treatment to dictionary of unique words/phrases
                    if disease not in uniqueWordsDictionary:
                        uniqueWordsDictionary[disease] = {}
                    if causeOrTreatment not in uniqueWordsDictionary:
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
                        sys.exit(2)
            else: break

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


def parseEntitiesIntoUnigrams(beneficialFile, harmfulFile, beneficialLimit, harmfulLimit):
    
    beneficialEntry = 0
    harmfulEntry = 0
    entitiesTrainingDictionary= {}
    
    entityUnigramList           = []
    
    beneficialFullEntitiesList  = []
    harmfulFullEntitiesList     = []
    
    sentenceUnigramList         = []
    
    beneficialSplitSentences    = []
    harmfulSplitSentences       = []
    
    entityUnigrams              = {}
    harmfulUnigrams             = {}
    beneficialUnigrams          = {}
    sentenceFeatureUnigrams             = {}

    testArrayForWritingEntries = numpy.empty(shape = (1, 1), dtype = "S128")
    
    #WORKING ON THE UNIGRAMS OF THE TRAINING BENEFICIAL ENTITIES HERE
    with open(beneficialFile, "r") as openedBeneficialFile:
        for line in openedBeneficialFile:
            if beneficialEntry < beneficialLimit:
                if line.startswith("entities: "):
                    #individual entities
                    disease = line[11:line.index(",")].lower().encode('utf-8')
                    causeOrTreatment = line[(line.index(",")+2):-2].lower().encode('utf-8')     
                    if disease not in entitiesTrainingDictionary:
                        entitiesTrainingDictionary[disease] = {}
                    if causeOrTreatment not in entitiesTrainingDictionary:
                        entitiesTrainingDictionary[causeOrTreatment] = {}  
                    #unigrams composing the entities
                    entityUnigramList = re.split("-|, |\. |\/| ", line[11:-2].lower())                    
                    for entry in entityUnigramList:
                        if (entry != "") and (entry not in entityUnigrams):
                            entityUnigrams[entry] = {}
                    beneficialEntry += 1
            else: break                
    #WORKING ON THE TRAINING HARMFUL ENTITIES HERE
    with open(harmfulFile, "r") as openedHarmfulFile:
        for line in openedHarmfulFile:
            if harmfulEntry < harmfulLimit:
                if line.startswith("entities: "):
                    #individual entities                    
                    disease = line[11:line.index(",")].lower().encode('utf-8')
                    causeOrTreatment = line[(line.index(",")+2):-2].lower().encode('utf-8')                    
                    if disease not in entitiesTrainingDictionary:
                        entitiesTrainingDictionary[disease] = {}
                    if causeOrTreatment not in entitiesTrainingDictionary:
                        entitiesTrainingDictionary[causeOrTreatment] = {}                    
                    entityUnigramList = re.split("-|, |\. |\/| ", line[11:-2].lower())                    
                    for entry in entityUnigramList:
                        if (entry != "")  and (entry not in entityUnigrams):
                            entityUnigrams[entry] = {}
                    harmfulEntry += 1
            else: break
                                       
    beneficialEntry = 0
    mostRecentPMCID = ""
    with open(beneficialFile, "r") as openedBeneficialFile:
        for line in openedBeneficialFile:
            if line.startswith("pmcid   : "): #it's the pmcid line
                mostRecentPMCID = line[11:-1]
            elif line.startswith("sentence: "):
                sentenceUnigramList = re.split("\—|\-|\, |\.|\/|\(|\)|\'|\"|\[|\]|\ |\“|\”|\,|\d|\<|\>|\:|\$|\%|\*|\′", line[10:-2].lower())                    
                beneficialSplitSentences.append(sentenceUnigramList)
                
                if beneficialEntry < beneficialLimit: 
                    for word in sentenceUnigramList:
                        if (word != "") and (word not in entityUnigrams):
                            if word not in sentenceFeatureUnigrams:
                                try: 
                                    testArrayForWritingEntries[0,0] = word
                                    sentenceFeatureUnigrams[word] = {}
                                    sentenceFeatureUnigrams[word]["beneficial"] = {}
                                    sentenceFeatureUnigrams[word]["beneficial"]["pmcid"] = {}
                                    sentenceFeatureUnigrams[word]["beneficial"]["pmcid"][mostRecentPMCID] = {}
                                    sentenceFeatureUnigrams[word]["beneficial"]["count"] = 0
                                    
                                    sentenceFeatureUnigrams[word]["harmful"] = {}
                                    sentenceFeatureUnigrams[word]["harmful"]["pmcid"] = {}
                                    sentenceFeatureUnigrams[word]["harmful"]["count"] = 0
                                except UnicodeEncodeError: pass 
                            else: #it is in the feature unigrams already, so add the 
                                if mostRecentPMCID not in sentenceFeatureUnigrams[word]["beneficial"]["pmcid"]: #and the same pmcid isn't already there
                                    sentenceFeatureUnigrams[word]["beneficial"]["pmcid"][mostRecentPMCID] = {}
                                    
                beneficialEntry += 1
            elif line.startswith("entities: "):
                #individual entities
                disease = line[11:line.index(",")].lower().encode('utf-8')
                causeOrTreatment = line[(line.index(",")+2):-2].lower().encode('utf-8')     
                                          
                beneficialFullEntitiesList.append([disease, causeOrTreatment]) 
                    
            else: pass
                   
                    
    harmfulEntry = 0
    mostRecentPMCID = ""
    with open(harmfulFile, "r") as openedHarmfulFile:
        for line in openedHarmfulFile:
            if line.startswith("pmcid   : "): #it's the pmcid line
                mostRecentPMCID = line[11:-1]                
            elif line.startswith("sentence: "):
                sentenceUnigramList = re.split("\—|\-|\, |\.|\/|\(|\)|\'|\"|\[|\]|\ |\“|\”|\,|\d|\<|\>|\:|\$|\%|\*|\′", line[10:-2].lower())
                harmfulSplitSentences.append(sentenceUnigramList)
                if harmfulEntry < harmfulLimit: 
                    for word in sentenceUnigramList:
                        if (word != "") and (word not in entityUnigrams):
                            if word not in sentenceFeatureUnigrams:
                                try:
                                    testArrayForWritingEntries[0,0] = word
                                    sentenceFeatureUnigrams[word] = {}
                                    sentenceFeatureUnigrams[word]["beneficial"] = {}
                                    sentenceFeatureUnigrams[word]["beneficial"]["pmcid"] = {}
                                    sentenceFeatureUnigrams[word]["beneficial"]["count"] = 0
                                    
                                    sentenceFeatureUnigrams[word]["harmful"] = {}
                                    sentenceFeatureUnigrams[word]["harmful"]["pmcid"] = {}
                                    sentenceFeatureUnigrams[word]["harmful"]["pmcid"][mostRecentPMCID] = {}
                                    sentenceFeatureUnigrams[word]["harmful"]["count"] = 0
                                except UnicodeEncodeError: pass 
                            else:
                                if mostRecentPMCID not in sentenceFeatureUnigrams[word]["harmful"]["pmcid"]: #and the same pmcid isn't already there
                                    sentenceFeatureUnigrams[word]["harmful"]["pmcid"][mostRecentPMCID] = {}
                harmfulEntry += 1
            elif line.startswith("entities: "):
                disease = line[11:line.index(",")].lower().encode('utf-8')
                causeOrTreatment = line[(line.index(",")+2):-2].lower().encode('utf-8')                    
                                 
                harmfulFullEntitiesList.append([disease, causeOrTreatment])
            
            else: pass

                    
                    
                    
    for word in sentenceFeatureUnigrams:
        for benefitHarmfulOrEntity in sentenceFeatureUnigrams[word]:
            #start counting!
            for pmcid in sentenceFeatureUnigrams[word][benefitHarmfulOrEntity]["pmcid"]:
                sentenceFeatureUnigrams[word][benefitHarmfulOrEntity]["count"] += 1
                
        if (sentenceFeatureUnigrams[word]["beneficial"]["count"] > 1) or (sentenceFeatureUnigrams[word]["harmful"]["count"] > 1):
            if sentenceFeatureUnigrams[word]["beneficial"]["count"] > (2*sentenceFeatureUnigrams[word]["harmful"]["count"]):
                beneficialUnigrams[word] = {}
            elif sentenceFeatureUnigrams[word]["harmful"]["count"] > (2*sentenceFeatureUnigrams[word]["beneficial"]["count"]):
                harmfulUnigrams[word] = {}
            else: pass #the words can't be categorized one way or the other
        
                                        
                    
    return (entitiesTrainingDictionary, 
            beneficialUnigrams, harmfulUnigrams, 
            beneficialEntry, harmfulEntry, 
            beneficialSplitSentences, harmfulSplitSentences,
            beneficialFullEntitiesList, harmfulFullEntitiesList)


def main(argv):
    #Python3 training.py beneficial.txt harmful.txt
    if len(argv) != 3:
        print("invalid number of arguments")
        sys.exit(2)
    
    #two separate lists because don't know how many entries in each, so dividing one list will be difficult
    (entitiesTrainingDictionary, beneficialUnigrams, harmfulUnigrams, 
                beneficialCount, harmfulCount, pmcidBeneficialSentences, pmcidHarmfulSentences, 
                beneficialFullEntitiesList, harmfulFullEntitiesList) = parseEntitiesIntoUnigrams(argv[1], argv[2], 10356, 9797)

    benprec = 10356/beneficialCount
    harmprec = 9797/harmfulCount


    numFeatures = len(entitiesTrainingDictionary) + len(beneficialUnigrams) + len(harmfulUnigrams) + 1  #plus 1 for harmful or beneficial
    uniqueFeaturesArray = numpy.empty(shape = (1, numFeatures), dtype="S128")
    
    #place the dictionary words into the array
    for index, feature in enumerate(entitiesTrainingDictionary):
        uniqueFeaturesArray[0, index] = feature

    finalColumn = len(entitiesTrainingDictionary)
    
    for index, feature in enumerate(beneficialUnigrams):
        currentColumn = index + finalColumn
        uniqueFeaturesArray[0, currentColumn] = feature
    finalColumn += len(beneficialUnigrams)

    for index, feature in enumerate(harmfulUnigrams):
        currentColumn = index + finalColumn
        uniqueFeaturesArray[0, currentColumn] = feature 
    
    uniqueFeaturesArray[0][:-1].sort()

    beneficial80Percent = int(beneficialCount * benprec)-1
    beneficial20Percent = int(beneficialCount - beneficial80Percent)
    harmful80Percent    = int(harmfulCount * harmprec)-1
    harmful20Percent    = int(harmfulCount - harmful80Percent)
  
    trainArray = numpy.empty(shape=((beneficial80Percent + harmful80Percent), numFeatures), dtype=numpy.int8) #Default is numpy.float64
    testArray   = numpy.empty(shape=((beneficial20Percent + harmful20Percent), numFeatures), dtype=numpy.int8)
    
    #training data
    for entry in range(0, beneficial80Percent):
        #for each entry, find the index of the given feature
        for word in pmcidBeneficialSentences[entry]:
            #get the index of the given feature
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], word.encode("utf-8"))
            if uniqueFeaturesArray[0][featureColumn] == word.encode("utf-8"):
                trainArray[entry, featureColumn] = 1

        for entity in beneficialFullEntitiesList[entry]:
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], entity)
            if uniqueFeaturesArray[0][featureColumn] == entity:
                trainArray[entry, featureColumn] = 1            
        trainArray[entry, -1] = 1
    
    for entry in range(0, harmful80Percent):
        trainingEntry = entry + beneficial80Percent
        for word in pmcidHarmfulSentences[entry]:
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], word.encode("utf-8"))
            if uniqueFeaturesArray[0][featureColumn] == word.encode("utf-8"):
                trainArray[trainingEntry, featureColumn] = 1            
        for entity in harmfulFullEntitiesList[entry]:    
            #get the index of the given feature
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], entity)
            if uniqueFeaturesArray[0][featureColumn] == entity:
                trainArray[trainingEntry, featureColumn] = 1

    #test data
    for entry in range(0, beneficial20Percent):
        dataEntry = entry + beneficial80Percent #finding next beneficial entry, starting from 60% until 80%        
        for word in pmcidBeneficialSentences[dataEntry]:
            #get the index of the given feature
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], word.encode("utf-8"))
            if uniqueFeaturesArray[0][featureColumn] == word.encode("utf-8"):
                testArray[entry, featureColumn] = 1
                    
        for entity in beneficialFullEntitiesList[dataEntry]:
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], entity)
            if uniqueFeaturesArray[0][featureColumn] == entity:
                testArray[entry, featureColumn] = 1
        testArray[entry, -1] = 1 
        
        
        
    for entry in range(0, harmful20Percent):
        dataEntry = entry + harmful80Percent # finding the next harmful entry starting from 60% until 80%
        testEntry  = entry + beneficial20Percent #because the prior data entered ended with beneficial20Percent

        for word in pmcidHarmfulSentences[dataEntry]:
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], feature.encode("utf-8"))
            if uniqueFeaturesArray[0][featureColumn] == word.encode("utf-8"):
                testArray[testEntry, featureColumn] = 1
              
        for entity in harmfulFullEntitiesList[dataEntry]:
            featureColumn = numpy.searchsorted(uniqueFeaturesArray[0][:-1], entity)
            if uniqueFeaturesArray[0][featureColumn] == entity:
                testArray[testEntry, featureColumn] = 1
            
 
    ###################################################CLASSIFICATION SECTION################################################################
    
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

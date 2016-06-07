#AUTHOR: SPIRO RAZIS
import sys
import os
from operator import itemgetter

def file_80_20Splitter(beneficialFile, harmfulFile):
    
    pseorData = [] #pseor: pmcid, sentence, entities, offset, relation
    beneficialData = []
    beneficialEntityPairs = {}
    
    with open(beneficialFile, "r") as openedBeneficialFile:
        for line in openedBeneficialFile:
            if line != "\n":
                if line.startswith("entities: "): #it's the two in a relationship
                    entityPair = line[10:-1].lower().encode('utf-8')
                    if entityPair not in beneficialEntityPairs:
                        beneficialEntityPairs[entityPair] = {}
                        #print(entityPair)
                pseorData.append(line)
            else: 
                beneficialData.append(pseorData)
                pseorData = []
                
    beneficial80Percent = int(len(beneficialEntityPairs) * 0.8)
    beneficialEntityPairs_80 = {}

    for index, pair in enumerate(beneficialEntityPairs):
        if index < beneficial80Percent:
            beneficialEntityPairs_80[pair] = {}

    #["pmcid...", "sentence...", "entities...", "offsets...", "relation..."]

    beneficialData_80Percent = []
    beneficialData_20Percent = []

    for entry in beneficialData:
        if entry[2][10:-1].lower().encode('utf-8') in beneficialEntityPairs_80:
            beneficialData_80Percent.append(entry)
            #print("80 Percent: ")
            #print(entry)
        else: 
            beneficialData_20Percent.append(entry)
            #print("20 Percent:" )
            #print(entry)


    
    beneficialData_80Percent.sort(key=itemgetter(2), reverse=False)
    beneficialData_20Percent.sort(key=itemgetter(2), reverse=False)
    
    try: os.remove("beneficial_80_20_Split.txt")
    except OSError: pass
    
    print("Beneficial Entries: First 80 Percent of Entity Pairs: %d" %(len(beneficialData_80Percent)))
    
    with open("beneficial_80_20_Split.txt", "w") as splitBeneficialOutput:
        for pseorEntry in beneficialData_80Percent:
            for line in pseorEntry:
                splitBeneficialOutput.write(line)
            splitBeneficialOutput.write("\n")
    
        for pseorEntry in beneficialData_20Percent:
            for line in pseorEntry:
                splitBeneficialOutput.write(line)
            splitBeneficialOutput.write("\n")            
    
    
    ##########
    #HARMFUL VERSION
    
    pseorData = [] #pseor: pmcid, sentence, entities, offset, relation
    harmfulData = []
    harmfulEntityPairs = {}
    
    with open(harmfulFile, "r") as openedHarmfulFile:
        for line in openedHarmfulFile:
            if line != "\n":
                if line.startswith("entities: "): #it's the two in a relationship
                    entityPair = line[10:-1].lower().encode('utf-8')
                    if entityPair not in harmfulEntityPairs:
                        harmfulEntityPairs[entityPair] = {}
                pseorData.append(line)
            else: 
                harmfulData.append(pseorData)
                pseorData = []
                
    harmful80Percent = int(len(harmfulEntityPairs) * 0.8)
    harmfulEntityPairs_80 = {}

    for index, pair in enumerate(harmfulEntityPairs):
        if index < harmful80Percent:
            harmfulEntityPairs_80[pair] = {}

    #["pmcid...", "sentence...", "entities...", "offsets...", "relation..."]

    harmfulData_80Percent = []
    harmfulData_20Percent = []

    for entry in harmfulData:
        if entry[2][10:-1].lower().encode('utf-8') in harmfulEntityPairs_80:
            harmfulData_80Percent.append(entry)
        else: 
            harmfulData_20Percent.append(entry)
    
    harmfulData_80Percent.sort(key=itemgetter(2), reverse=False)
    harmfulData_20Percent.sort(key=itemgetter(2), reverse=False)
    
    
    
    try: os.remove("harmful_80_20_Split.txt")
    except OSError: pass
    
    print("Harmful Entries: First 80 Percent of Entity Pairs: %d" %(len(harmfulData_80Percent)))
    
    with open("harmful_80_20_Split.txt", "w") as splitHarmfulOutput:
        for pseorEntry in harmfulData_80Percent:
            for line in pseorEntry:
                splitHarmfulOutput.write(line)
            splitHarmfulOutput.write("\n")
    
        for pseorEntry in harmfulData_20Percent:
            for line in pseorEntry:
                splitHarmfulOutput.write(line)
            splitHarmfulOutput.write("\n")            

    return


def main(argv):

    file_80_20Splitter(argv[1], argv[2])

    sys.exit(0)





main(sys.argv)
#






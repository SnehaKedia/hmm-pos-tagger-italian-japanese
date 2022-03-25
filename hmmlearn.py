#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import time
# start = time.time()


# ### Importing all packages

# In[2]:


import sys
from collections import Counter


# ### Functions for transition, emission and first word probabilities

# In[3]:


def getTransitionProbabilities():
    transitionProbabilities = {}
    for transition in transitionsFreq:
        startTag, endTag = transition.split('->')
        transitionProbabilities[transition] = (transitionsFreq[transition] + 1) / (transitionTagsFreq[startTag] + len(uniqueTags))
    ## divide by zero may occur, we can use log or avoid the zero situation
    for tag in uniqueTags:
        newTransition = tag + "->UNKNOWN"
        transitionProbabilities[newTransition] = 1 / (transitionTagsFreq[tag] + len(uniqueTags))
    return transitionProbabilities

def getEmissionProbabilities():
    emissionProbabilities = {}
    for emission in emissionsFreq:
        word, tag = emission.rsplit("/", 1)
        emissionProbabilities[emission] = emissionsFreq[emission] / emissionTagsFreq[tag]
    return emissionProbabilities

def getFirstWordProbabilities():
    firstWordProbabilities = {}
    for tag in firstWordTagsFreq:
        firstWordProbabilities[tag] = firstWordTagsFreq[tag] / totalLines
    return firstWordProbabilities
    


# ### Accesing the input file

# In[4]:


pathToInputFile = sys.argv[1]
# pathToInputFile = 'hmm-training-data/it_isdt_train_tagged.txt'
# pathToInputFile = 'hmm-training-data/ja_gsd_train_tagged.txt'

with open(pathToInputFile, 'r', encoding='utf-8', errors='ignore') as file:
    lines = file.read().splitlines()
    file.close()


# ### Processing the input file

# In[5]:


firstWordTagsFreq = {}
emissionsFreq = {}
emissionTagsFreq = {}
transitionsFreq = {}
transitionTagsFreq = {}

uniqueWords = set()
uniqueTags = set()
uniqueWordsPerTag = {}

# wordsPerTag = {}

totalLines = len(lines)

for line in lines:
    words = line.split()
    
    firstWord = words[0].split("/")[-1]
    if firstWord not in firstWordTagsFreq:
        firstWordTagsFreq[firstWord] = 1
    else:
        firstWordTagsFreq[firstWord] += 1
    
    for i, emission in enumerate(words):
        currentWord, currentTag = emission.rsplit("/", 1)
        uniqueWords.add(currentWord)
        uniqueTags.add(currentTag)
        
        if emission not in emissionsFreq:
            emissionsFreq[emission] = 1
        else:
            emissionsFreq[emission] += 1
            
        if currentTag not in emissionTagsFreq:
            emissionTagsFreq[currentTag] = 1
        else:
            emissionTagsFreq[currentTag] += 1
        
        if i < len(words) - 1:
            nextTag = words[i+1].rsplit("/", 1)[1]
            transition = currentTag + "->" + nextTag ## creating string depicting transition by taking tag of the current word and the next word
            
            if transition not in transitionsFreq:
                transitionsFreq[transition] = 1
            else:
                transitionsFreq[transition] += 1
            
            if currentTag not in transitionTagsFreq:
                transitionTagsFreq[currentTag] = 1
            else:
                transitionTagsFreq[currentTag] += 1
        
        ## we do not need the state value, just the count 
        ## but since we want unique number of states, we store them in a set first then calculate length
        
        if currentTag not in uniqueWordsPerTag:
            uniqueWordsPerTag[currentTag] = set()
        uniqueWordsPerTag[currentTag].add(currentWord)
            
        # if currentTag not in wordsPerTag:
            # wordsPerTag[currentTag] = []
        # wordsPerTag[currentTag].append(currentWord)
        
for tag, wordList in uniqueWordsPerTag.items():
    uniqueWordsPerTag[tag] = len(wordList)
    
uniqueWordsPerTag = dict(sorted(uniqueWordsPerTag.items(), key=lambda item: -item[1]))


# ### Calculating probabilities and creating the Hidden Markov Model

# In[6]:


uniqueWords = list(uniqueWords)
uniqueTags = list(uniqueTags)

transitionProbabilities = getTransitionProbabilities()
emissionProbabilities = getEmissionProbabilities()
firstWordProbabilities = getFirstWordProbabilities()


# ### Writing into hmmmodel file

# In[7]:


pathToOutputFile = 'hmmmodel.txt'
with open(pathToOutputFile, 'w') as file:
    file.write("transitionProbabilities=" + str(dict(transitionProbabilities)) + "\n")
    file.write("emissionProbabilities=" + str(dict(emissionProbabilities)) + "\n")
    file.write("firstWordProbabilities=" + str(dict(firstWordProbabilities)) + "\n")
    file.write("uniqueWordsPerTag=" + str(dict(uniqueWordsPerTag)) + "\n")
    file.write("uniqueWords=" + str(uniqueWords) + "\n")
    file.write("uniqueTags=" + str(uniqueTags) + "\n")
    file.close()


# In[8]:


# end = time.time()
# print(end-start)


# ### ------------------------------------------------------------------------------------------------

# In[9]:

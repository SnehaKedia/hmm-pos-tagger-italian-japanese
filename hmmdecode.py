#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import time
# start = time.time()


# ### Importing all packages

# In[2]:


import sys
import ast


# ### Functions for Viterbi Algorithm

# In[3]:


def getMaxProbabilityOfLastTag(words, probabilityMatrix):
    maxProb = -1
    index = -1
    for iTag in range(len(uniqueTags)):
        currentProb = probabilityMatrix[iTag][len(words) - 1]
        if maxProb < currentProb:
            maxProb = currentProb
            index = iTag
            tag = uniqueTags[iTag]
    return index, tag

def getPrediction(words, probabilityMatrix, parentMatrix):
    ilastWordTag, lastWordTag = getMaxProbabilityOfLastTag(words, probabilityMatrix)
    predictedTags = [lastWordTag]
    iRow = ilastWordTag
    iCol = len(words) - 1
    while iCol > 0:
        iRow = parentMatrix[iRow][iCol]
        predictedTags = [uniqueTags[iRow]] + predictedTags
        iCol -= 1
    return predictedTags

def getTaggedLine(words, prediction):
    taggedLine = ""
    for iTag, word in enumerate(words):
        taggedLine += word + "/" + prediction[iTag] + " "
    return taggedLine.strip()


# ### Processing the model file

# In[4]:


pathToModelFile = 'hmmmodel.txt'
with open(pathToModelFile, 'r') as file:
    lines = file.readlines()
    file.close()

model = {}
for line in lines:
    key, value = line.split('=', 1)
    key = key.strip()
    value = value.strip()
    value = ast.literal_eval(value)
    model[key] = value

transitionProbabilities = model['transitionProbabilities']
emissionProbabilities = model['emissionProbabilities']
firstWordProbabilities = model['firstWordProbabilities']
uniqueWordsPerTag = model['uniqueWordsPerTag']
uniqueWords = model['uniqueWords']
uniqueTags = model['uniqueTags']


# In[5]:


trainedWords = set(uniqueWords)
    
firstWordTags = set(firstWordProbabilities.keys())

top5CommonTags = list(uniqueWordsPerTag.keys())[:5] ## If an unseen word is encountered, use top 5 tags for prediction


# ### Accessing input file

# In[6]:


pathToInputFile = sys.argv[1]
# pathToInputFile = 'hmm-training-data/it_isdt_dev_raw.txt'
# pathToInputFile = 'hmm-training-data/ja_gsd_dev_raw.txt'

with open(pathToInputFile, 'r', encoding='utf-8', errors='ignore') as file:
    lines = file.read().splitlines()
    file.close()


# ### Viterbi Algorithm

# In[7]:


taggedLines = ""
for line in lines:
    words = line.split()
    probabilityMatrix = [[0]*len(words) for i in range(len(uniqueTags))]
    parentMatrix = [[0]*len(words) for i in range(len(uniqueTags))]
    for iWord in range(len(words)):
        tagsToLoop = uniqueTags
        if words[iWord] not in trainedWords:
            #### Try the spelling and suffix-prefix technique here
            tagsToLoop = top5CommonTags
        for i, currentTag in enumerate(tagsToLoop):
            word = words[iWord]
            emission = word + "/" + currentTag
            ## If an unseen word is encountered, let transition probability decide from top 5 tags
            if word not in trainedWords:
                emissionProb = 1
            else:
                emissionProb = 0 if emission not in emissionProbabilities else emissionProbabilities[emission]
            
            iTag = i if word in trainedWords else uniqueTags.index(currentTag) ## Can use a dictionary
            
            ## If first word then set probability accordingly
            if iWord == 0:
                probabilityMatrix[iTag][iWord] = 0 if currentTag not in firstWordTags else emissionProb * firstWordProbabilities[currentTag]
            else:
                maxTransitionProb = -1
                iMaxTransitionProbTag = -1
                for iPrevTag, prevTag in enumerate(uniqueTags):
                    transition = prevTag + "->" + currentTag
                    if probabilityMatrix[iPrevTag][iWord - 1] == 0:
                        currentProb = 0
                    else:
                        if transition not in transitionProbabilities:
                            transition = prevTag + "->UNKNOWN"
                        transitionProb = transitionProbabilities[transition]
                        currentProb = probabilityMatrix[iPrevTag][iWord - 1] * transitionProb
                    if currentProb > maxTransitionProb:
                        maxTransitionProb = currentProb
                        iMaxTransitionProbTag = iPrevTag
                parentMatrix[iTag][iWord] = iMaxTransitionProbTag
                probabilityMatrix[iTag][iWord] = 0 if maxTransitionProb == 0 else emissionProb * maxTransitionProb
    prediction = getPrediction(words, probabilityMatrix, parentMatrix)
    taggedLines += getTaggedLine(words, prediction) + "\n"


# ### Writing into hmmoutput file

# In[8]:


pathToOutputFile = 'hmmoutput.txt'

with open(pathToOutputFile, 'w') as file:
    file.write(taggedLines)
    file.close()


# In[9]:


# end = time.time()
# print(end-start)


# ### ------------------------------------------------------------------------------------------------

# In[10]:

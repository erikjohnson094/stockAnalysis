from compilePatterns import compile_patterns
from utilities import assemble_dir
from utilities import read_compiled_states
from utilities import write_compiled_patterns
import numpy as np
from datetime import datetime
startTime=datetime.now()
def sum_compiled_states(ticker,year,month,days):
    compiledStates=[]
    for day in days:
        filepath=assemble_dir(ticker,year,month,day)+'/compiledStates.txt'
        fileObject=open(filepath,'r')
        states=read_compiled_states(fileObject)
        fileObject.close()
        for state in states:
            compiledStates.append(state)
    return compiledStates



def read_active_keys(state):
    multipleElementNames=['pm|1', 'pm|2', 'pm|5', 'pm|10', 'pm|15', 'pm|30', 'pm|45', 'pm|60', 'pm|90', 'pm|120', 'pm|180', 'pm|240', 'pm|300', 'vl|5', 'vl|10', 'vl|30', 'vl|60', 'vl|120', 'vl|240', 'pr|1', 'pr|2', 'pr|5', 'pr|10', 'pr|15', 'pr|30', 'pr|45', 'pr|60', 'pr|90', 'pr|120', 'pr|180', 'pr|240', 'pr|300']
    keyList=list(state.keys())
    usedKeys=[]
    for key in keyList:
        used=False
        if key in multipleElementNames:
            for value in state[key].keys():
                if float(state[key][value])!=0.0:
                    used=True
        if used:
            usedKeys.append(key)
    return usedKeys

def get_seed_velocities(ticker,year,month,days):
    patterns=compile_patterns(ticker,year,month,days)
    velocities=[]
    for key in patterns.keys():
        pattern=patterns[key]
        for smallKey in pattern.keys():
            singlePattern=pattern[smallKey]
            for eachValue in singlePattern.keys():
                totalWeight=singlePattern[eachValue]['totalWeight']
                if totalWeight>0:
                    weightedVelocity=singlePattern[eachValue]['weightedVelocity']
                    totalCount=singlePattern[eachValue]['totalCount']
                    velocities.append(weightedVelocity/totalWeight)
    return velocities

def read_primary_keys(state,ignores):
    keyList=[]
    for possibleKey in state.keys():
        if possibleKey not in ignores:
            keyList.append(possibleKey)
    primaryKeys=[]
    for i in range(len(keyList)):
        for j in range(len(keyList)):
            if i==j:
                primaryKey=keyList[i]
            else:
                twoKeys=sorted([keyList[i],keyList[j]])
                primaryKey=twoKeys[0]+'^'+twoKeys[1]
            if primaryKey not in primaryKeys:
                primaryKeys.append(primaryKey)
    return primaryKeys



magnifier=.01


hours=16
numMinutes=hours*60
intervalLength=5
numIntervals=numMinutes/intervalLength

def find_volume_bin(keyParameters,volume):
    volBins=list(keyParameters.keys())
    for i in range(len(volBins)):
        if i==0:
            if volume<volBins[i]:
                return volBins[i]
        else:
            if volBins[i]<=volume<volBins[i+1]:
                return volBins[i]

def find_velocity_modifiers(stateKey,stateValue,valueWeight,thisPattern):
    splitKey=stateKey.split('|')
    keyParameters=thisPattern[stateKey]
    if splitKey[0]=='vl':
        patternBin=find_volume_bin(keyParameters,stateValue)
    else:
        patternBin=stateValue
    patternTraits=thisPattern[stateKey][patternBin]
    weightedVelocity=patternTraits['weightedVelocity']
    weight=patternTraits['totalWeight']
    if weight>0:
        normalizedVelocity=weightedVelocity/weight
        modifiedWeight=weight*valueWeight
    else:
        normalizedVelocity=0
        modifiedWeight=0
    return normalizedVelocity,modifiedWeight

def find_weighted_average(normalizedVelocities,weightModifiers):
    totalVel=0.0
    totalWeight=0.0
    if len(normalizedVelocities)!=len(weightModifiers):
        raise KeyError('Mismatch in list lengths for find_weighted_average')
    else:
        for i in range(len(weightModifiers)):
            totalVel+=normalizedVelocities[i]*weightModifiers[i]
            totalWeight+=weightModifiers[i]
    weightedVelocity=totalVel/totalWeight
    return weightedVelocity

def estimate_velocity(state,patterns):
    ignores=['velocity','price','time','volume','priceDifference','volumeDifference','timeInterval']
    floatValues=['velocity','price','time','volume','priceDifference','volumeDifference','timeInterval','wkd','hr']
    primaryKeys=read_primary_keys(state,ignores)
    velocity=0.0
    normalizedVelocities=[]
    weightModifiers=[]
    usedPatterns=[]
    for primaryKey in primaryKeys:
        splitPrimaryKey=primaryKey.split('^')
        thisPattern=patterns[primaryKey]
        for eachKey in splitPrimaryKey:
            patternKeyData=thisPattern[eachKey]
            if eachKey in floatValues:
                value=state[eachKey]
                normalizedVelocity,modifiedWeight=find_velocity_modifiers(eachKey,value,1.0,thisPattern)
                if modifiedWeight>0:
                    normalizedVelocities.append(normalizedVelocity)
                    weightModifiers.append(modifiedWeight)
                    usedPatterns.append({'primaryKey':primaryKey,'eachKey':eachKey,'value':value})
            else:
                valueWeights=list(state[eachKey].keys())
                splitKey=eachKey.split('|')
                if splitKey[0]=='vl':
                    for value in valueWeights:
                        weight=state[eachKey][value]
                        normalizedVelocity,modifiedWeight=find_velocity_modifiers(eachKey,value,weight,thisPattern)
                        if modifiedWeight>0:
                            normalizedVelocities.append(normalizedVelocity)
                            weightModifiers.append(modifiedWeight)
                            keyParameters=thisPattern[eachKey]
                            volBin=find_volume_bin(keyParameters,value)
                            usedPatterns.append({'primaryKey':primaryKey,'eachKey':eachKey,'value':volBin})
                else:
                    for value in valueWeights:
                        weight=state[eachKey][value]
                        normalizedVelocity,modifiedWeight=find_velocity_modifiers(eachKey,value,weight,thisPattern)
                        if modifiedWeight>0:
                            normalizedVelocities.append(normalizedVelocity)
                            weightModifiers.append(modifiedWeight)
                            usedPatterns.append({'primaryKey':primaryKey,'eachKey':eachKey,'value':value})
    weightedVelocity=find_weighted_average(normalizedVelocities,weightModifiers)
    return weightedVelocity,usedPatterns

def optimize_patterns(trueVelocity,patterns,usedPatterns,speedFactor):
    offsets=[]
    for i in range(len(usedPatterns)):
        patternFactors=usedPatterns[i]
        primaryKey=patternFactors['primaryKey']
        eachKey=patternFactors['eachKey']
        value=patternFactors['value']
        thesePatternTraits=patterns[primaryKey][eachKey][value]
        totalWeight=thesePatternTraits['totalWeight']
        weightedVelocity=thesePatternTraits['weightedVelocity']
        totalCount=thesePatternTraits['totalCount']
        if totalWeight>0:
            normalizedVelocity=weightedVelocity/totalWeight
            velocityDifference=normalizedVelocity-trueVelocity
            if float(normalizedVelocity)==0.0:
                percentOffset=1
            else:
                percentOffset=velocityDifference/abs(normalizedVelocity)
            offsets.append(percentOffset)
            offsetRatio=min((speedFactor*100/totalCount),1.0)
            newWeightedVelocity=weightedVelocity-(offsetRatio*percentOffset)
            patterns[primaryKey][eachKey][value]['weightedVelocity']=newWeightedVelocity
            patterns[primaryKey][eachKey][value]['totalCount']=totalCount+(100*speedFactor)
            
    return patterns,offsets

def store_updated_patterns(ticker,patterns):
    filepath='Stocks/'+ticker+'/learnedPatterns.txt'
    fileObject=open(filepath,'w')
    write_compiled_patterns(patterns,fileObject)
    fileObject.close()


if __name__=='__main__':
    iterations=0
    allOffsets=[]
    statesIterated=0
    while True:
        portfolio=['AAPL']
        days=['18','19','20','21','22']
        for ticker in portfolio:
            year,month='2017','12'
            if iterations==0:
                patterns=compile_patterns(ticker,year,month,days)
            else:
                patterns=new_patterns
            compiledStates=sum_compiled_states(ticker,year,month,days)
            for i in range(len(compiledStates)):
                statesIterated+=1
                state=compiledStates[i]
                calculatedVelocity,usedPatterns=estimate_velocity(state,patterns)
                if i!=0:
                    trueVelocity=state['velocity']
                    new_patterns,offsets=optimize_patterns(trueVelocity,patterns,usedPatterns,.5)
                    for offset in offsets:
                        allOffsets.append(abs(100*offset))
            iterations+=1
        runTime=datetime.now()-startTime
        
        print('Iterations:',iterations)
        print('States iterated:',statesIterated)
        print('Runtime:',runTime)
        print('Mean:',np.mean(allOffsets))
        print('Median:',np.median(allOffsets))
        print('Min:',min(allOffsets))
        print('Max:',max(allOffsets))
        print(new_patterns)
        store_updated_patterns(ticker,new_patterns)
        #newPatterns=optimize_patterns(patterns,compiledStates)
        
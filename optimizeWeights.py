from datetime import datetime
startTime=datetime.now()
from compilePatterns import compile_patterns
from utilities import assemble_dir
from utilities import read_compiled_states
from utilities import write_compiled_patterns_dict
import numpy as np

print('STARTED',startTime)
def sum_compiled_states(ticker,dayMonthYears):
    compiledStates=[]
    for dayMonthYear in dayMonthYears:
        day,month,year=dayMonthYear
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
    stateValue=round(stateValue,4)
    splitKey=stateKey.split('|')
    keyParameters=thisPattern[stateKey]
    if splitKey[0]=='vl':
        patternBin=find_volume_bin(keyParameters,stateValue)
    else:
        patternBin=stateValue
    if patternBin==None:
        return 0.0,0.0
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
    if np.isnan(weightedVelocity):
        weightedVelocity=0
    return weightedVelocity,usedPatterns

def add_true_velocity(trueVelocity,usedPatterns,patterns):
    for i in range(len(usedPatterns)):
        patternFactors=usedPatterns[i]
        primaryKey=patternFactors['primaryKey']
        eachKey=patternFactors['eachKey']
        value=patternFactors['value']
        thesePatternTraits=patterns[primaryKey][eachKey][value]
        if trueVelocity!=0.0:
            thesePatternTraits['velocities'].append(trueVelocity)
    return patterns

def store_updated_patterns(ticker,patterns):
    filepath='Stocks/'+ticker+'/learnedPatterns2.txt'
    fileObject=open(filepath,'w')
    write_compiled_patterns_dict(patterns,fileObject)
    fileObject.close()

def init_patterns(patterns):
    for primaryKey in patterns.keys():
        for stateKey in patterns[primaryKey].keys():
            for value in patterns[primaryKey][stateKey].keys():
                patterns[primaryKey][stateKey][value]['velocities']=[]
    return patterns


def add_true_velocities(compiledStates,patterns):
    for i in range(len(compiledStates)):
        state=compiledStates[i]
        calculatedVelocity,usedPatterns=estimate_velocity(state,patterns)
        if i!=0:
            trueVelocity=state['velocity']
            patterns=add_true_velocity(trueVelocity,usedPatterns,patterns)
    return patterns



def update_velocities(patterns,speedFactor):
    offsets=[]
    for primaryKey in patterns.keys():
        for stateKey in patterns[primaryKey].keys():
            for value in patterns[primaryKey][stateKey].keys():
                theseTraits=patterns[primaryKey][stateKey][value]
                medianVelocity=np.median(theseTraits['velocities'])
                weightedVelocity=theseTraits['weightedVelocity']
                weight=theseTraits['totalWeight']
                count=theseTraits['totalCount']
                if weight!=0.0 and weightedVelocity!=0.0:
                    normalizedVelocity=weightedVelocity/weight
                    velocityDifference=normalizedVelocity-medianVelocity
                    percentDifference=velocityDifference/normalizedVelocity
                    offsets.append(100*percentDifference)
                    if percentDifference<5:
                        patterns[primaryKey][stateKey][value]['weightedVelocity']=weight*normalizedVelocity*(1-percentDifference*speedFactor)
                    else:
                        patterns[primaryKey][stateKey][value]['weightedVelocity']=weight*medianVelocity
                else:
                    patterns[primaryKey][stateKey][value]['weightedVelocity']=weight*medianVelocity
                for numericKey in patterns[primaryKey][stateKey][value].keys():
                    if numericKey!='velocities':
                        if np.isnan(patterns[primaryKey][stateKey][value][numericKey]):
                            patterns[primaryKey][stateKey][value][numericKey]=0.0
                patterns[primaryKey][stateKey][value]['velocities']=[]
    return patterns,offsets


dayMonthYears=[(18,12,2017),
               (19,12,2017),
               (20,12,2017),
               (21,12,2017),
               (22,12,2017),
               (28,12,2017),
               (2,1,2018),
               (3,1,2018)]

if __name__=='__main__':
    iterations=0
    numTotalIterations=8
    statesIterated=0
    done=['AMD','AMZN','BABA',]
    portfolio=['GE','GM','LIT','RIOT','SHLD','TAL','TSLA','TXN']
    for ticker in portfolio:
        for i in range(numTotalIterations):
            if iterations==0:
                patterns=compile_patterns(ticker,dayMonthYears)
            init_patterns(patterns)
            compiledStates=sum_compiled_states(ticker,dayMonthYears)
            patterns=add_true_velocities(compiledStates,patterns)
            patterns,allOffsets=update_velocities(patterns,.05)
            statesIterated+=len(compiledStates)
            iterations+=1
            runTime=datetime.now()-startTime
            print('Ticker:',ticker)
            print('Iterations:',iterations)
            print('States iterated:',statesIterated)
            print('Runtime:',runTime)
            print('Mean:',np.mean(allOffsets))
            print('Median:',np.median(allOffsets))
            print('Min:',min(allOffsets))
            print('Max:',max(allOffsets))
            print('Stdev:',np.std(allOffsets))
            store_updated_patterns(ticker,patterns)
            #newPatterns=optimize_patterns(patterns,compiledStates)
        
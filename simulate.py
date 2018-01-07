from compilePatterns import compile_patterns
from datetime import datetime
from datetime import timedelta
from utilities import get_snapshot
from utilities import get_quote
from utilities import read_compiled_patterns
from utilities import get_date
from utilities import timeToUTCMills
from intervals import compile_intervals_from_snapshots
from states import compile_states_from_intervals
from optimizeWeights import estimate_velocity
from compilePatterns import compile_these_patterns
import numpy as np
from random import shuffle
done=[]
hold=['AMD','AMZN','BABA','GE','GM','LIT','RIOT','SHLD','TAL','TSLA','TXN','IYW']
portfolio=['AAPL',]



def get_seed_velocities(ticker,dayMonthYears):
    for dayMonthYear in dayMonthYears:
        day,month,year=dayMonthYear
        patterns=compile_patterns(ticker,dayMonthYears)
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

def estimate_future_price(ticker,seedVelocity,numIterations,startDayMonthYear,endDayMonthYear):
    velocitySpeed=.3
    day,month,year=startDayMonthYear
    startTime=datetime(day=day,month=month,year=year,hour=9,minute=30)
    startUTC=timeToUTCMills(startTime)
    day,month,year=endDayMonthYear
    endTime=datetime(day=day,month=month,year=year,hour=16)
    td=endTime-startTime
    numDays=td.days
    hours=float(numDays*6.5)
    filepath='Stocks/'+ticker+'/learnedPatterns2.txt'
    fileObject=open(filepath,'r')
    learnedPatterns=compile_these_patterns(ticker,fileObject)
    timeInterval=60*hours/numIterations
    avgVol=float(get_quote(ticker)['avgTotalVolume'])
    numIterationsPerDay=numIterations/numDays
    iterationVolume=float(avgVol/numIterationsPerDay)
    for i in range(numIterations):
        if i==0:
            initialSnapshot,quotes=get_snapshot(ticker)
            initialSnapshot['velocity']=seedVelocity
            snapshots=[initialSnapshot]
            initialSnapshot['time']=startUTC
        elif i==1:
            secondSnapshot={}
            for key in initialSnapshot.keys():
                secondSnapshot[key]=initialSnapshot[key]
            secondSnapshot['time']=int(secondSnapshot['time'])
            secondSnapshot['price']=float(secondSnapshot['price'])
            secondSnapshot['volume']=int(secondSnapshot['volume'])
            secondSnapshot['time']+=(timeInterval*60000)
            secondSnapshot['price']=secondSnapshot['price']*(1+(secondSnapshot['velocity']*timeInterval))
            secondSnapshot['volume']+=iterationVolume
            snapshots.append(secondSnapshot)
        elif i==2:
            thirdSnapshot={}
            for key in secondSnapshot.keys():
                thirdSnapshot[key]=secondSnapshot[key]
            thirdSnapshot['time']=int(thirdSnapshot['time'])
            thirdSnapshot['price']=float(thirdSnapshot['price'])
            thirdSnapshot['volume']=int(thirdSnapshot['volume'])
            thirdSnapshot['time']+=(timeInterval*60000)
            thirdSnapshot['price']=thirdSnapshot['price']*(1+(thirdSnapshot['velocity']*timeInterval))
            thirdSnapshot['volume']+=iterationVolume
            snapshots.append(thirdSnapshot)
        else:
            intervals=compile_intervals_from_snapshots(snapshots)
            states=compile_states_from_intervals(intervals)
            state=states[-1]
            estimatedVelocity,usedPatterns=estimate_velocity(state,learnedPatterns)
            lastSnapshot=snapshots[i-1]
            lastVelocity=lastSnapshot['velocity']
            lastVolume=lastSnapshot['volume']
            lastPrice=lastSnapshot['price']
            lastTime=lastSnapshot['time']
            newVelocity=lastVelocity*(1-velocitySpeed)+(velocitySpeed)*estimatedVelocity
            newPrice=lastSnapshot['price']*(1+newVelocity*timeInterval)
            randomVolume=-1
            while randomVolume<0:
                randomVolume=np.random.normal(iterationVolume,iterationVolume/3,1)
                randomVolume=randomVolume[0]
            newVolume=lastVolume+randomVolume
            newTime=lastTime+(timeInterval*60000)
            newSnapshot={'price':newPrice,'volume':newVolume,'time':newTime,'velocity':newVelocity}
            if get_date(newTime)[3]>=16:
                newSnapshot['time']=newTime+int(17.5*60*60*1000)
            
            snapshots.append(newSnapshot)
    return snapshots[-1]['price']
    
def stats(listOfFloats):
    print('Length:',len(listOfFloats))
    print('Mean:',np.mean(listOfFloats))
    print('Median:',np.median(listOfFloats))
    print('Stdev:',np.std(listOfFloats))
    print('Min:',min(listOfFloats))
    print('Max:',max(listOfFloats))
    
if __name__=='__main__':
    dayMonthYears=[(18,12,2017),
               (19,12,2017),
               (20,12,2017),
               (21,12,2017),
               (22,12,2017),
               (28,12,2017),
               (29,12,2017),
               (2,1,2018),
               (3,1,2018)]
    startDayMonthYear=(8,1,2018)
    endDayMonthYear=(12,1,2018)
    numIterations=50
    seedsPerTicker=50
    endPrices=[]
    for ticker in portfolio:
        tickerSeeds=0
        seedVelocities=get_seed_velocities(ticker,dayMonthYears)
        shuffle(seedVelocities)
        for seedVelocity in seedVelocities:
            if abs(seedVelocity)<.0002:
                tickerSeeds+=1
                if tickerSeeds<=seedsPerTicker:
                    estimatedEndPrice=estimate_future_price(ticker,seedVelocity,numIterations,startDayMonthYear,endDayMonthYear)
                    endPrices.append(estimatedEndPrice)
                    if len(endPrices)%10==0:
                        stats(endPrices)
    print(ticker,endPrices)
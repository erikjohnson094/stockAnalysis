from datetime import datetime
startTime=datetime.now()
from intervals import read_intervals
from utilities import assemble_dir
from utilities import remove_outliers
from utilities import write_compiled_states
from intervals import write_day_intervals
from utilities import read_compiled_states
portfolio=['AAPL','ADI','ALB','AMD','AMZN','ANF','ATVI','BABA','BHGE','EA','EGHT','FMC','GE','GGP','GILD','GM','GME',
           'GOOG','HAL','HD','HON','INTC','JCP','LIT','M','MDT','MSFT','NFLX','NVDA','QCOM','RIOT','RNG','SHLD','SHOP',
           'SLB','SNE','SQ','SQM','STMP','SYF','TAL','TGT','TJX','TSLA','TWX','TXN','UA','UTX','VNQ','XNET','AEP','BDX','CB','EIX',
           'GLW','INTU','MMM','NSC','PX','SHW','SNX','TXN','XEL','IYW']

def state_variables():
    priceMoveIntervals=[1,2,5,10,15,30,45,60,90,120,180,240,300]
    volumeIntervals=[5,10,30,60,120,240]
    parityIntervals=[1,2,5,10,15,30,45,60,90,120,180,240,300]
    svNames={'wkd':'weekday','hr':'hour'}
    svIntervals={}
    for i in range(len(priceMoveIntervals)):
        key='pm|'+str(priceMoveIntervals[i])
        value='priceMove'+str(priceMoveIntervals[i])+'Mins'
        svNames[key]=value
        if i==len(priceMoveIntervals)-1:
            interval=[priceMoveIntervals[i],400]
        else:
            interval=[priceMoveIntervals[i],priceMoveIntervals[i+1]]
        svIntervals[key]=interval
    for i in range(len(volumeIntervals)):
        key='vl|'+str(volumeIntervals[i])
        value='newVol'+str(volumeIntervals[i])+'Mins'
        svNames[key]=value
        if i==len(volumeIntervals)-1:
            interval=[volumeIntervals[i],400]
        else:
            interval=[volumeIntervals[i],volumeIntervals[i+1]]
        svIntervals[key]=interval
    for i in range(len(parityIntervals)):
        key='pr|'+str(parityIntervals[i])
        value='parity'+str(parityIntervals[i])+'Mins'
        svNames[key]=value
        if i==len(parityIntervals)-1:
            interval=[parityIntervals[i],400]
        else:
            interval=[parityIntervals[i],parityIntervals[i+1]]
        svIntervals[key]=interval
    return svNames,svIntervals


def price_movement(newInterval,oldInterval):
    percentMovement=(newInterval['price']-oldInterval['price'])/oldInterval['price']
    return percentMovement

def volume_movement(newInterval,oldInterval):
    
    newVolume=newInterval['volume']-oldInterval['volume']
    return newVolume

def parity(newInterval,oldInterval):
    if oldInterval['priceDifference']==0:
        return 0
    else:
        if (newInterval['priceDifference']/oldInterval['priceDifference'])>0:
            return 1
        else: 
            return -1

    
def findStates(timeDiff,newInterval,oldInterval):
    #print(newInterval,oldInterval)
    minutes=timeDiff/60000
    svNames,svIntervals=state_variables()
    newStates={}
    for key in svIntervals.keys():
        split=key.split('|')
        segment=split[0]
        if svIntervals[key][0]<=minutes<svIntervals[key][1]:
            if segment=='pm':
                value=price_movement(newInterval,oldInterval)
                newStates[key]=value
            elif segment=='vl':
                value=volume_movement(newInterval,oldInterval)
                newStates[key]=value
            elif segment=='pr':
                value=parity(newInterval,oldInterval)
                newStates[key]=value
    return newStates



def compileVolBins(numBins,ticker,year,month,day):
    intervals=read_intervals(ticker,year,month,day)
    volChanges=[]
    for i in range(len(intervals)):
        interval=intervals[i]
        volChanges.append(interval['volumeDifference'])
    volChanges=remove_outliers(volChanges)
    volRange=max(volChanges)-min(volChanges)
    volBins=[]
    for i in range(numBins):
        nextBin=((i+1)*float(1/numBins))**2*volRange
        volBins.append(nextBin)
    return volBins

def compilePmBins():
    pmBins=[-100,-60,-40,-25,-10,-8,-6,-4,-3,-2.5,-2,-1.6,-1.3,-1,-.8,-.6,-.5, -.4, -.3, -.2,-.1,-.05,0,.05,.1,.2,.3,.4, .5, .6, .8,1, 1.3,1.6, 2,2.5,3,4,6,8, 10,20,40,70,100]
    reducedBins=[]
    for eachBin in pmBins:
        reducedBins.append(float(eachBin/100))
    return reducedBins

def readDayStates(ticker,year,month,day):
    intervals=read_intervals(ticker,year,month,day)
    svNames,svIntervals=state_variables()
    states=[]
    for i in range(len(intervals)):
        timeStates=[]
        #print('I',intervals[i])
        dt=datetime.fromtimestamp(intervals[i]['time']/1000)
        wkd=dt.weekday()
        hr=dt.hour
        for j in range(i):
            #print('J',intervals[j])
            state={}
            for key in intervals[i].keys():
                state[key]=intervals[i][key]
            timeDiff=intervals[i]['time']-intervals[j]['time']
            #print(timeDiff)
            newStates=findStates(timeDiff,intervals[i],intervals[j])
            newStates['wkd']=wkd
            newStates['hr']=hr
            for key in newStates.keys(): 
                state[key]=newStates[key]
            for key in svIntervals.keys():
                if key not in state.keys():
                    state[key]=None
            timeStates.append(state)
        states.append(timeStates)
    return states

def compileStates(ticker,year,month,day):
    print('Compiling',ticker)
    states=readDayStates(ticker,year,month,day)
    compiledStates=[]
    intervals=read_intervals(ticker,year,month,day)
    for i in range(len(states)):
        dt=datetime.fromtimestamp(intervals[i]['time']/1000)
        wkd=dt.weekday()
        hr=dt.hour
        pmBins=compilePmBins()
        volBins=compileVolBins(len(pmBins),ticker,year,month,day)
        prBins=[-1,0,1]
        compiledState={}
        for key in intervals[i].keys():
            compiledState[key]=intervals[i][key]                        
        compiledState['wkd']=wkd
        compiledState['hr']=hr
        keys=['pm|1', 'pm|2', 'pm|5', 'pm|10', 'pm|15', 'pm|30', 'pm|45', 'pm|60', 'pm|90', 'pm|120', 'pm|180', 'pm|240', 'pm|300', 'vl|5', 'vl|10', 'vl|30', 'vl|60', 'vl|120', 'vl|240', 'pr|1', 'pr|2', 'pr|5', 'pr|10', 'pr|15', 'pr|30', 'pr|45', 'pr|60', 'pr|90', 'pr|120', 'pr|180', 'pr|240', 'pr|300']
        for key in keys:
            split=key.split('|')
            segment=split[0]
            compiledState[key]={}
            if segment=='pm':
                for eachBin in pmBins:
                    compiledState[key][eachBin]=0
            elif segment=='vl':
                for eachBin in volBins:
                    compiledState[key][eachBin]=0
            elif segment=='pr':
                for eachBin in prBins:
                    compiledState[key][eachBin]=0
        for state in states[i]:
            for key in keys:
                if state[key]!=None:
                    split=key.split('|')
                    segment=split[0]
                    if segment=='pm':  
                        for k in range(len(pmBins)):
                            if k==len(pmBins)-1:
                                if pmBins[k]<state[key]:
                                    compiledState[key][pmBins[k]]+=1
                            else:
                                if pmBins[k]<state[key]<=pmBins[k+1]:
                                    compiledState[key][pmBins[k]]+=1
                    elif segment=='vl':  
                        for k in range(len(volBins)):
                            if k==0:
                                if volBins[k]>state[key]:
                                    compiledState[key][volBins[k]]+=1
                            else:
                                if volBins[k-1]<state[key]<=volBins[k]:
                                    compiledState[key][volBins[k]]+=1
                    elif segment=='pr':
                        for k in range(len(prBins)):
                            if prBins[k]==state[key]:
                                compiledState[key][prBins[k]]+=1
        compiledStates.append(compiledState)
    return compiledStates 


def writeStates(ticker,year,month,day):
    states=compileStates(ticker,year,month,day)
    filepath=assemble_dir(ticker,year,month,day)+'/states.csv'
    statesFile=open(filepath,'w')
    svNames,svIntervals=state_variables()
    print('Writing',ticker)
    write_compiled_states(states,ticker,year,month,day)
    statesFile.close()
    

    
for ticker in portfolio:
    year,month,day='2017','12','21'
    write_day_intervals(ticker,year,month,day)
    writeStates(ticker,year,month,day)
    day='22'
    write_day_intervals(ticker,year,month,day)
    writeStates(ticker,year,month,day)


finishTime=datetime.now()
runTime=finishTime-startTime

print('Total Runtime:',runTime)    
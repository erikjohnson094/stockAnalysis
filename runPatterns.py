from utilities import read_compiled_states
from utilities import assemble_dir
from utilities import read_pattern_traits
from utilities import write_compiled_patterns
from datetime import datetime
startTime=datetime.now()
portfolio=['AAPL','ADI','ALB','AMD','AMZN','ANF','ATVI','BABA','BHGE','EA','EGHT','FMC','GE','GGP','GILD','GM','GME',
           'GOOG','HAL','HD','HON','INTC','JCP','LIT','M','MDT','MSFT','NFLX','NVDA','QCOM','RIOT','RNG','SHLD','SHOP',
           'SLB','SNE','SQ','SQM','STMP','SYF','TAL','TGT','TJX','TSLA','TWX','TXN','UA','UTX','VNQ','XNET','AEP','BDX','CB','EIX',
           'GLW','INTU','MMM','NSC','PX','SHW','SNX','TXN','XEL','IYW']
days=['18','19','20','21','22']
if __name__ == "__main__":
    for ticker in portfolio:
        for day in days:
            year,month='2017','12'
            filepath=assemble_dir(ticker,year,month,day)+'/compiledStates.txt'
            fileObject=open(filepath,'r')
            states=read_compiled_states(fileObject)
            fileObject.close()
            patterns=read_pattern_traits(ticker)
            compiledPatterns=[]
            patternsAnalyzed=0
            for pattern in patterns:
                compiledPattern={}
                for key in pattern.keys():
                    compiledPattern[key]={}
                    for eachValue in pattern[key]:
                        compiledPattern[key][eachValue]={'weightedVelocity':0.0,'totalWeight':0.0,'totalCount':0}
                compiledPatterns.append(compiledPattern)
                for state in states:
                    stateVelocity=state['velocity']
                    for key in pattern.keys():
                        if key=='wkd' or key=='hr':
                            stateValue=float(state[key])
                            binWeight=1
                            compiledPattern[key][stateValue]['totalWeight']+=binWeight
                            compiledPattern[key][stateValue]['weightedVelocity']+=binWeight*stateVelocity
                            compiledPattern[key][stateValue]['totalCount']+=1
                        else:
                            patternBins=list(compiledPattern[key].keys())
                            stateBins=list(state[key].keys())
                            totalWeights=0
                            for eachBin in stateBins:
                                binWeight=state[key][eachBin]
                                totalWeights+=binWeight
                            if 1.1>totalWeights>0.9:
                                for i in range(len(stateBins)):
                                    eachBin=stateBins[i]
                                    binWeight=state[key][eachBin]
                                    thisBin=False
                                    for j in range(len(patternBins)):
                                        if j==len(patternBins)-1:
                                            if eachBin>=patternBins[j]:
                                                thisBin=patternBins[j]
                                        else:
                                            if patternBins[j]<=eachBin<patternBins[j+1]:
                                                thisBin=patternBins[j]
                                    if thisBin:
                                        if binWeight>0:
                                            compiledPattern[key][thisBin]['totalWeight']+=binWeight
                                            compiledPattern[key][thisBin]['weightedVelocity']+=binWeight*stateVelocity
                                            compiledPattern[key][thisBin]['totalCount']+=1
                patternsAnalyzed+=1
                currentTime=datetime.now()
                runTime=currentTime-startTime
                if patternsAnalyzed%100==0:
                    print('Analyzing',ticker,'on',year,month,day,'patterns analyzed:',patternsAnalyzed)
                    print('Runtime:',runTime)
            filepath=assemble_dir(ticker,year,month,day)+'/compiledPatterns.txt'
            fileObject=open(filepath,'w')
            write_compiled_patterns(compiledPatterns,fileObject)
            fileObject.close()
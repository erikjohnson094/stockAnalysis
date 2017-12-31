from utilities import read_compiled_patterns
from utilities import assemble_dir
from datetime import datetime
startTime=datetime.now()

portfolio=['AAPL']
days=['18','19','20','21','22']
year,month='2017','12'
def compile_patterns(ticker,year,month,days):
    ticker_patterns={}
    for day in days:
        usedKeys=[]
        filepath=assemble_dir(ticker,year,month,day)+'/compiledPatterns.txt'
        fileObject=open(filepath,'r')
        patterns=read_compiled_patterns(fileObject)
        fileObject.close()
        for pattern in patterns:
            storedKeys=list(ticker_patterns.keys())
            keyList=list(pattern.keys())
            keyList=sorted(keyList)
            if len(keyList)==1:
                primaryKey=keyList[0]
            else:
                primaryKey=keyList[0]
                for i in range(len(keyList)-1):
                    primaryKey=primaryKey+'^'+keyList[i+1]
            if primaryKey not in usedKeys:
                if primaryKey not in storedKeys:
                    ticker_patterns[primaryKey]=pattern
                else:
                    for key in pattern.keys():
                        for value in pattern[key].keys():
                            for element in pattern[key][value].keys():
                                ticker_patterns[primaryKey][key][value][element]+=pattern[key][value][element]
            usedKeys.append(primaryKey)
    return ticker_patterns



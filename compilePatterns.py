from utilities import read_compiled_patterns
from utilities import assemble_dir
from datetime import datetime
startTime=datetime.now()


def compile_patterns(ticker,dayMonthYears):
    ticker_patterns={}
    for dayMonthYear in dayMonthYears:
        day,month,year=dayMonthYear
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

def compile_these_patterns(ticker,fileObject):
    ticker_patterns={}
    usedKeys=[]
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

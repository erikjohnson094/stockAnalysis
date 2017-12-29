from utilities import read_compiled_patterns
from utilities import assemble_dir
from datetime import datetime
startTime=datetime.now()

portfolio=['AAPL']
days=['22']
year,month='2017','12'
for ticker in portfolio:
    for day in days:
        filepath=assemble_dir(ticker,year,month,day)+'/compiledPatterns.txt'
        fileObject=open(filepath,'r')
        patterns=read_compiled_patterns(fileObject)
        for pattern in patterns:
            print(pattern)
        fileObject.close()
        
runTime=datetime.now()-startTime
print('Runtime:',runTime)
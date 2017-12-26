from utilities import read_compiled_states
from utilities import assemble_dir

'''
correlations=[
    ['pm|60','pm|90','vl|60','wkd','hr'],
    ['wkd','hr','pm|60'],
    ['pm|60','pm|90','vl|60'],
    ['pm|60','pr|60','vl|60'],
    ['pm|5','pm|15','pm|45s','pm|60'],
    ['pm|60','pr|60','vl|60'],
    [],
    [],
    [],
    [],
    [],
    
]'''

weightBrackets=[]
for i in range(10):
    weightBrackets.append((i+1)*.1)

base={'price':0 ,'time':0 ,'volume':0 ,'priceDifference':0 ,'volumeDifference':0 , 'timeInterval':0 ,'wkd':0 ,'hr':0 ,'pm|1':0 , 'pm|2':0 , 'pm|5':0 , 'pm|10':0 , 'pm|15':0 , 'pm|30':0 , 'pm|45':0 , 'pm|60':0 , 'pm|90':0 , 'pm|120':0 , 'pm|180':0 , 'pm|240':0 , 'pm|300':0 , 'vl|5':0 , 'vl|10':0 , 'vl|30':0 , 'vl|60':0 , 'vl|120':0 , 'vl|240':0 , 'pr|1':0 , 'pr|2':0 , 'pr|5':0 , 'pr|10':0 , 'pr|15':0 , 'pr|30':0 , 'pr|45':0 , 'pr|60':0 , 'pr|90':0 , 'pr|120':0 , 'pr|180':0 , 'pr|240':0 , 'pr|300':0 }


portfolio=['AAPL']
if __name__ == "__main__":
    for ticker in portfolio:
        days=['22']
        for day in days:
            year,month='2017','12'
            filepath=assemble_dir(ticker,year,month,day)+'/compiledStates.txt'
            fileObject=open(filepath,'r')
            states=read_compiled_states(fileObject)
            #patterns=read_patterns(ticker)
            patterns=[{'keys':['pm|45']}]
            for state in states:
                for pattern in patterns:
                    for key in pattern.keys():
                        totalWeights=0

                        stateBins=list(state[key].keys())
                        for eachBin in stateBins:
                            totalWeights+=state[key][eachBin]
                        if totalWeights>0.1:
                        


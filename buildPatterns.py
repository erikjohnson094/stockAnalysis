from utilities import get_quote
from utilities import parse_str_from_dict
from states import compilePmBins

weightBrackets=[]
for i in range(10):
    weightBrackets.append((i+1)*.1)

patternBases=['wkd','hr','pm|1', 'pm|2', 'pm|5', 'pm|10', 'pm|15', 'pm|30', 'pm|45', 'pm|60', 'pm|90', 'pm|120', 'pm|180', 'pm|240', 'pm|300', 'vl|5', 'vl|10', 'vl|30', 'vl|60', 'vl|120', 'vl|240', 'pr|1', 'pr|2', 'pr|5', 'pr|10', 'pr|15', 'pr|30', 'pr|45', 'pr|60', 'pr|90', 'pr|120', 'pr|180', 'pr|240', 'pr|300']



portfolio=['AAPL','ADI','ALB','AMD','AMZN','ANF','ATVI','BABA','BHGE','EA','EGHT','FMC','GE','GGP','GILD','GM','GME',
           'GOOG','HAL','HD','HON','INTC','JCP','LIT','M','MDT','MSFT','NFLX','NVDA','QCOM','RIOT','RNG','SHLD','SHOP',
           'SLB','SNE','SQ','SQM','STMP','SYF','TAL','TGT','TJX','TSLA','TWX','TXN','UA','UTX','VNQ','XNET','AEP','BDX','CB','EIX',
           'GLW','INTU','MMM','NSC','PX','SHW','SNX','TXN','XEL','IYW']

pmBins=compilePmBins()
prBins=[-1,0,1]
volBinModifiers=[.000001,.000002,.000004,.000007,.00001,.00002,.00004,.00007,.0001,.0002,.0004,.0007,.001,.002,.004,.007,.01,.02,.04,.07,.1,.2,.4,.7,1]
volBins=[]
for ticker in portfolio:
    filepath='Stocks/'+ticker+'/patternTraits.txt'
    fileObject=open(filepath,'w')
    quote=get_quote(ticker)
    for volMod in volBinModifiers:
        volume=int(quote['avgTotalVolume'])
        volBin=volume*volMod
        volBins.append(volBin)
    for i in range(len(patternBases)):
        for j in range(len(patternBases)):
            patternTraits={}
            patternKeys=[patternBases[i],patternBases[j]]
            for key in patternKeys:
                splitkey=key.split('|')
                keyBins=[]
                if splitkey[0]=='wkd':
                    patternTraits[key]=[0,1,2,3,4,5,6]
                elif splitkey[0]=='hr':
                    patternTraits[key]=[6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
                elif splitkey[0]=='pm':
                    patternTraits[key]=pmBins
                elif splitkey[0]=='pr':
                    patternTraits[key]=prBins
                elif splitkey[0]=='vl':
                    patternTraits[key]=volBins
            patternString=parse_str_from_dict(patternTraits)
            fileObject.write(patternString+'\n')    
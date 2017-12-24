from utilities import write_latest_snapshot
import signal
from datetime import datetime
import random
import time
from utilities import get_quote
def signal_handler(signal, frame):
    global interrupted
    interrupted = True
startTime=datetime.now()
signal.signal(signal.SIGINT, signal_handler)

count=0

def updateTest():
    testQuote=get_quote('AAPL')
    source=testQuote['latestSource']
    print('Market Source:',source)
    if source=="IEX real time price":
        marketOpen=True
    else:
        marketOpen=False
    return source,marketOpen

def run_snapshots(tickers):
    for ticker in tickers: 
        write_latest_snapshot(ticker)
        print('Writing ticker '+ticker)
    return True

complete=[]

portfolio=['AAPL','ADI','ALB','AMD','AMZN','ANF','ATVI','BABA','BHGE','EA','EGHT','FMC','GE','GGP','GILD','GM','GME',
           'GOOG','HAL','HD','HON','INTC','JCP','LIT','M','MDT','MSFT','NFLX','NVDA','QCOM','RIOT','RNG','SHLD','SHOP',
           'SLB','SNE','SQ','SQM','STMP','SYF','TAL','TGT','TJX','TSLA','TWX','TXN','UA','UTX','VNQ','XNET','AEP','BDX','CB','EIX',
           'GLW','INTU','MMM','NSC','PX','SHW','SNX','TXN','XEL','IYW']

portfolioWeights={'AAPL':1,'ADI':1,'ALB':1,'AMD':1,'AMZN':2,'ANF':1,'ATVI':2,'BABA':4,'BHGE':1,'EA':1,'EGHT':1,'FMC':1,
                  'GE':4,'GGP':1,'GILD':1,'GM':5,'GME':1,'GOOG':2,'HAL':1,'HD':5,'HON':1,'INTC':1,'JCP':1,'LIT':2,'M':1,'MDT':1,
                  'MSFT':1,'NFLX':1,'NVDA':1,'QCOM':1,'RIOT':5,'RNG':1,'SHLD':1,'SHOP':1,'SLB':1,'SNE':1,'SQ':1,'SQM':1,'STMP':1,
                  'SYF':1,'TAL':5,'TGT':1,'TJX':1,'TSLA':1,'TWX':1,'TXN':5,'UA':1,'UTX':1,'VNQ':1,'XNET':1,'AEP':1,'BDX':1,'CB':1,
                  'EIX':1,'GLW':1,'INTU':1,'MMM':1,'NSC':1,'PX':1,'SHW':1,'SNX':1,'XEL':1,'IYW':1}


tickers=[]
for ticker in portfolioWeights.keys():
    for i in range(portfolioWeights[ticker]):
        tickers.append(ticker)
random.shuffle(tickers)
interrupted = False

while True:
    source,marketOpen=updateTest()
    if marketOpen:
        run_snapshots(tickers)
        count+=(len(tickers))
        if interrupted:
            break
    else:
        run_snapshots(tickers)
        count+=(len(tickers))
        if interrupted:
            break
        time.sleep(60)
    
        
finishTime=datetime.now()
runTime=finishTime-startTime
print('Total Queries:',count)
print('Total Runtime:',runTime)
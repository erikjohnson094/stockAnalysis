from intervals import write_day_intervals
from datetime import datetime
from utilities import get_quote
from runSnapshots import run_snapshots
from runSnapshots import updateTest
import time


startTime=datetime.now()
portfolio=['AAPL','ADI','ALB','AMD','AMZN','ANF','ATVI','BABA','BHGE','EA','EGHT','FMC','GE','GGP','GILD','GM','GME',
           'GOOG','HAL','HD','HON','INTC','JCP','LIT','M','MDT','MSFT','NFLX','NVDA','QCOM','RIOT','RNG','SHLD','SHOP',
           'SLB','SNE','SQ','SQM','STMP','SYF','TAL','TGT','TJX','TSLA','TWX','TXN','UA','UTX','VNQ','XNET','AEP','BDX','CB','EIX',
           'GLW','INTU','MMM','NSC','PX','SHW','SNX','TXN','XEL','IYW']


ignores=[]

("IEX real time price", "15 minute delayed price", "Close" or "Previous close")


testQuote=get_quote('AAPL')
source=testQuote['latestSource']
if source=="Close" or source == "Previous close":
    marketOpen=False
elif source == "IEX real time price" or "15 minute delayed price":
    marketOpen=True

if marketOpen:
    print('open')
    while marketOpen:
        source,marketOpen=updateTest()
        count=run_snapshots(count,portfolio,ignores)
else:
    print('not open')
    while not marketOpen:
        source,marketOpen=updateTest()
        count=run_snapshots(count,portfolio,ignores)
        time.sleep(45)
    if marketOpen:
        while marketOpen:
            source,marketOpen=updateTest()
            count=run_snapshots(count,portfolio,ignores)
    
#scrape snapshots and delete the latest rows that share a utc    
    
finishTime=datetime.now()
runTime=finishTime-startTime
print('Total Queries:',count)
print('Total Runtime:',runTime)
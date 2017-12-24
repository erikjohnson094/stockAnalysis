from datetime import datetime
from intervals import write_day_intervals

startTime=datetime.now()

portfolio=['AAPL','ADI','ALB','AMD','AMZN','ANF','ATVI','BABA','BHGE','EA','EGHT','FMC','GE','GGP','GILD','GM','GME',
           'GOOG','HAL','HD','HON','INTC','JCP','LIT','M','MDT','MSFT','NFLX','NVDA','QCOM','RIOT','RNG','SHLD','SHOP',
           'SLB','SNE','SQ','SQM','STMP','SYF','TAL','TGT','TJX','TSLA','TWX','TXN','UA','UTX','VNQ','XNET','AEP','BDX','CB','EIX',
           'GLW','INTU','MMM','NSC','PX','SHW','SNX','TXN','XEL','IYW']

nowTime=datetime.now()
year=nowTime.year
month=nowTime.month
#day=nowTime.day

days=[18,19,20,21,22]
count=0

for ticker in portfolio:
    print('Compiling intervals for',ticker)
    for day in days:
        count+=1
        write_day_intervals(ticker,year,month,str(day))

        
finishTime=datetime.now()
runTime=finishTime-startTime
print('Compiled intervals for',count,'tickers.')
print('Total Runtime:',runTime)
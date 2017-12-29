from utilities import assemble_dir
from shutil import copyfile
from datetime import datetime
import os


portfolio=['AAPL','ADI','ALB','AMD','AMZN','ANF','ATVI','BABA','BHGE','EA','EGHT','FMC','GE','GGP','GILD','GM','GME',
           'GOOG','HAL','HD','HON','INTC','JCP','LIT','M','MDT','MSFT','NFLX','NVDA','QCOM','RIOT','RNG','SHLD','SHOP',
           'SLB','SNE','SQ','SQM','STMP','SYF','TAL','TGT','TJX','TSLA','TWX','TXN','UA','UTX','VNQ','XNET','AEP','BDX','CB','EIX',
           'GLW','INTU','MMM','NSC','PX','SHW','SNX','TXN','XEL','IYW']


nowTime=datetime.now()
year=nowTime.year
month=nowTime.month
#day=nowTime.day

days=[26]

for ticker in portfolio:
    for day in days:
        day=str(day)
        directory=assemble_dir(ticker,year,month,day)
        destination=directory+'/snapshotData.csv'
        if not os.path.exists(directory):
            os.makedirs(directory)
        newSnapshots='New'+destination
        copyfile(newSnapshots, destination)
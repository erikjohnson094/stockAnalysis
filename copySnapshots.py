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

dayMonthYears=[(27,12,2017),
               (28,12,2017),
               (29,12,2017),
               (2,1,2018),
               (3,1,2018),
               (5,1,2018)]

for dayMonthYear in dayMonthYears:
    for ticker in portfolio:
        day,month,year=dayMonthYear
        directory=assemble_dir(ticker,year,month,day)
        destination=directory+'/snapshotData.csv'
        if not os.path.exists(directory):
            os.makedirs(directory)
        newSnapshots='New'+destination
        copyfile(newSnapshots, destination)
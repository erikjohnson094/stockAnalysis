from utilities import read_snapshots
from utilities import assemble_dir
from utilities import write_intervals
from utilities import read_day_intervals

def compile_intervals(ticker,year,month,day):
    snapshots=read_snapshots(ticker,year,month,day)
    latestSnapshot=None
    intervals=[]
    for snapshot in snapshots:
        if not latestSnapshot==None:
            timeInterval=snapshot['time']-latestSnapshot['time']
            if timeInterval>0:
                priceDifference=snapshot['price']-latestSnapshot['price']
                volumeDifference=snapshot['volume']-latestSnapshot['volume']
                if not( (priceDifference!=0) and (volumeDifference==0)):
                    interval={'price':snapshot['price'], 'time':snapshot['time'], 'volume':snapshot['volume'], 'priceDifference':priceDifference, 'volumeDifference':volumeDifference, 'timeInterval':timeInterval}
                    intervals.append(interval)
        latestSnapshot=snapshot
    return intervals
        
def write_day_intervals(ticker,year,month,day):
    filepath=assemble_dir(ticker,year,month,day)+'/intervalData.csv'
    fileObject=open(filepath,'w')
    intervals=compile_intervals(ticker,year,month,day)
    write_intervals(fileObject,intervals)
    fileObject.close()
    return True
    
def read_intervals(ticker,year,month,day):
    filepath=assemble_dir(ticker,year,month,day)+'/intervalData.csv'
    fileObject=open(filepath,'r')
    intervals=read_day_intervals(fileObject)
    fileObject.close()
    return intervals

    

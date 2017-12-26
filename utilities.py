import urllib.request
from urllib.error import URLError
import time
import os
import numpy as np
from datetime import datetime 
def small_string(Float):
    if len(str(Float))>4:
        return ('%.4g' % Float)
    else:
        return str(Float)
def med_string(Float):
    if len(str(Float))>6:
        return ('%.6g' % Float)
    else:
        return str(Float)
def assemble_dir(ticker,year,month,day):
    return 'Stocks/'+ticker+'/'+str(year)+'/'+str(month)+'/'+str(day)

def parse_dict_from_str(dictStr,dictObj):
    if dictStr[0]=='{' and dictStr[-1]=='}':
        args=dictStr.replace('{','')
        args=args.replace('}','').split(',"')
        for arg in args:
            arg=arg.split(':')
            key=arg[0].replace('"','')
            value=arg[1].replace('"','')
            dictObj[key]=value
        return dictObj
    else:
        raise KeyError('Bad dict string supplied.')
def parse_str_from_dict(dictObj):
    string='{'
    keyList=list(dictObj.keys())
    for i in range(len(dictObj.keys())):
        key=keyList[i]
        string+=str(key)+':'
        if type(dictObj[key])==list:
            string+='['
            for obj in dictObj[key]:
                string+=small_string(obj)+','
            string+=']'
        else:
            string+=small_string(dictObj[key])
        if i != len(keyList)-1:
            string+=','
    string+='}'        
    return string
def parse_interval_from_str(string):
    string=string.replace('\n','')
    splitString=string.split(',')
    price=float(splitString[0])
    volume=int(splitString[1])
    time=int(splitString[2])
    priceDifference=float(splitString[3])
    volumeDifference=int(splitString[4])
    timeInterval=int(splitString[5])
    return {'price':price,'volume':volume,'time':time,'priceDifference':priceDifference,'volumeDifference':volumeDifference,
            'timeInterval':timeInterval}
def parse_snapshot_from_str(string):
    string=string.replace('\n','')
    splitString=string.split(',')
    price=float(splitString[0])
    volume=int(splitString[1])
    time=int(splitString[2])
    return {'price':price,'volume':volume,'time':time}

def write_list(fileObject,listToWrite):
    '''
    Parses a python list and appends it to the write file as a newline in csv format
    filepath must be open file
    '''
    for i in range(len(listToWrite)):
        if i==len(listToWrite)-1:
            fileObject.write(str(listToWrite[i]))
        else:
            fileObject.write(str(listToWrite[i])+',')
    fileObject.write('\n')

def write_snapshot(fileObject,snapshotToWrite):
    # price, volume, time
    # float int time
    fileObject.write(snapshotToWrite['price']+',')
    fileObject.write(snapshotToWrite['volume']+',')
    fileObject.write(snapshotToWrite['time'])
    fileObject.write('\n')
def write_interval(fileObject,intervalToWrite):
    # price, volume, time
    # float int time
    fileObject.write(str(intervalToWrite['price'])+',')
    fileObject.write(str(intervalToWrite['volume'])+',')
    fileObject.write(str(intervalToWrite['time'])+',')
    fileObject.write(str(intervalToWrite['priceDifference'])+',')
    fileObject.write(str(intervalToWrite['volumeDifference'])+',')
    fileObject.write(str(intervalToWrite['timeInterval']))
    fileObject.write('\n')
    
def write_intervals(fileObject,intervals):
    for interval in intervals:
        write_interval(fileObject,interval)
    
def read_day_intervals(fileObject):
    intervals=[]
    for line in fileObject.readlines():
        intervalString=line
        intervals.append(parse_interval_from_str(intervalString))
    return intervals
def read_snapshots(ticker,year,month,day):
    snapshots=[]
    directory=assemble_dir(ticker,year,month,day)
    filepath=directory+'/snapshotData.csv'
    fileObject=open(filepath,'r')
    for line in fileObject.readlines():
        snapshotString=line
        snapshots.append(parse_snapshot_from_str(snapshotString))
    fileObject.close()
    return snapshots
    
def api_get(endpoint):
    preURL='https://api.iextrading.com/1.0'
    try:
        response=urllib.request.urlopen(preURL+endpoint).read()
    except URLError:
        time.sleep(60)
        response=urllib.request.urlopen(preURL+endpoint).read()
    decoded=response.decode('utf-8')
    return decoded    

def get_quote_string(ticker):
    quoteURL='/stock/'+ticker+'/quote'
    quote=api_get(quoteURL)
    return quote

def get_quote(ticker):
    quote={}
    quoteStr=get_quote_string(ticker)
    fullQuote=parse_dict_from_str(quoteStr,quote)
    return fullQuote

def get_snapshot(ticker):
    quote=get_quote(ticker)
    snapshot={}
    snapshot['price']=quote['latestPrice']
    snapshot['volume']=quote['latestVolume']
    snapshot['time']=quote['latestUpdate']
    return snapshot,quote

def get_snapshot_date(snapshot):
    date=datetime.fromtimestamp(int(snapshot['time'])/1000)
    year=date.year
    month=date.month
    day=date.day
    return year,month,day
def get_date(utcMills):
    date=datetime.fromtimestamp(utcMills/1000)
    year=date.year
    month=date.month
    day=date.day
    return year,month,day

def write_latest_snapshot(ticker):
    snapshot,quote=get_snapshot(ticker)
    year,month,day=get_snapshot_date(snapshot)
    directory=assemble_dir(quote['symbol'],year,month,day)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath=directory+'/snapshotData.csv'
    fileObject=open(filepath,'a')
    write_snapshot(fileObject,snapshot)
    fileObject.close()
    return ticker+' captured at '+snapshot['time']

def remove_outliers(listToClean):
    cleanList=[]
    median=np.median(listToClean)
    stdev=np.std(listToClean)
    for element in listToClean:
        diff=abs(element-median)
        if diff<(4*stdev):
            cleanList.append(element)
    return cleanList
def write_compiled_state(fileObject,state):
    keys=['pm|1', 'pm|2', 'pm|5', 'pm|10', 'pm|15', 'pm|30', 'pm|45', 'pm|60', 'pm|90', 'pm|120', 'pm|180', 'pm|240', 'pm|300', 'vl|5', 'vl|10', 'vl|30', 'vl|60', 'vl|120', 'vl|240', 'pr|1', 'pr|2', 'pr|5', 'pr|10', 'pr|15', 'pr|30', 'pr|45', 'pr|60', 'pr|90', 'pr|120', 'pr|180', 'pr|240', 'pr|300']
    for element in ['price','time','volume','priceDifference','volumeDifference', 'timeInterval','wkd']:
        fileObject.write(str(state[element])+'|')
    fileObject.write(str(state['hr']))
    for key in keys:
        fileObject.write('^'+key)
        keyCounts=[]
        totalCounts=0
        dictKeys=list(state[key].keys())
        for eachBin in dictKeys:
            keyCount=state[key][eachBin]
            keyCounts.append(keyCount)
            totalCounts+=keyCount
        for i in range(len(dictKeys)):  
            if totalCounts==0:
                fileObject.write('$'+small_string(dictKeys[i])+'|'+'0')
            else:    
                fileObject.write('$'+small_string(dictKeys[i])+'|'+small_string(float(keyCounts[i]/totalCounts)))
    fileObject.write('\n')
    return True
def write_compiled_states(states,ticker,year,month,day):
    directory=assemble_dir(ticker,year,month,day)
    filepath=directory+'/compiledStates.txt'
    fileObject=open(filepath,'w')
    for state in states:
        write_compiled_state(fileObject,state)
    fileObject.close()
    

def read_compiled_states(fileObject):
    singleElementNames=['price','time','volume','priceDifference','volumeDifference', 'timeInterval','wkd','hr']
    multipleElementNames=['pm|1', 'pm|2', 'pm|5', 'pm|10', 'pm|15', 'pm|30', 'pm|45', 'pm|60', 'pm|90', 'pm|120', 'pm|180', 'pm|240', 'pm|300', 'vl|5', 'vl|10', 'vl|30', 'vl|60', 'vl|120', 'vl|240', 'pr|1', 'pr|2', 'pr|5', 'pr|10', 'pr|15', 'pr|30', 'pr|45', 'pr|60', 'pr|90', 'pr|120', 'pr|180', 'pr|240', 'pr|300']
    states=[]
    lines=fileObject.readlines()
    for i in range(len(lines)):
        state={}
        line=lines[i]
        line=line.split('^')
        singleElements=line[0].split('|')
        for j in range(len(singleElements)):
            state[singleElementNames[j]]=float(singleElements[j])
        multipleElements=line[1:]
        for k in range(len(multipleElements)):
            element=multipleElements[k].split('$')
            name=multipleElementNames[k]
            if element[0]!=name:
                raise KeyError('Read/Write mismatch in compiled states.',element[0],name)
            state[name]={}    
            for l in range(len(element)):
                if l>0:
                    thisBin=element[l].split('|')
                    value=float(thisBin[0])
                    total=float(thisBin[1])
                    state[name][value]=total
        state['velocity']=float(state['priceDifference']/state['timeInterval'])
        states.append(state)
    return states


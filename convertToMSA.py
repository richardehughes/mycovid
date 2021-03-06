import csv
import xlrd 
from collections import defaultdict
from functools import partial
from itertools import repeat
def nested_defaultdict(default_factory, depth=1):
    result = partial(defaultdict, default_factory)
    for _ in repeat(None, depth - 1):
        result = partial(defaultdict, result)
    return result()


import datetime
import numpy as np
def running_mean(x, N):
	cumsum = np.cumsum(np.insert(x, 0, 0)) 
	return (cumsum[N:] - cumsum[:-N]) / N

from scipy.signal import savgol_filter
def smooth(x,window_len=4,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """
    x = np.asarray(x)

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y



remap = {}
remap['31100'] = '31080'
remap['26180'] = '46520'
remap['19380'] = '19430'
remap['42060'] = '42200'
remap['14020'] = '14010'
remap['39140'] = '39150'
remap['29140'] = '29200'
remap['44600'] = '48260'


loc = ("pop_weighted_density_cbsa.xlsx") 
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
sheet.cell_value(0, 0)
print("sheet.nrows ",sheet.nrows)
#FIPS State Code        FIPS County Code
fipsToCbsa = {}
cbsaPop2010 = {}
cbsaPopWDensity = {}
for i in range(sheet.nrows):
	cbsa = sheet.cell_value(i, 0)
	if cbsa in remap:
		cbsa = remap[cbsa]
	pop2010 = sheet.cell_value(i, 3)
	density = sheet.cell_value(i, 6)
	cbsaPop2010[cbsa] = pop2010
	cbsaPopWDensity[cbsa] = density


loc = ("metro_micro_delin_Sep_2018.xls")   
#loc = ("list3.xlsx")   
wb = xlrd.open_workbook(loc) 
sheet = wb.sheet_by_index(0) 
sheet.cell_value(0, 0) 
  
print("sheet.nrows ",sheet.nrows)

#FIPS State Code	FIPS County Code
fipsToCbsa = {}
cbsaName = {}
for i in range(sheet.nrows): 
	metro_micro = sheet.cell_value(i, 4)
	if metro_micro=='Metropolitan Statistical Area':
		fipsState = sheet.cell_value(i, 9)
		fipsCounty = sheet.cell_value(i, 10)
		fips = fipsState + fipsCounty
		cbsa = sheet.cell_value(i, 0)
		fipsToCbsa[fips] = cbsa
		cbsaName[cbsa] = sheet.cell_value(i, 3)
#	print("fipsState ",fipsState,fipsCounty)
#    print(sheet.cell_value(i, 0)) 




ifn = csv.DictReader(open("../covid-19-data/us-counties.csv"))
#date,county,state,fips,cases,deaths

from collections import defaultdict
cbsaCasesByDate = nested_defaultdict(int,2)
cbsaDeathsByDate = nested_defaultdict(int,2)
cbsaDeathsTotal = defaultdict(int)
cbsaCasesTotal = defaultdict(int)

for row in ifn:
	fips = row['fips']
	county = row['county']
	state = row['state']
	cases = int(row['cases'])
	deaths = int(row['deaths'])
	date = row['date']
#	print("state ",state,cases,deaths,fips)
	if fips in fipsToCbsa:
#		print("found fips")
		cbsa = fipsToCbsa[fips]
		cbsaCasesTotal[cbsa] += cases
		cbsaDeathsTotal[cbsa] += deaths
		cbsaCasesByDate[cbsa][date] += cases
		cbsaDeathsByDate[cbsa][date] += deaths

#
# Now print out
#for cbsa in sorted(cbsaDeathsTotal,key=cbsaDeathsTotal.get,reverse=True):
writer = csv.DictWriter(open('covid_by_cbsa.csv','w'), 
    fieldnames=['CBSA','Name','TotalCases',
                'TotalDeaths','Population2010','WeightedDensity',
                'Date','Cases','Deaths'])
writer.writeheader()
for cbsa in sorted(cbsaCasesTotal,key=cbsaCasesTotal.get,reverse=True):
	print("cbsa,name ",cbsa,cbsaName[cbsa])
	if cbsa in remap:
		cbsa = remap[cbsa]
	pop2010 = 0
	density = 0
	if cbsa in cbsaPop2010:
		pop2010 = cbsaPop2010[cbsa]
		density = int(float(cbsaPopWDensity[cbsa]))
	else:
		print("*** cbsa not found ",cbsa,cbsaName[cbsa])

	print("")
	print("CBSA ",cbsa,cbsaName[cbsa],cbsaDeathsTotal[cbsa],cbsaCasesTotal[cbsa])
	for date in sorted(cbsaCasesByDate[cbsa]):
		print("   ",date,cbsaCasesByDate[cbsa][date],cbsaDeathsByDate[cbsa][date])
		writer.writerow({'CBSA':cbsa,'Name':cbsaName[cbsa],
				'TotalCases':cbsaCasesTotal[cbsa],'TotalDeaths':cbsaDeathsTotal[cbsa],
				'Population2010':pop2010,'WeightedDensity':density,'Date':date,
				'Cases':cbsaCasesByDate[cbsa][date],'Deaths':cbsaDeathsByDate[cbsa][date]})


#
# Now gather together everyone with at least 10 deaths.  Call that day0


writer2 = csv.DictWriter(open('covid_by_cbsa_samestart.csv','w'), 
    fieldnames=['CBSA','Name','TotalCases',
                'TotalDeaths','Population2010','WeightedDensity',
                'Date','Day','Cases',
                'Deaths','DeathsPerMillion',
                'deathGrowthRate',
                'deathGrowthRatePerMill','deathGrowthRatePerMillSmoothed',
                'deathsSmoothed',
                'deathsSmoothedPerMillion'])
writer2.writeheader()

minDeaths = 5
minDeathsPerMillion = 1
smoothDays = 3
for cbsa in sorted(cbsaDeathsTotal,key=cbsaDeathsTotal.get,reverse=True):
    if cbsa in remap:
        cbsa = remap[cbsa]
    pop2010 = 0
    density = 0
    if cbsa in cbsaPop2010:
        pop2010 = cbsaPop2010[cbsa]
        density = int(float(cbsaPopWDensity[cbsa]))
    else:
        print("*** cbsa not found ",cbsa,cbsaName[cbsa])
    if cbsaDeathsTotal[cbsa]>10 and cbsa in cbsaPop2010:
        sumDeaths = 0
        start_day_of_year = -100
        includeData = False
        for date in sorted(cbsaDeathsByDate[cbsa]):
            sumDeaths += cbsaDeathsByDate[cbsa][date]
#            if sumDeaths >= minDeaths:
            if 1000000.0*sumDeaths/pop2010 >= minDeathsPerMillion:
                datet = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                start_day_of_year = datet.timetuple().tm_yday
                includeData = True
                break
    #
    # If there are more than 10 deaths, keep this cbsa
        if includeData:
            deathRate = 0
            numDays = 0
            deaths = []
            deathsPerMill = []
            for date in sorted(cbsaDeathsByDate[cbsa]):
                deaths.append(cbsaDeathsByDate[cbsa][date])
                deathsPerMill.append(1000000.0*cbsaDeathsByDate[cbsa][date]/pop2010)
#            deathsAvg = running_mean(deaths,smoothDays)
#            deathsAvgPerMill = running_mean(deathsPerMill,smoothDays)
# 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
#            deathsAvg = smooth(deaths,window_len=smoothDays,window='flat')
#            deathsAvgPerMill = smooth(deathsPerMill,window_len=smoothDays,window='flat')
#
# yhat = savgol_filter(y, 51, 3)
            deathsAvg = savgol_filter(deaths,9,3)
            deathsAvgPerMill = savgol_filter(deathsPerMill,9,3)
#
# Noiw get gradients
            deathGrowthRate = np.gradient(deathsAvg)
            deathGrowthRatePerMill = np.gradient(deathsPerMill)
            deathGrowthRatePerMillSmoothed = np.gradient(deathsAvgPerMill)
            num = 0
            for date in sorted(cbsaDeathsByDate[cbsa]):
                datet = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                day_of_year = datet.timetuple().tm_yday - start_day_of_year
                print("   ",day_of_year,num,date,cbsaCasesByDate[cbsa][date],cbsaDeathsByDate[cbsa][date])
                
                writer2.writerow({'CBSA':cbsa,'Name':cbsaName[cbsa],
                    'TotalCases':cbsaCasesTotal[cbsa],'TotalDeaths':cbsaDeathsTotal[cbsa],
                    'Population2010':pop2010,'WeightedDensity':density,
                    'Date':date,'Day':day_of_year,
                    'Cases':cbsaCasesByDate[cbsa][date],
                    'Deaths':cbsaDeathsByDate[cbsa][date],
                    'DeathsPerMillion':deathsPerMill[num],
                    'deathGrowthRate':round(deathGrowthRate[num],4),
                    'deathGrowthRatePerMill':round(deathGrowthRatePerMill[num],4),
                    'deathGrowthRatePerMillSmoothed':round(deathGrowthRatePerMillSmoothed[num],4),
                    'deathsSmoothed':round(deathsAvg[num],4),
                    'deathsSmoothedPerMillion':round(deathsAvgPerMill[num],4)})
                num += 1

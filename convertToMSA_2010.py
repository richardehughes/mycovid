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
	pop2010 = sheet.cell_value(i, 3)
	density = sheet.cell_value(i, 6)
	cbsaPop2010[cbsa] = pop2010
	cbsaPopWDensity[cbsa] = density

#loc = ("metro_micro_delin_Sep_2018.xls")   
loc = ("list3.xlsx")   
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
#	fipsState = sheet.cell_value(i, 9)
#	fipsCounty = sheet.cell_value(i, 10)
		fips = sheet.cell_value(i, 10) # fipsState + fipsCounty
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
writer = csv.DictWriter(open('covid_by_cbsa.csv','w'), fieldnames=['CBSA','Name','TotalCases','TotalDeaths','Population2010','WeightedDensity','Date','Cases','Deaths'])
writer.writeheader()
for cbsa in sorted(cbsaCasesTotal,key=cbsaCasesTotal.get,reverse=True):
	pop2010 = cbsaPop2010[cbsa]
	density = int(float(cbsaPopWDensity[cbsa]))
	

	print("")
	print("CBSA ",cbsa,cbsaName[cbsa],cbsaDeathsTotal[cbsa],cbsaCasesTotal[cbsa])
	for date in sorted(cbsaCasesByDate[cbsa]):
		print("   ",date,cbsaCasesByDate[cbsa][date],cbsaDeathsByDate[cbsa][date])
		writer.writerow({'CBSA':cbsa,'Name':cbsaName[cbsa],
				'TotalCases':cbsaCasesTotal[cbsa],'TotalDeaths':cbsaDeathsTotal[cbsa],
				'Population2010':pop2010,'WeightedDensity':density,'Date':date,
				'Cases':cbsaCasesByDate[cbsa][date],'Deaths':cbsaDeathsByDate[cbsa][date]})

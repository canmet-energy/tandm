import pandas as pd
from scipy import stats

import seaborn as sns
import pandas as pd

import matplotlib.pyplot as plt 
import numpy as np 



sheetnames = [
	"All units total Elec (kWh)",
	"SD Pre-1977 Elec (kWh)",
	"SD 1978-1995 Elec (kWh)",
	"SD 1996-2012 Elec (kWh)",
	"SD 2013 and later Elec (kWh)",
	"DR Pre-1977 Elec (kWh)",
	"DR 1978-1995 Elec (kWh)",
	"DR 1996-2012 Elec (kWh)",
	"DR 2013 and later Elec (kWh)",
	"MH Pre-1977 Elec (kWh)",
	"MH 1978-1995 Elec (kWh)",
	"MH 1996-2012 Elec (kWh)",
	"MH 2013 and later Elec (kWh)",
	"MU Pre-1977 Elec (kWh)",
	"MU 1978-1995 Elec (kWh)",
	"MU 1996-2012 Elec (kWh)",
	"MU 2013 and later Elec (kWh)",
	]
	
with open('K-S electrical results.csv','w') as f:
	for sheet in sheetnames:
		#import the data
		df = pd.read_excel(r'240325 v3 CEE Map Histograms Template.xlsx', sheet_name = sheet)

		# run the test
		CEEMap = df['BC_Electrical_Energy_kWh']
		Fortis = df['Fortis_By_Unit_Elect_kWh']

		result = stats.ks_2samp(CEEMap,Fortis)
		print (sheet)
		print (result)
		#f.write(result + "\n")
		f.write(f"{sheet} {result}\n")
		#f"{item[0]},{item[1]},{item[2]}\n"

		sns.ecdfplot(pd.DataFrame({'CEEMap': CEEMap, 'Fortis': Fortis}))
		#plt.show()
		plt.savefig(sheet + "_cdf.png")
		plt.close("all")
sheetnames = [
	"All units total NG (GJ)",
	"SD Pre-1977 NG (GJ)",
	"SD 1978-1995 NG (GJ)",
	"SD 1996-2012 NG (GJ)",
	"SD 2013 and later NG (GJ)",
	"DR Pre-1977 NG (GJ)",
	"DR 1978-1995 NG (GJ)",
	"DR 1996-2012 NG (GJ)",
	"DR 2013 and later NG (GJ)",
	"MH Pre-1977 NG (GJ)",
	"MH 1978-1995 NG (GJ)",
	"MH 1996-2012 NG (GJ)",
	"MH 2013 and later NG (GJ)",
	"MU Pre-1977 NG (GJ)",
	"MU 1978-1995 NG (GJ)",
	"MU 1996-2012 NG (GJ)",
	"MU 2013 and later NG (GJ)",
	]
	
with open('K-S natural gas results.csv','w') as f:
	for sheet in sheetnames:
		#import the data
		df = pd.read_excel(r'240325 v3 CEE Map Histograms Template.xlsx', sheet_name = sheet)

		# run the test
		CEEMap = df['BC_Natural_Gas_Energy_GJ']
		Fortis = df['Fortis_By_Unit_NG_GJ']

		result = stats.ks_2samp(CEEMap,Fortis)
		print (sheet)
		print (result)
		#f.write(result + "\n")
		f.write(f"{sheet} {result}\n")
		#f"{item[0]},{item[1]},{item[2]}\n"

		sns.ecdfplot(pd.DataFrame({'CEEMap': CEEMap, 'Fortis': Fortis}))
		#plt.show()
		plt.savefig(sheet + "_cdf.png")
		plt.close("all")
		
with open('K-S total energy use results.csv','w') as f:
	#import the data
	df = pd.read_excel(r'240310-CEE Map Histograms Template.xlsx', sheet_name = 'All units total (GJ)')

	# run the test
	CEEMap = df['BC_Total_Energy_GJ']
	Fortis = df['Fortis-Total_GJ']

	result = stats.ks_2samp(CEEMap,Fortis)
	
	print ('All units total (GJ)')
	print (result)
	
	#f.write(result + "\n")
	f.write(f'All units total (GJ) {result}\n')
	#f"{item[0]},{item[1]},{item[2]}\n"

	sns.ecdfplot(pd.DataFrame({'CEEMap': CEEMap, 'Fortis': Fortis}))
	#plt.show()
	plt.savefig('All units total GJ_cdf.png')
	plt.close("all")

#KstestResult(statistic=0.2024, pvalue=5.4520491966072294e-90, statistic_location=22192.37, statistic_sign=1)

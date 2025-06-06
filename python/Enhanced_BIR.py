import os
import json

import shutil
import pandas as pd 
import click
import numpy as np

import re

'''
This script relies on input data available in a Inputs subfolder and will export results to an Outputs subfolder
A TestOutputs folder is used for staged outputs as the script progresses if the export commands are uncommented
To export staged working files, search for #For TestOutputs and uncomment the export line below or add new exports in the script

These subfolders must exist before running the script: Inputs, Outputs, TestOutputs

The following input data is required:
 - BIR-headers.txt: holds the field names of the BCAA Building Inventory Report
 - CEEI_Extract_data.txt: holds the data from the BCAA Building Inventory Report
 - ASSESSMENT_FABRIC_CENTROIDS_with_NEIGHBOURHOODS.csv: the resulting file from spatially joining the Assessment Fabric centroids with the Census Tract and Neighourhood polygons
   This csv file must include these fields: Folio (from Assessment Fabric), Neighbourhood (from Neighbourhood boundaries), CT (from Census bounaries), X (from Assessment Fabric),
   Y(from Assessment Fabric)
 - lut_ActualUseCode.csv: this file is from the TaNDM project and assigns building categories based on BCAA BIR Actual Use Code - it can be updated
 - lut_ManualClassCode.csv: this file is from the TaNDM project and refines building categories based on BCAA BIR Manual Class Code - it can be updated
 - lut_Occupancy.csv: this file is from the TaNDM project and refines building categories based on BCAA BIR Occupancy - it can be updated
 - lut_UnitOfMeasure.csv: this file is from the TaNDM project and refines building categories based on BCAA BIR Unit of Measure - it can be updated
 
 - to change the definition of vintages, search for Allocate buildings to vintages
'''


#Import BCAA files and column headers
df = pd.read_csv(r"Inputs/CEEI_Extract_Data.txt", sep='|', dtype={'0':'str','1':'str','2':'str','3':'str','4':'str','5':'str','6':'str','7':'float','8':'float','9':'str','10':'str','11':'str','12':'int','13':'int','14':'float','15':'float','16':'str','17':'str','18':'int','19':'int','20':'int','21':'int','22':'int','23':'int','24':'int','25':'int'},header = None)
headers = pd.read_csv(r"Inputs/BIR-headers.txt", sep='|', nrows=0).columns
df.columns = headers

#Note: if you are importing BIR information from a different source and/or format, the fields that are needed for this script are: Jur, Roll, TotalArea, FloorArea, FloorAreaType, StrataUnitArea, Occupancy, PrimAUC, MCC, UnitOfMeasure, BiuldingType, NosUnits. 


#add leading zeroes to the BCA Roll number
df.loc[df['Jur'] == 214, 'Roll'] = df['Roll'].astype(str).str.zfill(6)
df.loc[df['Jur'] == 217, 'Roll'] = df['Roll'].astype(str).str.zfill(8)


#Add columns to be populated and fill with generic values to be able to identify which rows were populated in the process
df['Folio'] = '0'
df['Vintage'] = 'No Vintage'
df['FloorArea'] = 0
df['FloorAreaType'] = 'No FloorAreaType Assigned'
df['Major Category'] = 'No Major Category'
df['Category'] = 'No Category'
df['Sub-category'] = 'No Sub-category'
df['BCBCOccupancyCode'] = 'No BCBCOccupancyCode'
df['Part3_Part9'] = 'No Part3_Part9'
df['Municipality'] = 'City of Kelowna'
df['RegionalDistrict'] = 'Regional District of Central Okanagan'
df['CSDName'] = 'No CSDName'
df['CSD'] = 'No CSD'
df['CT'] = 0
df['DA'] = 'No DA'
df['DB'] = 0
df['StreetAddressUnit'] = ''
df['StreetNumber'] = ''
df['StreetDirectionalPrefix'] = ''
df['StreetName'] = 'No Name'
df['StreetSuffix'] = ''
df['StreetDirectionalSuffix'] = ''
df['Neighbourhood'] = 'No Neighbourhood'
df['StreetNumberDigitOne'] = 0
df['StreetUnitMarker'] = 'No Unit'
df['StreetStringLengthCheck'] = 0
df['StreetString0Length'] = 0
df['StreetString1Length'] = 0
df['StreetString2Length'] = 0
df['StreetString3Length'] = 0
df['StreetString4Length'] = 0
df['StreetString5Length'] = 0
df['StreetString6Length'] = 0
df['StreetString7Length'] = 0
df['StreetString0'] = ''
df['StreetString1'] = ''
df['StreetString2'] = ''
df['StreetString3'] = ''
df['StreetString4'] = ''
df['StreetString5'] = ''
df['StreetString6'] = ''
df['StreetString7'] = ''
df['StreetStringNotSure'] = ''
df['RootAddress'] = ''
df['BuildingComment'] = ''
df['BuildingCommentTemp'] = ''
df['X'] = 0
df['Y'] = 0

#Define type of columns to be populated
df['Folio'].astype(str)
df['Vintage'].astype(str)
df['FloorArea'].astype(int)
df['FloorAreaType'].astype(str)
df['Major Category'].astype(str)
df['Category'].astype(str)
df['Sub-category'].astype(str)
df['BCBCOccupancyCode'].astype(str)
df['Part3_Part9'].astype(str)
df['Municipality'].astype(str)
df['RegionalDistrict'].astype(str)
df['CSDName'].astype(str)
df['CSD'].astype(str)
df['CT'].astype(int)
df['DA'].astype(str)
df['DB'].astype(int)
df['Neighbourhood'].astype(str)
df['X'].astype(float)
df['Y'].astype(float)

#Create unique Folio number for linking
df['Folio'] = df['Jur'].astype(str) + df['Roll'].astype(str)
df['Folio'] = pd.to_numeric(df['Folio'])

df.sort_values(by=['Folio'])

df_dup = df.duplicated()
df_dup.to_excel("TestOutputs/outturn_data_1_dups_identified.xlsx")
df = df.drop_duplicates()

#remove duplicate rows
df['dup_id'] = pd.factorize(df.apply(tuple, axis=1))[0] + 1
df_out = df.drop_duplicates(subset='dup_id')
df_out.to_excel("TestOutputs/outturn_dups_removed.xlsx")
df = df_out

'''
Set the stage for parsing the BCAA BIR civic address - note: if there are more than 7 words in this field, the related parts of the code will need to be updated
for full detail of the address, but do not need updating to use the Root Address part of the code which is the only part that is functionally required
'''

df['number_of_words'] = df.CivicAddress.apply(lambda x: len(x.split()))
df['number_of_words'].astype(int) 

df['StreetString0'] = df['CivicAddress'].str.split(' ').str[0]
df['StreetString1'] = df['CivicAddress'].str.split(' ').str[1]
df['StreetString2'] = df['CivicAddress'].str.split(' ').str[2]
df['StreetString3'] = df['CivicAddress'].str.split(' ').str[3]
df['StreetString4'] = df['CivicAddress'].str.split(' ').str[4]
df['StreetString5'] = df['CivicAddress'].str.split(' ').str[5]
df['StreetString6'] = df['CivicAddress'].str.split(' ').str[6]

df['StreetString0Length'] = df['StreetString0'].str.len()
df['StreetString1Length'] = df['StreetString1'].str.len()
df['StreetString2Length'] = df['StreetString2'].str.len()
df['StreetString3Length'] = df['StreetString3'].str.len()
df['StreetString4Length'] = df['StreetString4'].str.len()
df['StreetString5Length'] = df['StreetString5'].str.len()
df['StreetString6Length'] = df['StreetString6'].str.len()


df['StreetUnitMarker'] = df['CivicAddress'].str.split(' ').str[0]
df.loc[df['StreetUnitMarker'] == 'UNIT', 'StreetAddressUnit'] = df['CivicAddress'].str.split(' ').str[1]

#For 5 words
#Sort Directional suffix and standard suffix
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] == 1), 'StreetDirectionalSuffix'] = df['StreetString3']
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] > 1) & (df['StreetString3'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST','WAY'])),'StreetSuffix'] = df['StreetString3']
#Sort name
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] == 1), 'StreetName'] = df['StreetString1']
#correct for 1 being the address!
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] > 1), 'StreetName'] = df['StreetString2']
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] == 1) & (df['StreetString2'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString2']
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] == 1) & (~df['StreetString2'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE','CRES', 'CRT', 'DR', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString1'] + ' ' + df['StreetString2']
#Sort number
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] == 1), 'StreetNumber'] = df['StreetString0']
#Check number
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 5) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString3Length'] == 1), 'StreetName'] = df['StreetString0'] + " " + df['StreetString1'] 
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] > 1), 'StreetNumber'] = df['StreetString1']
#Check number
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 5) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString3Length'] > 1) & (df['StreetString1Length'] > 1), 'StreetName'] = df['StreetString1'] + " " + df['StreetString2']
df.loc[(df['number_of_words'] == 5) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString3Length'] > 1) & (df['StreetString1Length'] > 1), 'StreetNumber'] = df['StreetString0']

df.loc[(df['number_of_words'] == 5) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString3Length'] > 1) & (df['StreetString1Length'] == 1), 'StreetDirectionalPrefix'] = df['StreetString1'] 
df.loc[(df['number_of_words'] == 5) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString3Length'] > 1) & (df['StreetString1Length'] == 1), 'StreetNumber'] = df['StreetString0'] 
#Check not sure
df.loc[(df['number_of_words'] == 5) & (df['StreetString3Length'] > 1), 'StreetStringNotSure'] = df['StreetString0']

#For 6 words
#Sort Directional suffix and standard suffix
df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] == 1), 'StreetDirectionalSuffix'] = df['StreetString4']
df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] > 1) & (df['StreetString4'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString4']
#Sort name
df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] == 1), 'StreetName'] = df['StreetString2']
#correct for 1 being the address!
df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] > 1), 'StreetName'] = df['StreetString3']

df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] == 1) & (df['StreetString3'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString3']
df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] == 1) & (~df['StreetString3'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE','CRES', 'CRT', 'DR', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString1'] + ' ' + df['StreetString2']
df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] > 1) & (df['StreetUnitMarker'] == 'UNIT') & (~df['StreetString4'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE','CRES', 'CRT', 'DR', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString3'] + ' ' + df['StreetString4']
#Sort number
df.loc[(df['number_of_words'] == 6), 'StreetNumber'] = df['StreetString0']
#Check number
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 6) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString4Length'] == 1), 'StreetName'] = df['StreetString1'] + " " + df['StreetString2'] 
df.loc[(df['number_of_words'] == 6) & (df['StreetUnitMarker'] == 'UNIT'), 'StreetNumber'] = df['StreetString2']
#Check number
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 6) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString4Length'] > 1) & (df['StreetString1Length'] > 1), 'StreetName'] = df['StreetString2'] + " " + df['StreetString3']
df.loc[(df['number_of_words'] == 6) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString4Length'] > 1) & (df['StreetString2Length'] > 1), 'StreetNumber'] = df['StreetString1']
df.loc[(df['number_of_words'] == 6) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString4Length'] > 1) & (df['StreetString2Length'] == 1), 'StreetDirectionalPrefix'] = df['StreetString2'] 
df.loc[(df['number_of_words'] == 6) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString4Length'] > 1) & (df['StreetString2Length'] == 1), 'StreetNumber'] = df['StreetString1'] 
#Check not sure
df.loc[(df['number_of_words'] == 6) & (df['StreetString4Length'] > 1), 'StreetStringNotSure'] = df['StreetString1']
df['StreetUnitMarker'] = df['CivicAddress'].str.split(' ').str[0]
df.loc[df['StreetUnitMarker'] == 'UNIT', 'StreetAddressUnit'] = df['CivicAddress'].str.split(' ').str[1]

#For 7 words
#Sort Directional suffix and standard suffix
df.loc[(df['number_of_words'] == 7) & (df['StreetString5Length'] == 1), 'StreetDirectionalSuffix'] = df['StreetString5']
df.loc[(df['number_of_words'] == 7) & (df['StreetString5Length'] > 1) & (df['StreetString5'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString5']
#Sort name
df.loc[(df['number_of_words'] == 7) & (df['StreetString5Length'] == 1), 'StreetName'] = df['StreetString3']
#correct for 1 being the address!
df.loc[(df['number_of_words'] == 7) & (df['StreetString5Length'] > 1), 'StreetName'] = df['StreetString4']
df.loc[(df['number_of_words'] == 7) & (df['StreetString5Length'] == 1) & (df['StreetString4'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString4']
#Sort number
df.loc[(df['number_of_words'] == 7), 'StreetNumber'] = df['StreetString2']
#Check number
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 7) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString5Length'] == 1) & (~df['StreetString4'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE','CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString2'] + ' ' + df['StreetString3']
df.loc[(df['number_of_words'] == 7) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString5Length'] == 1), 'StreetName'] = df['StreetString2'] + " " + df['StreetString3'] 
df.loc[(df['number_of_words'] == 7) & (df['StreetString5Length'] > 1), 'StreetNumber'] = df['StreetString3']
#Check number
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 7) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString5Length'] > 1) & (df['StreetString2Length'] > 1), 'StreetName'] = df['StreetString3'] + " " + df['StreetString4']
df.loc[(df['number_of_words'] == 7) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString5Length'] > 1) & (df['StreetString3Length'] > 1), 'StreetNumber'] = df['StreetString2']
df.loc[(df['number_of_words'] == 7) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString5Length'] > 1) & (df['StreetString3Length'] == 1), 'StreetDirectionalPrefix'] = df['StreetString2'] 
df.loc[(df['number_of_words'] == 7) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString5Length'] > 1) & (df['StreetString3Length'] == 1), 'StreetNumber'] = df['StreetString1'] 
#Check not sure
df.loc[(df['number_of_words'] == 7) & (df['StreetString5Length'] > 1), 'StreetStringNotSure'] = df['StreetString2']
df['StreetUnitMarker'] = df['CivicAddress'].str.split(' ').str[0]
df.loc[df['StreetUnitMarker'] == 'UNIT', 'StreetAddressUnit'] = df['CivicAddress'].str.split(' ').str[1]

#Check short civic addresses
df.loc[df['number_of_words'] == 2, 'StreetName'] = df['StreetString0']
#Check suffix and directional suffix
df.loc[(df['number_of_words'] == 3) & (df['StreetString1Length'] == 1), 'StreetDirectionalSuffix'] = df['StreetString2']
df.loc[(df['number_of_words'] == 3) & (df['StreetString1Length'] == 1) & (df['StreetString0'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString0']
#Check number
df.loc[df['number_of_words'] == 3, 'StreetNumber'] = df['StreetString0']
df.loc[df['number_of_words'] == 3, 'StreetName'] = df['StreetString1']
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 3) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString0Length'] == 1), 'StreetDirectionalPrefix'] = df['StreetString0']
df.loc[(df['number_of_words'] == 3) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString0Length'] == 1), 'StreetName'] = df['StreetString1']
df.loc[(df['number_of_words'] == 3) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString1'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString1']
df.loc[(df['number_of_words'] == 3) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString1'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString0']
df.loc[(df['number_of_words'] == 3) & (df['StreetNumberDigitOne'].isnull()) & (~df['StreetString2'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE','CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString0'] + ' ' + df['StreetString1']
#Check suffix and directional suffix
df.loc[(df['number_of_words'] == 4) & (df['StreetString2Length'] == 1), 'StreetDirectionalSuffix'] = df['StreetString2']
df.loc[(df['number_of_words'] == 4) & (df['StreetString2Length'] == 1) & (df['StreetString1'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString1']
df.loc[(df['number_of_words'] == 4) & (df['StreetString2Length'] > 1) & (df['StreetString2'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString2']
#Check number
df.loc[df['number_of_words'] == 4, 'StreetNumber'] = df['StreetString0']
df.loc[df['number_of_words'] == 4, 'StreetName'] = df['StreetString1']
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['number_of_words'] == 4) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString0Length'] == 1), 'StreetName'] = df['StreetString1']
df.loc[(df['number_of_words'] == 4) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString1'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetSuffix'] = df['StreetString1']
df.loc[(df['number_of_words'] == 4) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString1'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE', 'CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString0']
df.loc[(df['number_of_words'] == 4) & (df['StreetNumberDigitOne'].isnull()) & (~df['StreetString2'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE','CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString1'] + ' ' + df['StreetString2']
df.loc[(df['number_of_words'] == 4) & (df['StreetNumberDigitOne'].isnull()) & (df['StreetString2'].isin(['AVE', 'BLVD', 'CIR', 'CLOSE','CRES', 'CRT', 'DR', 'LKOUT', 'LANE', 'PL', 'RD', 'ST', 'WAY'])), 'StreetName'] = df['StreetString1']
df['StreetNumberDigitOne'] = df['StreetNumber'].str[1]
df['StreetNumberDigitOne'] = df['StreetNumberDigitOne'].apply(pd.to_numeric, errors='coerce')
df.loc[(df['StreetNumberDigitOne'].isnull()), 'StreetNumber'] = ''

df['RootAddress'] = df['StreetNumber'] + " " + df['StreetDirectionalPrefix'] + " " + df['StreetName'] + " " + df['StreetSuffix'] + " " + df['StreetDirectionalSuffix']
df['RootAddress'] = df['RootAddress'].apply(lambda x: x.replace('  ', ' '))

#Transfer all area values to a standard floor area column and define in the Floor Area Type column
df.loc[df['TotalArea'] > 0, 'FloorArea'] = df['TotalArea']
df.loc[df['TotalArea'] > 0, 'FloorAreaType'] = 'Total Area'
df.loc[df['StrataUnitArea'] > 0, 'FloorArea'] = df['StrataUnitArea']
df.loc[df['StrataUnitArea'] > 0, 'FloorAreaType'] = 'StrataUnit Area'
df.loc[df['StrataUnitArea'] > 0, 'FloorArea'] = df['StrataUnitArea']
df.loc[df['StrataUnitArea'] > 0, 'FloorAreaType'] = 'Strata Unit Area'
df.loc[df['GBA'] > 0, 'FloorArea'] = df['GBA']
df.loc[df['GBA'] > 0, 'FloorAreaType'] = 'GBA'
df.loc[df['GLA'] > 0, 'FloorArea'] = df['GLA']
df.loc[df['GLA'] > 0, 'FloorAreaType'] = 'GLA'
df.loc[df['NLA'] > 0, 'FloorArea'] = df['NLA']
df.loc[df['NLA'] > 0, 'FloorAreaType'] = 'NLA'

#Remove parking from floor area calculations
df.loc[df['Occupancy'].str.contains('PARKING', regex=False) > 0, 'FloorArea'] = 0
#For TestOutputs
#df.to_excel("TestOutputs/BeforeAUC.xlsx")

#Update building categories based on Actual Use Code
df.set_index('PrimAUC', inplace=True)
df_AUC = pd.read_csv(r"Inputs/lut_ActualUseCode.csv")
df_AUC.set_index('PrimAUC', inplace=True)
df.update(df_AUC)
#For TestOutputs
#df.to_csv("TestOutputs/outturn_data_9.csv")
df = df.rename_axis('PrimAUC').reset_index()

#Refine building cagtegories based on Manual Class Code
#For TestOutputs
#df.to_excel("TestOutputs/BeforeMCC.xlsx")
#Refine building categries
df.set_index('MCC', inplace=True)
df_MCC = pd.read_csv(r"Inputs/lut_ManualClassCode.csv")
df_MCC.set_index('MCC', inplace=True)
df.update(df_MCC)
df = df.rename_axis('MCC').reset_index()
#For TestOutputs
#df.to_excel("TestOutputs/BeforeOccupancy.xlsx")

#Refine building categries based on Occupancy
df.set_index('Occupancy', inplace=True)
df_Occupancy = pd.read_csv(r"Inputs/lut_Occupancy.csv")
df_Occupancy.set_index('Occupancy', inplace=True)
df.update(df_Occupancy)
df = df.rename_axis('Occupancy').reset_index()
#For TestOutputs
#df.to_excel("TestOutputs/BeforeUnitOfMeasure.xlsx")

#Refine building categries based on Unit of Measure
df.set_index('UnitOfMeasure', inplace=True)
df_UnitOfMeasure = pd.read_csv(r"Inputs/lut_UnitOfMeasure.csv")
df_UnitOfMeasure.set_index('UnitOfMeasure', inplace=True)
df.update(df_UnitOfMeasure)
#Outbuildings for Residential properties
df.loc[(df['BuildingType'] == "Outbuilding") & (df['Major Category'] ==  "Residential"), 'Category'] = 'Category'
df.loc[(df['BuildingType'] == "Outbuilding") & (df['Major Category'] == "Residential"),  'Sub-category'] = "Other - residential"

#Remove any duplicates resulting from the assignment of building categories
df_temp = df.drop_duplicates()
df = df_temp

#Summarise number of units in Strata Unit Area buildings for future reference
df2 = df.filter(['Folio', 'StrataUnitArea', 'RootAddress'], axis = 1)
df3 = df2[df2['StrataUnitArea'].notnull()]
df4a = df3.drop_duplicates()
df4 = df4a.groupby(['RootAddress'])['StrataUnitArea'].sum().reset_index()
df4.rename(columns={'StrataUnitArea': 'StrataUnitAreaSum'}, inplace=True)
#For TestOutputs
#df4.to_excel("TestOutputs/StrataUnitAreaSum.xlsx")
df5 = df3.groupby(['RootAddress'])['StrataUnitArea'].count().reset_index()
df5.rename(columns={'StrataUnitArea': 'StrataUnitAreaCount'}, inplace=True)
#For TestOutputs
#df5.to_excel("TestOutputs/StrataUnitAreaCount.xlsx")
df_SUA = df.merge(df4, on='RootAddress', how='left')
df_SUA['StrataBuildingTotalArea'] = df_SUA['StrataUnitAreaSum']
df = df_SUA.merge(df5, on='RootAddress', how='left')
df['StrataBuildingUnitCount'] = df['StrataUnitAreaCount']
df.drop(['StrataUnitAreaCount', 'StrataUnitAreaSum'], axis=1, inplace=True)
df.loc[(df['StrataBuildingUnitCount'] > 0), 'BuildingComment'] = "This strata unit is part of a Building that has " + df['StrataBuildingUnitCount'].astype(str) + " strata units, and a total strata area of " + df['StrataBuildingTotalArea'].astype(str) + " square feet as calculated based on the number of records assigned to the Root Address."

#Summarise number of units in GBA buildings for future reference
df2 = df.filter(['Folio','RootAddress', 'GBA','NosUnits'], axis = 1)
df3 = df2[df2['GBA']>=1]
df4a = df3.drop_duplicates()
df4 = df4a.groupby(['RootAddress'])['GBA'].sum().reset_index()
df4.rename(columns={'GBA': 'GBAAreaSum'}, inplace=True)
#For TestOutputs
#df4.to_excel("TestOutputs/GBAAreaSum.xlsx")
df5 = df3.groupby(['RootAddress'])['NosUnits'].sum().reset_index()
df5.rename(columns={'NosUnits': 'GBAAreaUnitCount'}, inplace=True)
#For TestOutputs
#df5.to_excel("TestOutputs/GBAUnitCount.xlsx")
df_SUA = df.merge(df4, on='RootAddress', how='left')
df_SUA['GBABuildingTotalArea'] = df_SUA['GBAAreaSum']
#For TestOutputs
#df.to_excel("TestOutputs/GBAUnitCount_df_test.xlsx")
df = df_SUA.merge(df5, on='RootAddress', how='left')
df['GBAUnitCount'] = df['GBAAreaUnitCount']
df.loc[(df['NosUnits'].isnull()) & (df['FloorAreaType'] ==  "GBA"), 'GBAUnitCount'] = 1
df.loc[(df['GBAAreaUnitCount'].notnull()), 'BuildingCommentTemp'] = "This GBA Building has " + df['GBAUnitCount'].astype(str) + " GBA units, and a total GBA area of " + df['GBABuildingTotalArea'].astype(str) + " square feet as defined by BCA. One unit will be assigned if no units were allocated."
df.loc[(df['GBAAreaUnitCount'].notnull()), 'BuildingComment'] = df['BuildingComment'] + " " + df['BuildingCommentTemp']
df.drop(['GBAAreaUnitCount', 'GBAAreaSum'], axis=1, inplace=True)
#For TestOutputs
#df.to_excel("TestOutputs/DF_GBAUnitCount1.xlsx")

#Summarise number of units in GBA buildings for future reference
df2 = df.filter(['Folio','RootAddress', 'GBA', 'NosUnits'], axis = 1)
df3 = df2[df2['GBA'] >= 1]
df3b = df3[df3['NosUnits'].isnull()]
df4a = df3b.drop_duplicates()
df4 = df4a.groupby(['RootAddress'])['GBA'].sum().reset_index()
df4.rename(columns={'GBA': 'GBAAreaSum'}, inplace=True)
#For TestOutputs
#df4.to_excel("TestOutputs/GBAAreaSumNullNosUnits_a.xlsx")
df4['GBAAreaUnitCount'] = 0
df4['GBAAreaUnitCount'].astype(float)
#For TestOutputs
#df4.to_excel("TestOutputs/GBAAreaSumNullNosUnits_b.xlsx")
df4.loc[(df4['GBAAreaSum'] >= 1000), 'GBAAreaUnitCount'] = df4['GBAAreaSum'] / 1000
df4.loc[(df4['GBAAreaSum'] < 1000), 'GBAAreaUnitCount'] = 1
#For TestOutputs
#df4.to_excel("TestOutputs/GBAAreaSumNullNosUnits.xlsx")
df_temp = df.merge(df4, on='RootAddress', how='left')
df = df_temp
df.loc[(df['GBAUnitCount'].isnull()),'GBAUnitCount'] = df['GBAAreaUnitCount']
df.loc[(df['GBABuildingTotalArea'].isnull()),'GBABuildingTotalArea'] = df['GBAAreaSum']
df.drop(['GBAAreaUnitCount', 'GBAAreaSum'], axis=1, inplace=True)

#Summarise number of units in GLA buildings for future reference
df2 = df.filter(['Folio', 'GLA', 'RootAddress'], axis = 1)
df3 = df2[df2['GLA'].notnull()]
df4a = df3.drop_duplicates()
df4 = df4a.groupby(['RootAddress'])['GLA'].sum().reset_index()
df4.rename(columns={'GLA': 'GLAAreaSum'}, inplace=True)
#For TestOutputs
#df4.to_excel("TestOutputs/GLAAreaSum.xlsx")
df5 = df3.groupby(['RootAddress'])['GLA'].count().reset_index()
df5.rename(columns={'GLA': 'GLAAreaUnitCount'}, inplace=True)
#For TestOutputs
#df5.to_excel("TestOutputs/GLAUnitCount.xlsx")
df_SUA = df.merge(df4, on='RootAddress', how='left')
df_SUA['GLABuildingTotalArea'] = df_SUA['GLAAreaSum']
df = df_SUA.merge(df5, on='RootAddress', how='left')
df['GLAUnitCount'] = df['GLAAreaUnitCount']
df.loc[(df['GLAAreaUnitCount'] > 0), 'BuildingCommentTemp'] = "This GLA unit is part of a Building that has " + df['GLAUnitCount'].astype(str) + " GLA units as calculated based on the number of records assigned to the Root Address (BCA did not define the number of units), and a total GLA area of " + df['GLABuildingTotalArea'].astype(str) + " square feet as calculated based on the number of records assigned to the Root Address."
df.loc[(df['GLAAreaUnitCount'] > 0), 'BuildingComment'] = df['BuildingComment'] + " " + df['BuildingCommentTemp']
df.drop(['GLAAreaUnitCount', 'GLAAreaSum'], axis=1, inplace=True)

#Summarise number of units in Total Area buildings
df2 = df.filter(['Folio', 'TotalArea', 'RootAddress'], axis = 1)
df3 = df2[df2['TotalArea'].notnull() & (df['BuildingType'] != "Outbuilding")]
df4a = df3.drop_duplicates()
df4 = df4a.groupby(['RootAddress'])['TotalArea'].sum().reset_index()
df4.rename(columns={'TotalArea': 'TotalAreaAreaSum'}, inplace=True)
#For TestOutputs
#df4.to_excel("TestOutputs/TotalAreaAreaSum.xlsx")
df5 = df3.groupby(['RootAddress'])['TotalArea'].count().reset_index()
df5.rename(columns={'TotalArea': 'TotalAreaAreaUnitCount'}, inplace=True)
#For TestOutputs
#df5.to_excel("TestOutputs/TotalAreaUnitCount.xlsx")
df_SUA = df.merge(df4, on='RootAddress', how='left')
df_SUA['TotalAreaBuildingTotalArea'] = df_SUA['TotalAreaAreaSum']
#df_SUA = df_SUA.drop(['StrataUnitAreaSum'], axis=1)
df = df_SUA.merge(df5, on='RootAddress', how='left')
df['TotalAreaUnitCount'] = df['TotalAreaAreaUnitCount']
df.loc[(df['BuildingType'] == "Outbuilding"), 'TotalAreaBuildingTotalArea'] = 0
df.loc[(df['BuildingType'] == "Outbuilding"), 'TotalAreaAreaUnitCount'] = 0
df.loc[(df['TotalAreaAreaUnitCount'].notnull()),'BuildingCommentTemp'] = "This unit is part of a Building that has " + df['TotalAreaUnitCount'].astype(str) + " units, and a total area of " + df['TotalAreaBuildingTotalArea'].astype(str) + " square feet as defined by BCA."
df.loc[(df['TotalAreaAreaUnitCount'].notnull()), 'BuildingComment'] = df['BuildingComment'] + " " + df['BuildingCommentTemp']
df.drop(['TotalAreaAreaUnitCount', 'TotalAreaAreaSum'], axis=1, inplace=True)

#Summarise number of units in NLA buildings for future reference
df2 = df.filter(['Folio', 'NLA', 'RootAddress'], axis = 1)
df3 = df2[df2['NLA'].notnull()]
df4a = df3.drop_duplicates()
df4 = df4a.groupby(['RootAddress'])['NLA'].sum().reset_index()
df4.rename(columns={'NLA': 'NLAAreaSum'}, inplace=True)
#For TestOutputs
#df4.to_excel("TestOutputs/NLAAreaSum.xlsx")
df5 = df3.groupby(['RootAddress'])['NLA'].count().reset_index()
df5.rename(columns={'NLA': 'NLAAreaUnitCount'}, inplace=True)
#For TestOutputs
#df5.to_excel("TestOutputs/NLAUnitCount.xlsx")

df_SUA = df.merge(df4, on='RootAddress', how='left')
df_SUA['NLABuildingTotalArea'] = df_SUA['NLAAreaSum']
#df_SUA = df_SUA.drop(['StrataUnitAreaSum'], axis=1
df = df_SUA.merge(df5, on='RootAddress', how='left')
df['NLAUnitCount'] = df['NLAAreaUnitCount']
df.loc[(df['NLAAreaUnitCount'] > 0), 'BuildingCommentTemp'] = "This NLA unit is part of a Building that has " + df['NLAUnitCount'].astype(str) + " NLA units as calculated based on the number of records assigned to the Root Address (BCA did not define the number of units), and a total NLA area of " + df['NLABuildingTotalArea'].astype(str) + " square feet as calculated based on the number of records assigned to the Root Address."
df.loc[(df['NLAAreaUnitCount'] > 0), 'BuildingComment'] = df['BuildingComment'] + " " + df['BuildingCommentTemp']
df.drop(['NLAAreaUnitCount', 'NLAAreaSum'], axis=1, inplace=True)

#Summarise number of units in Total Area buildings
df.loc[(df['BuildingType'] == "Outbuilding"), 'TotalAreaUnitCount'] = df['NosUnits']
df.loc[(df['BuildingType'] == "Outbuilding"), 'UnitByRootAddressCount'] = df['NosUnits']
df.loc[(df['BuildingType'] == "Outbuilding") & (df['NosUnits'].isnull()), 'TotalAreaUnitCount'] = 1
df.loc[(df['BuildingType'] == "Outbuilding") & (df['NosUnits'].isnull()), 'UnitByRootAddressCount'] = 1
df.loc[(df['BuildingType'] == "Outbuilding"), 'BuildingCommentTemp'] = "This unit is defined as an Outbuilding that has " + df['UnitByRootAddressCount'].astype(str) + " units, a total area of " + df['TotalArea'].astype(str) + " square feet as defined by BCA."
df.loc[(df['BuildingType'] == "Outbuilding"), 'BuildingComment'] = df['BuildingComment'] + " " + df['BuildingCommentTemp']

#Remove outbuilding number of units and floor area to avoid confusing the summaries
df.loc[(df['BuildingType'] == "Outbuilding"), 'TotalAreaUnitCount'] = 0
df.loc[(df['BuildingType'] == "Outbuilding"), 'UnitByRootAddressCount'] = 0
df.loc[df['TotalAreaUnitCount'].isnull(), 'TotalAreaUnitCount'] = 0
df.loc[df['TotalAreaBuildingTotalArea'].isnull(), 'TotalAreaBuildingTotalArea'] = 0
df.loc[df['GLAUnitCount'].isnull(), 'GLAUnitCount'] = 0
df.loc[df['GLABuildingTotalArea'].isnull(), 'GLABuildingTotalArea'] = 0
df.loc[df['NLAUnitCount'].isnull(), 'NLAUnitCount'] = 0
df.loc[df['NLABuildingTotalArea'].isnull(), 'NLABuildingTotalArea'] = 0
df.loc[df['GBAUnitCount'].isnull(), 'GBAUnitCount'] = 0
df.loc[df['GBABuildingTotalArea'].isnull(), 'GBABuildingTotalArea'] = 0
df.loc[df['StrataBuildingUnitCount'].isnull(), 'StrataBuildingUnitCount'] = 0
df.loc[df['StrataBuildingTotalArea'].isnull(), 'StrataBuildingTotalArea'] = 0
df['BuildingFloorArea'] = df['TotalAreaBuildingTotalArea'] + df['GLABuildingTotalArea'] + df['NLABuildingTotalArea'] + df['GBABuildingTotalArea'] + df['StrataBuildingTotalArea']
df['UnitByRootAddressCount'] = df['TotalAreaUnitCount'] + df['GLAUnitCount'] + df['NLAUnitCount'] + df['GBAUnitCount'] + df['StrataBuildingUnitCount']
#For TestOutputs
#df.to_excel("TestOutputs/StrataUnitArea Check in main df.xlsx")

#Threshold for Part 3 / Part 9 is 600 square meters or 6458.35 square feet (identified in column Part3_Part9)
df.loc[(df['StrataBuildingTotalArea'] > 6458.35), 'Part3_Part9'] = "Part 3"
df.loc[(df['StrataBuildingTotalArea'] > 6458.35) & (df['Major Category'] ==  "Residential"), 'Sub-category'] = "Hi-rise apartment"

#Allocate buildings to vintages
df.loc[df['YearBuilt'] >= 2013, 'Vintage'] = '2013 and later'
df.loc[df['YearBuilt'] <= 2012, 'Vintage'] = '1996-2012'
df.loc[df['YearBuilt'] < 1996, 'Vintage'] = '1978-1995'
df.loc[df['YearBuilt'] < 1978, 'Vintage'] = '1977 and prior'
df.loc[df['YearBuilt'].isnull(), 'Vintage'] = '1977 and prior'

#Add census tract and neighbourhood spatial information
df.set_index('Folio', inplace=True)
df_Assessment_Fabric = pd.read_csv(r"Inputs/ASSESSMENT_FABRIC_CENTROIDS_with_NEIGHBOURHOODS.csv")
df_Assessment_Fabric['Folio'] = pd.to_numeric(df_Assessment_Fabric['Folio'])
df_Assessment_Fabric['CT'].astype(int)
df_Assessment_Fabric['Neighbourhood'].astype(str)
df_Assessment_Fabric['X'].astype(float)
df_Assessment_Fabric['Y'].astype(float)
df_Assessment_Fabric.set_index('Folio', inplace=True)
df.update(df_Assessment_Fabric)
df = df.rename_axis('Folio').reset_index()

#Simplify table by dropping temporary fields
df.drop(['BuildingCommentTemp', 'StreetUnitMarker', 'dup_id', 'StreetUnitMarker', 'StreetStringLengthCheck', 'StreetString1Length', 'StreetStringNotSure', 'StreetString0Length', 'StreetString1Length', 'StreetString2Length', 'StreetString3Length', 'StreetString4Length', 'StreetString5Length', 'StreetString6Length','StreetString7Length'], axis=1, inplace=True)

#Simplify table by dropping duplicates
df_temp = df.drop_duplicates()
df = df_temp
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

#For TestOutputs
#df.to_excel("TestOutputs/Before_drop_df.xlsx")

#Drop records that are for outbuildings to esnure counts are as accurate as they can be
df = df.drop(df[df['BuildingType'] == 'Outbuilding'].index)
#For TestOutputs
#df.to_excel("TestOutputs/final_df.xlsx")
df_original = df

'''
Develop different summaries and groupings
'''

#remove floor area and  'NosUnits', 
df_with_address_original = df.groupby(['RootAddress', 'X', 'Y', 'UnitByRootAddressCount', 'BuildingFloorArea', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfSub-categories')
#For TestOutputs
#df_with_address_original.to_excel("TestOutputs/final_df_with_address_original.xlsx")

#remove vintages, 
df_with_address_original_no_vintage = df.groupby(['RootAddress', 'X', 'Y', 'UnitByRootAddressCount', 'BuildingFloorArea', 'Major Category', 'Category', 'Sub-category', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfSub-categoriesNoVintage')
#For TestOutputs
#df_with_address_original_no_vintage.to_excel("TestOutputs/final_df_with_address_original_no_vintage.xlsx")

#remove sub-category, 
df_with_address_original_category = df.groupby(['RootAddress', 'X', 'Y', 'UnitByRootAddressCount', 'BuildingFloorArea', 'Major Category', 'Category',  'BCBCOccupancyCode', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfCategories')
#For TestOutputs
#df_with_address_original_category.to_excel("TestOutputs/final_df_with_address_original_category.xlsx")

#remove category
df_with_address_original_major_category = df.groupby(['RootAddress', 'X', 'Y', 'UnitByRootAddressCount', 'BuildingFloorArea','Major Category', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfMajorCategories')
#For TestOutputs
#df_with_address_original_major_category.to_excel("TestOutputs/final_df_with_address_original_major_category.xlsx")


df_with_address = df.groupby(['RootAddress', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict', 'BuildingFloorArea','UnitByRootAddressCount']).size().reset_index(name='CountOfRecords')
#For TestOutputs
#df_with_address.to_excel("TestOutputs/final_df_with_address_group.xlsx")

df_with_address2 = df_with_address.groupby(['RootAddress', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict', 'BuildingFloorArea'])['UnitByRootAddressCount'].sum().reset_index()
df_with_address2['RootAddressSubCategoryVintage'] = df_with_address2['RootAddress'] + "|" + df_with_address2['Sub-category'] + "|" + df_with_address2['Vintage']
df_with_address_dups = df_with_address2.groupby(['RootAddress', 'Sub-category', 'RootAddressSubCategoryVintage']).size().reset_index(name='CountOfRecords') 
#For TestOutputs
#df_with_address_dups.to_excel("TestOutputs/final_df_with_address_dups.xlsx")

df_with_address_dups2 = df_with_address_dups.groupby(['RootAddress']).size().reset_index(name='CountOfSub-categories') 
df_with_address_dups2.to_excel("TestOutputs/final_df_with_address_dups2.xlsx")
df_with_address2_no_vintage = df_with_address.groupby(['RootAddress', 'Major Category', 'Category', 'Sub-category', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict', 'BuildingFloorArea'])['UnitByRootAddressCount'].sum().reset_index()
df_with_address2_no_vintage['RootAddressSubCategory'] = df_with_address2_no_vintage['RootAddress'] + "|" + df_with_address2_no_vintage['Sub-category']
df_with_address_dups_no_vintage = df_with_address2_no_vintage.groupby(['RootAddress', 'Sub-category', 'RootAddressSubCategory']).size().reset_index(name='CountOfRecords') 
#For TestOutputs
#df_with_address_dups_no_vintage.to_excel("TestOutputs/final_df_with_address_dups_no_vintage.xlsx")

df_with_address_dups2_no_vintage = df_with_address_dups_no_vintage.groupby(['RootAddress']).size().reset_index(name='CountOfSub-categoriesNoVintage')
#For TestOutputs
#df_with_address_dups2_no_vintage.to_excel("TestOutputs/final_df_with_address_dups2_no_vintage.xlsx")

df_with_address2_category = df_with_address.groupby(['RootAddress', 'Major Category', 'Category', 'BCBCOccupancyCode', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict', 'BuildingFloorArea'])['UnitByRootAddressCount'].sum().reset_index()
df_with_address2_category['RootAddressSubCategory'] = df_with_address2_category['RootAddress'] + "|" + df_with_address2['Category']
df_with_address_dups_category = df_with_address2_category.groupby(['RootAddress', 'Category', 'RootAddressSubCategory']).size().reset_index(name='CountOfRecords') 
#For TestOutputs
#df_with_address_dups_category.to_excel("TestOutputs/final_df_with_address_dups_category.xlsx")

df_with_address_dups2_category = df_with_address_dups_category.groupby(['RootAddress']).size().reset_index(name='CountOfCategories') 
#For TestOutputs
#df_with_address_dups2.to_excel("TestOutputs/final_df_with_address_dups2_category.xlsx")

df_with_address2_MajorCategory = df_with_address.groupby(['RootAddress', 'Major Category', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict', 'BuildingFloorArea'])['UnitByRootAddressCount'].sum().reset_index()
df_with_address2_MajorCategory['RootAddressSubCategory'] = df_with_address2_MajorCategory['RootAddress'] + "|" + df_with_address2['Major Category']
df_with_address_dups_MajorCategory = df_with_address2_MajorCategory.groupby(['RootAddress', 'Major Category', 'RootAddressSubCategory']).size().reset_index(name='CountOfRecords') 
#For TestOutputs
#df_with_address_dups_MajorCategory.to_excel("TestOutputs/final_df_with_address_dups_MajorCategory.xlsx")

df_with_address_dups2_MajorCategory = df_with_address_dups_MajorCategory.groupby(['RootAddress']).size().reset_index(name='CountOfMajorCategories') 
#For TestOutputs
#df_with_address_dups2_MajorCategory.to_excel("TestOutputs/final_df_with_address_dups2_MajorCategory.xlsx")

df_with_address.rename(columns={'UnitByRootAddressCount': 'UniqueUnitCount'}, inplace=True)
#For TestOutputs
#df_with_address.to_excel("TestOutputs/final_df_with_address.xlsx")


df_lean = df.groupby(['Folio', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs
#df_lean.to_excel("TestOutputs/final_df_lean.xlsx")

df_lean_address = df.groupby(['Folio', 'RootAddress', 'X', 'Y', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs
#df_lean_address.to_excel("TestOutputs/final_df_lean_address.xlsx")

df_address_only = df_lean_address.groupby(['RootAddress', 'X', 'Y', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs
#df_address_only.to_excel("TestOutputs/final_df_address_only.xlsx")

df_lean_address_no_vintage = df_lean_address.groupby(['Folio', 'RootAddress', 'X', 'Y', 'Major Category', 'Category', 'Sub-category', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs
#df_address_only.to_excel("TestOutputs/final_df_address_only.xlsx")

df_lean_address_category_only = df_lean_address.groupby(['Folio', 'RootAddress', 'X', 'Y', 'Major Category', 'Category', 'BCBCOccupancyCode', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs
#df_address_only.to_excel("TestOutputs/final_df_address_only.xlsx")

#Export final excel book with summaries based on different groupings
with pd.ExcelWriter("Outputs/Enhanced_BIR.xlsx") as writer:
	df_original.to_excel(writer, sheet_name = "all records", index=False)
	df_lean_address.to_excel(writer, sheet_name = "by Folio and Root Address", index=False)
	df_lean_address_no_vintage.to_excel(writer, sheet_name = "by Folio Address no vintage", index=False)
	df_lean_address_category_only.to_excel(writer, sheet_name = "by Folio Address category only", index=False)
	df_with_address_original.to_excel(writer, sheet_name = "by Root Address Sub-category", index=False)
	df_with_address_original_no_vintage.to_excel(writer, sheet_name = "by Root Address no vintage", index=False)
	df_with_address_original_category.to_excel(writer, sheet_name = "by Root Address category", index=False)
	df_with_address_original_major_category.to_excel(writer, sheet_name = "by Root Address major category", index=False)
	df_with_address_dups2.to_excel(writer, sheet_name = "Multis Sub-category", index=False)
	df_with_address_dups2_no_vintage.to_excel(writer, sheet_name = "Multis Sub-category no vintage", index=False)
	df_with_address_dups2_category.to_excel(writer, sheet_name = "Multis Category", index=False)
	df_with_address_dups2_MajorCategory.to_excel(writer, sheet_name = "Multis Major Category", index=False)


	

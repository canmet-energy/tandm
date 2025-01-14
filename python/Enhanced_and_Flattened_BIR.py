import os
import json

import shutil
import pandas as pd 
import click
import numpy as np

import re

'''
This is the second script. 
It is to be used after the Enhanced_BIR.py script has been run. 

After the Enhanced_BIR.py script has been run, the resulting worksheet 'by Root Address Sub-category" found in Enhanced_BIR.xlsx
must be spatially joined to either a flattened BC Assessment Fabric layer, or Parcel Map BC layer (both with no overlapping polygons and a unique ID for each polygon)

The unique Parcel ID must be included in a FABRIC_ID column and FABRIC_ID_COUNT column must be created to identify the preliminary number of Enhanced_BIR records that fall within each FABRIC_ID

The results of that spatial work must be saved in a file called 'Enhanced_BIR_Points_with_count.csv' for this script to work

With that information, this script will aggregate building categories and vintages so that one unique record is created for each polygon
This process allows for a one to many relationship between one building category and vintage aggregation and many utility meter locations within a parcel

This script relies on input data available in a Inputs subfolder and will export results to a Outputs subfolder
A TestOutputs folder is used for staged outputs as the script progresses if the export commands are uncommented
To export staged working files, search for #For TestOutputs and uncomment the export line below or add new exports in the script

These subfolders must exist before running the script: Inputs, Outputs, TestOutputs
'''

'''
Import the file that identifies which BCAA building information points belong within which parcel ID (identified by the FABRIC_ID) and the preliminary estimate of how many 
building information points exist within each parcel ID point
'''
df_GIS = pd.read_csv(r"Inputs/Enhanced_BIR_Points_with_count.csv")
df_GIS = df_GIS.drop(df_GIS[df_GIS['UnitByRootAddress'] == 0].index)
#For TestOutputs 
#df_GIS.to_excel("TestOutputs/df_GIS_withUnits.xlsx")

#Complete one set of grouping and aggregation at the root address level and a second at the parcel level to ensure proper accounting of unit numbers and building floor area
#first set for root address 
#Group to find count greater than 2
df_GIS_address_count_1b = df_GIS.groupby(['RootAddress', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict','UnitByRootAddress','BuildingFloorArea']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_1b.to_excel("TestOutputs/df_GIS_address_count_1b.xlsx")

df_GIS_address_count_1b_check = df_GIS_address_count_1b.groupby(['RootAddress']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_1b_check.to_excel("TestOutputs/df_GIS_address_count_1b_check.xlsx")
df_GIS_address_count_1b.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_address_count_1b = df_GIS_address_count_1b.merge(df_GIS_address_count_1b_check, on='RootAddress', how='left')
df_GIS_address_count_1b['RootAddress_COUNT'] = df_GIS_address_count_1b['CountOfRecords']
#For TestOutputs 
#df_GIS_address_count_1b.to_excel("TestOutputs/df_GIS_address_count_1b_updated.xlsx")

#Assign two vintage categories to counts greater than 1
df_GIS_address_count_2 = df_GIS_address_count_1b
df_GIS_address_count_2.loc[(df_GIS_address_count_2['RootAddress_COUNT'] > 1) & (df_GIS_address_count_1b['Vintage'] == "1977 and prior"),  'Vintage'] = "1977 and prior"
df_GIS_address_count_2.loc[(df_GIS_address_count_2['RootAddress_COUNT'] > 1) & (df_GIS_address_count_1b['Vintage'].isin(['1978-1995', '1996-2012', '2013 and later'])),  'Vintage'] = "1978 and later"
df_GIS_address_count_2ab = df_GIS_address_count_2.groupby(['RootAddress','RootAddress_COUNT', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict','UnitByRootAddress','BuildingFloorArea']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_2ab.to_excel("TestOutputs/df_GIS_address_count_2ab.xlsx")
df_GIS_address_count_2ab_check = df_GIS_address_count_2ab.groupby(['RootAddress']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_2ab_check.to_excel("TestOutputs/df_GIS_address_count_2ab_check.xlsx")
df_GIS_address_count_2ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_address_count_2ab = df_GIS_address_count_2ab.merge(df_GIS_address_count_2ab_check, on='RootAddress', how='left')
df_GIS_address_count_2ab['RootAddress_COUNT'] = df_GIS_address_count_2ab['CountOfRecords']
#For TestOutputs 
#df_GIS_address_count_2ab.to_excel("TestOutputs/df_GIS_address_count_2ab_updated.xlsx")

#Assign one vintage categories to counts greater than 1
df_GIS_address_count_3 = df_GIS_address_count_2ab
df_GIS_address_count_3.loc[(df_GIS_address_count_3['RootAddress_COUNT'] > 1),  'Vintage'] = "All years"
df_GIS_address_count_3ab = df_GIS_address_count_3.groupby(['RootAddress', 'RootAddress_COUNT', 'Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict','UnitByRootAddress','BuildingFloorArea']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_3ab.to_excel("TestOutputs/df_GIS_address_count_3ab.xlsx")
df_GIS_address_count_3ab_check = df_GIS_address_count_3ab.groupby(['RootAddress']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_3ab_check.to_excel("TestOutputs/df_GIS_address_count_3ab_check.xlsx")
df_GIS_address_count_3ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_address_count_3ab = df_GIS_address_count_3ab.merge(df_GIS_address_count_3ab_check, on='RootAddress', how='left')
df_GIS_address_count_3ab['RootAddress_COUNT'] = df_GIS_address_count_3ab['CountOfRecords']
#For TestOutputs 
#df_GIS_address_count_3ab.to_excel("TestOutputs/df_GIS_address_count_3ab_updated.xlsx")

#Assign Aggregate to Sub-categoty to counts greater than 1
df_GIS_address_count_4 = df_GIS_address_count_3ab
df_GIS_address_count_4.loc[(df_GIS_address_count_4['RootAddress_COUNT'] > 1),  'Sub-category'] = "Aggregated"
df_GIS_address_count_4ab = df_GIS_address_count_4.groupby(['RootAddress', 'RootAddress_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict','UnitByRootAddress','BuildingFloorArea']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_4ab.to_excel("TestOutputs/df_GIS_address_count_4ab.xlsx")
df_GIS_address_count_4ab_check = df_GIS_address_count_4ab.groupby(['RootAddress']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_4ab_check.to_excel("TestOutputs/df_GIS_address_count_4ab_check.xlsx")
df_GIS_address_count_4ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_address_count_4ab = df_GIS_address_count_4ab.merge(df_GIS_address_count_4ab_check, on='RootAddress', how='left')
df_GIS_address_count_4ab['RootAddress_COUNT'] = df_GIS_address_count_4ab['CountOfRecords']
#For TestOutputs 
#df_GIS_address_count_4ab.to_excel("Data/df_GIS_address_count_4ab_updated.xlsx")

#Assign Aggregated to Category to counts greater than 1
df_GIS_address_count_5 = df_GIS_address_count_4ab
df_GIS_address_count_5.loc[(df_GIS_address_count_5['RootAddress_COUNT'] > 1),  'Category'] = "Aggregated"
df_GIS_address_count_5ab = df_GIS_address_count_5.groupby(['RootAddress', 'RootAddress_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict','UnitByRootAddress','BuildingFloorArea']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_5ab.to_excel("TestOutputs/df_GIS_address_count_5ab.xlsx")
df_GIS_address_count_5ab_check = df_GIS_address_count_5ab.groupby(['RootAddress']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_5ab_check.to_excel("TestOutputs/df_GIS_address_count_5ab_check.xlsx")
df_GIS_address_count_5ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_address_count_5ab = df_GIS_address_count_5ab.merge(df_GIS_address_count_5ab_check, on='RootAddress', how='left')
df_GIS_address_count_5ab['RootAddress_COUNT'] = df_GIS_address_count_5ab['CountOfRecords']
#For TestOutputs 
#df_GIS_address_count_5ab.to_excel("TestOutputs/df_GIS_address_count_5ab_updated.xlsx")

#Assign Mixed-use to Major-Category to counts greater than 1
df_GIS_address_count_6 = df_GIS_address_count_5ab
df_GIS_address_count_6.loc[(df_GIS_address_count_6['RootAddress_COUNT'] > 1),  'Major Category'] = "Mixed-use"
df_GIS_address_count_6.loc[(df_GIS_address_count_6['RootAddress_COUNT'] > 1),  'BCBCOccupancy'] = "Aggregated"
df_GIS_address_count_6.loc[(df_GIS_address_count_6['RootAddress_COUNT'] > 1),  'Part3_Part9'] = "Aggregated"
df_GIS_address_count_6ab = df_GIS_address_count_6.groupby(['RootAddress', 'RootAddress_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict','UnitByRootAddress','BuildingFloorArea']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_address_count_6ab.to_excel("TestOutputs/df_GIS_address_count_6ab.xlsx")
df_GIS_address_count_6ab_check = df_GIS_address_count_6ab.groupby(['RootAddress']).size().reset_index(name='CountOfRecords')
#df_GIS_address_count_6ab_check.to_excel("TestOutputs/df_GIS_address_count_6ab_check.xlsx")
df_GIS_address_count_6ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_address_count_6ab = df_GIS_address_count_6ab.merge(df_GIS_address_count_6ab_check, on='RootAddress', how='left')
df_GIS_address_count_6ab['RootAddress_COUNT'] = df_GIS_address_count_6ab['CountOfRecords']
#For TestOutputs 
#df_GIS_address_count_6ab.to_excel("TestOutputs/df_GIS_address_count_6ab_updated.xlsx")

#second set for parcel level - Fabric_ID
#Group to find count greater than 2
df_GIS_count_1b = df_GIS.groupby(['FABRIC_ID','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_1b.to_excel("TestOutputs/df_GIS_count_1b.xlsx")
df_GIS_count_1b_check = df_GIS_count_1b.groupby(['FABRIC_ID']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_1b_check.to_excel("TestOutputs/df_GIS_count_1b_check.xlsx")
df_GIS_count_1b.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_count_1b = df_GIS_count_1b.merge(df_GIS_count_1b_check, on='FABRIC_ID', how='left')
df_GIS_count_1b['FABRIC_ID_COUNT'] = df_GIS_count_1b['CountOfRecords']
#For TestOutputs 
#df_GIS_count_1b.to_excel("TestOutputs/df_GIS_count_1b_updated.xlsx")

#Assign two vintage categories to counts greater than 1
df_GIS_count_2 = df_GIS_count_1b
df_GIS_count_2.loc[(df_GIS_count_2['FABRIC_ID_COUNT'] > 1) & (df_GIS_count_1b['Vintage'] == "1977 and prior"),  'Vintage'] = "1977 and prior"
df_GIS_count_2.loc[(df_GIS_count_2['FABRIC_ID_COUNT'] > 1) & (df_GIS_count_1b['Vintage'].isin(['1978-1995', '1996-2012', '2013 and later'])),  'Vintage'] = "1978 and later"
df_GIS_count_2ab = df_GIS_count_2.groupby(['FABRIC_ID', 'FABRIC_ID_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_2ab.to_excel("TestOutputs/df_GIS_count_2ab.xlsx")
df_GIS_count_2ab_check = df_GIS_count_2ab.groupby(['FABRIC_ID']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_2ab_check.to_excel("TestOutputs/df_GIS_count_2ab_check.xlsx")
df_GIS_count_2ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_count_2ab = df_GIS_count_2ab.merge(df_GIS_count_2ab_check, on='FABRIC_ID', how='left')
df_GIS_count_2ab['FABRIC_ID_COUNT'] = df_GIS_count_2ab['CountOfRecords']
#For TestOutputs 
#df_GIS_count_2ab.to_excel("TestOutputs/df_GIS_count_2ab_updated.xlsx")

#Assign one vintage categories to counts greater than 1
df_GIS_count_3 = df_GIS_count_2ab
df_GIS_count_3.loc[(df_GIS_count_3['FABRIC_ID_COUNT'] > 1),  'Vintage'] = "All years"
df_GIS_count_3ab = df_GIS_count_3.groupby(['FABRIC_ID', 'FABRIC_ID_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_3ab.to_excel("TestOutputs/df_GIS_count_3ab.xlsx")
df_GIS_count_3ab_check = df_GIS_count_3ab.groupby(['FABRIC_ID']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_3ab_check.to_excel("TestOutputs/df_GIS_count_3ab_check.xlsx")
df_GIS_count_3ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_count_3ab = df_GIS_count_3ab.merge(df_GIS_count_3ab_check, on='FABRIC_ID', how='left')
df_GIS_count_3ab['FABRIC_ID_COUNT'] = df_GIS_count_3ab['CountOfRecords']
#For TestOutputs 
#df_GIS_count_3ab.to_excel("TestOutputs/df_GIS_count_3ab_updated.xlsx")

#Assign Aggregate to Sub-categoty to counts greater than 1
df_GIS_count_4 = df_GIS_count_3ab
df_GIS_count_4.loc[(df_GIS_count_4['FABRIC_ID_COUNT'] > 1),  'Sub-category'] = "Aggregated"
df_GIS_count_4ab = df_GIS_count_4.groupby(['FABRIC_ID', 'FABRIC_ID_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_4ab.to_excel("TestOutputs/df_GIS_count_4ab.xlsx")
df_GIS_count_4ab_check = df_GIS_count_4ab.groupby(['FABRIC_ID']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_4ab_check.to_excel("TestOutputs/df_GIS_count_4ab_check.xlsx")
df_GIS_count_4ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_count_4ab = df_GIS_count_4ab.merge(df_GIS_count_4ab_check, on='FABRIC_ID', how='left')
df_GIS_count_4ab['FABRIC_ID_COUNT'] = df_GIS_count_4ab['CountOfRecords']
#For TestOutputs 
#df_GIS_count_4ab.to_excel("TestOutputs/df_GIS_count_4ab_updated.xlsx")

#Assign Aggregated to Category to counts greater than 1
df_GIS_count_5 = df_GIS_count_4ab
df_GIS_count_5.loc[(df_GIS_count_5['FABRIC_ID_COUNT'] > 1),  'Category'] = "Aggregated"
df_GIS_count_5ab = df_GIS_count_5.groupby(['FABRIC_ID', 'FABRIC_ID_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_5ab.to_excel("TestOutputs/df_GIS_count_5ab.xlsx")
df_GIS_count_5ab_check = df_GIS_count_5ab.groupby(['FABRIC_ID']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_5ab_check.to_excel("TestOutputs/df_GIS_count_5ab_check.xlsx")
df_GIS_count_5ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_count_5ab = df_GIS_count_5ab.merge(df_GIS_count_5ab_check, on='FABRIC_ID', how='left')
df_GIS_count_5ab['FABRIC_ID_COUNT'] = df_GIS_count_5ab['CountOfRecords']
#For TestOutputs 
#df_GIS_count_5ab.to_excel("TestOutputs/df_GIS_count_5ab_updated.xlsx")

#Assign Mixed-use to Major-Category to counts greater than 1
df_GIS_count_6 = df_GIS_count_5ab
df_GIS_count_6.loc[(df_GIS_count_6['FABRIC_ID_COUNT'] > 1),  'Major Category'] = "Mixed-use"
df_GIS_count_6.loc[(df_GIS_count_6['FABRIC_ID_COUNT'] > 1),  'BCBCOccupancy'] = "Aggregated"
df_GIS_count_6.loc[(df_GIS_count_6['FABRIC_ID_COUNT'] > 1),  'Part3_Part9'] = "Aggregated"
df_GIS_count_6ab = df_GIS_count_6.groupby(['FABRIC_ID', 'FABRIC_ID_COUNT','Major Category', 'Category', 'Sub-category', 'Vintage', 'BCBCOccupancy', 'Part3_Part9', 'CT', 'Neighbourhood', 'Municipality', 'RegionalDistrict']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_6ab.to_excel("TestOutputs/df_GIS_count_6ab.xlsx")
df_GIS_count_6ab_check = df_GIS_count_6ab.groupby(['FABRIC_ID']).size().reset_index(name='CountOfRecords')
#For TestOutputs 
#df_GIS_count_6ab_check.to_excel("TestOutputs/df_GIS_count_6ab_check.xlsx")
df_GIS_count_6ab.drop(['CountOfRecords'], axis=1, inplace=True)
df_GIS_count_6ab = df_GIS_count_6ab.merge(df_GIS_count_6ab_check, on='FABRIC_ID', how='left')
df_GIS_count_6ab['FABRIC_ID_COUNT'] = df_GIS_count_6ab['CountOfRecords']
#For TestOutputs 
#df_GIS_count_6ab.to_excel("TestOutputs/df_GIS_count_6ab_updated.xlsx")

#Create Energy Report 1: Community-wide, Major Categories, Four Vintages
df_ER1_count_step1 = df_GIS_address_count_6ab.groupby(['Major Category', 'Vintage','RootAddress', 'UnitByRootAddress']).size().reset_index(name='CountOfBuildings')
df_ER1_count_step2 = df_ER1_count_step1.groupby(['Major Category', 'Vintage'])['CountOfBuildings'].sum().reset_index()
#For TestOutputs 
#df_ER1_count_step2.to_excel("TestOutputs/ER1-comm-MajCat-4V-count_lean.xlsx")
df_ER1_unitcount = df_ER1_count_step1.groupby(['Major Category', 'Vintage'])['UnitByRootAddress'].sum().reset_index()
#For TestOutputs 
#df_ER1_unitcount.to_excel("TestOutputs/ER1-comm-MajCat-4V-UnitCount_lean.xlsx")
df_ER1 = df_ER1_count_step2.merge(df_ER1_unitcount, left_on=['Major Category', 'Vintage'], right_on = ['Major Category', 'Vintage'], how='left')
#For TestOutputs 
#df_ER1.to_excel("TestOutputs/ER1-comm-MajCat-4V.xlsx")

#Create Energy Report 2: Community-wide, Sub Categories, Four Vintages
df_ER2_count_step1 = df_GIS_address_count_6ab.groupby(['Sub-category', 'Vintage','RootAddress','UnitByRootAddress']).size().reset_index(name='CountOfBuildings')
df_ER2_count_step2 = df_ER2_count_step1.groupby(['Sub-category', 'Vintage'])['CountOfBuildings'].sum().reset_index()
#For TestOutputs 
#df_ER2_count_step2.to_excel("TestOutputs/ER2-comm-SubCat-4V-count.xlsx")
df_ER2_unitcount = df_ER2_count_step1.groupby(['Sub-category', 'Vintage'])['UnitByRootAddress'].sum().reset_index()
#For TestOutputs 
#df_ER2_unitcount.to_excel("TestOutputs/ER2-comm-SubCat-4V-UnitCount.xlsx")
df_ER2 = df_ER2_count_step2.merge(df_ER2_unitcount, left_on=['Sub-category', 'Vintage'], right_on = ['Sub-category', 'Vintage'], how='left')
#For TestOutputs 
#df_ER2.to_excel("TestOutputs/ER2-comm-SubCat-4V.xlsx")

#Create Energy Report 3: Community-wide, Code parts, Four Vintages
df_ER3_count_step1 = df_GIS_address_count_6ab.groupby(['Part3_Part9', 'Vintage','RootAddress','UnitByRootAddress']).size().reset_index(name='CountOfBuildings')
df_ER3_count_step2 = df_ER3_count_step1.groupby(['Part3_Part9', 'Vintage'])['CountOfBuildings'].sum().reset_index()
#For TestOutputs 
#df_ER3_count_step2.to_excel("TestOutputs/ER3-comm-CodeParts-4V-count.xlsx")
df_ER3_unitcount = df_ER3_count_step1.groupby(['Part3_Part9', 'Vintage'])['UnitByRootAddress'].sum().reset_index()
#df_ER3_unitcount.to_excel("TestOutputs/ER3-comm-CodeParts-4V-UnitCount.xlsx")
df_ER3 = df_ER3_count_step2.merge(df_ER3_unitcount, left_on=['Part3_Part9', 'Vintage'], right_on = ['Part3_Part9', 'Vintage'], how='left')
#For TestOutputs 
#df_ER3.to_excel("TestOutputs/ER3-comm-CodeParts-4V.xlsx")

#Create Energy Report 4: Community-wide, BCBC Occupancy Codes, Four Vintages
df_ER4_count_step1 = df_GIS_address_count_6ab.groupby(['BCBCOccupancy', 'Vintage','RootAddress','UnitByRootAddress']).size().reset_index(name='CountOfBuildings')
df_ER4_count_step2 = df_ER4_count_step1.groupby(['BCBCOccupancy', 'Vintage'])['CountOfBuildings'].sum().reset_index()
#For TestOutputs 
#df_ER4_count_step2.to_excel("TestOutputs/ER4-comm-CodeParts-4V-count.xlsx")
df_ER4_unitcount = df_ER4_count_step1.groupby(['BCBCOccupancy', 'Vintage'])['UnitByRootAddress'].sum().reset_index()
#For TestOutputs 
#df_ER4_unitcount.to_excel("TestOutputs/ER4-comm-CodeParts-4V-UnitCount.xlsx")
df_ER4 = df_ER4_count_step2.merge(df_ER4_unitcount, left_on=['BCBCOccupancy', 'Vintage'], right_on = ['BCBCOccupancy', 'Vintage'], how='left')
#For TestOutputs 
#df_ER4.to_excel("TestOutputs/ER4-comm-CodeParts-4V.xlsx")

#Create Energy Report 5: Neighbourhood Scale, Major Building Categories, Four Vintages
df_ER5_count_step1 = df_GIS_address_count_6ab.groupby(['Neighbourhood', 'Major Category','RootAddress', 'UnitByRootAddress']).size().reset_index(name='CountOfBuildings')
df_ER5_count_step2 = df_ER5_count_step1.groupby(['Neighbourhood', 'Major Category'])['CountOfBuildings'].sum().reset_index()
#For TestOutputs 
#df_ER5_count_step2.to_excel("TestOutputs/ER5-neigh-MajCat-4V-count.xlsx")
df_ER5_unitcount = df_ER5_count_step1.groupby(['Neighbourhood', 'Major Category'])['UnitByRootAddress'].sum().reset_index()
#For TestOutputs 
#df_ER5_unitcount.to_excel("TestOutputs/ER5-neigh-MajCat-4V-UnitCount.xlsx")
df_ER5 = df_ER5_count_step2.merge(df_ER5_unitcount, left_on=['Neighbourhood', 'Major Category'], right_on = ['Neighbourhood', 'Major Category'], how='left')
#For TestOutputs 
#df_ER5.to_excel("TestOutputs/ER5-neigh-MajCat-4V.xlsx")

#Create Energy Report 6: Census Tracts, Major Building Categories, Four Vintages
df_ER6_count_step1 = df_GIS_address_count_6ab.groupby(['CT', 'Major Category', 'Vintage','RootAddress', 'UnitByRootAddress']).size().reset_index(name='CountOfBuildings')
df_ER6_count_step2 = df_ER6_count_step1.groupby(['CT', 'Major Category', 'Vintage'])['CountOfBuildings'].sum().reset_index()
#For TestOutputs 
#df_ER6_count_step2.to_excel("TestOutputs/ER6-CT-MajCat-4V-count.xlsx")
df_ER6_unitcount = df_ER6_count_step1.groupby(['CT', 'Major Category','Vintage'])['UnitByRootAddress'].sum().reset_index()
#For TestOutputs 
#df_ER6_unitcount.to_excel("TestOutputs/ER6-CT-MajCat-4V-UnitCount.xlsx")
df_ER6 = df_ER6_count_step2.merge(df_ER6_unitcount, left_on=['CT', 'Major Category', 'Vintage'], right_on = ['CT', 'Major Category', 'Vintage'], how='left')
#For TestOutputs 
#df_ER6.to_excel("TestOutputs/ER6-CT-MajCat-4V.xlsx")

#Export final table
with pd.ExcelWriter("Outputs/Enhanced_and_Flattened_BIR.xlsx") as writer:
	df_GIS_count_6ab.to_excel(writer, sheet_name = "Enhanced_and_Flattened_BIR", index=False)
	df_ER1.to_excel(writer, sheet_name = "ER1-comm-MajCat-4V", index=False)
	df_ER2.to_excel(writer, sheet_name = "ER2-comm-SubCat-4V", index=False)
	df_ER3.to_excel(writer, sheet_name = "ER3-comm-CodeParts-4V", index=False)
	df_ER4.to_excel(writer, sheet_name = "ER4-comm-OccCodes-4V", index=False)
	df_ER5.to_excel(writer, sheet_name = "ER5-neigh-MajCat-4V", index=False)
	df_ER6.to_excel(writer, sheet_name = "ER6-CT-MajCat-4V", index=False)


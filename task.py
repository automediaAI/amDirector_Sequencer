##############
#### DIRECTOR v0.2 ####
#################
###### Sequence of frames ###########
## Fills 'Sequence' column in order that frames need to be displayed; runs for each media property separately ##
## Based on manually entered Section_Sequence_x columns 1,2 ## 
##############
## Ticket: https://www.notion.so/automedia/Create-Director-Py-v1-ie-LordCreator-v1-8daca81456de496494cde882f993d034
#############

## Declarations 
import os
from airtable import Airtable
import pandas as pd

# Airtable settings 
base_key = os.environ.get("PRIVATE_BASE_KEY")
table_name = os.environ.get("PRIVATE_TABLE_NAME")
api_key = os.environ.get("PRIVATE_API_KEY")
airtable = Airtable(base_key, table_name, api_key) #For production env

## Function to get how many media properties are there, to run loop
def getMediaProperties(colToCheck='media_property'):
	allProperties = airtable.get_all(fields='media_property')
	uniqueProperties = []
	for i in allProperties:
		mediaProp = i['fields'][colToCheck]
		if mediaProp not in uniqueProperties:
			uniqueProperties.append(mediaProp)
	return (uniqueProperties)

## Actual loop to update Airtable sequence - NOT EFFICIENT ALGO, Change to something better
def updateLoop(
		mediaProperty, 
		viewToCheck = 'Sections View', 
		outputSequenceCol='Sequence', 
		inputSequence1='Section_Sequence_1', 
		inputSequence2='Section_Sequence_2', 
		statusGood='Standby', 
		statusFail='Error - QA',
		):
	allRecords = airtable.get_all(formula="({media_property}='%s')" %(mediaProperty)) #Limits dict size
	df = pd.DataFrame.from_records((r['fields'] for r in allRecords)) # From https://github.com/iampatterson/
	# print('df filtered:', df)
	#Convert columns to integer, normally string
	df[inputSequence1] = pd.to_numeric(df[inputSequence1], errors='coerce') 
	df[inputSequence2] = pd.to_numeric(df[inputSequence2], errors='coerce') 
	# Max for each column
	get_max_col1 = int(df[inputSequence1].max()) 
	get_max_col2 = int(df[inputSequence2].max()) 
	# Coordinates to check
	x_index = [i+1 for i in range(get_max_col1)]
	y_index = [i+1 for i in range(get_max_col2)]
	seq_toUpdate = 1 #First sequence

	# Actual algorithm that matches, not good
	for y in y_index:
		for x in x_index:
			for i in allRecords:
				# print('Coord to test',(x,y))
				if "Prod_Ready" in i["fields"]:
					if (i["fields"][inputSequence1]==str(x)) and (i["fields"][inputSequence2]==str(y)): 
						recID = i["id"]
						fields = {outputSequenceCol: seq_toUpdate}
						airtable.update(recID, fields)
						seq_toUpdate += 1
## Actual loop that runs program	
allProperties = getMediaProperties(colToCheck='media_property')
print ('Media property list gathered..')
for i in allProperties:
	updateLoop(mediaProperty = i)
	print ('Media property complete..')
print ('Table complete..')

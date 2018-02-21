import csv
import copy
import os
import time
import re

import Time_Stuff

# This function is a wrapper around other functions to deal with issues
# that cause exceptions which can be solved simply by waiting and trying again
# One example is OS calls that, when called back to back, may not complete synchronously
def AdvancedTryToRun( times_to_try, function, *args ):
	success = False
	for retries in range(0,times_to_try):
		try:
			function( *args )
			success = True
			break
		except:
			time.sleep(1) # wait a second and then try again
			continue
	return success

def GetBlackboardFormatData( Data_File_Location, Settings ):
	all_data = {}

	gradesfile = open( Data_File_Location, 'r', newline = '' )
	gradesreader = csv.reader( gradesfile, delimiter = ',' )

	headers = next( gradesreader )
	header_to_index = {}
	translated_headers = []
	for index, header in enumerate( headers ):
		for key in Settings.keys():
			found1 = re.search( "(.*?)\s\[", header )
			if( found1 ):
				grade_title = found1.group(1)
			else:
				grade_title = None
			if( key == grade_title or (key == header and Settings[key] in ['UIN']) ):
				header_to_index[ Settings[key] ] = index
				translated_headers.append( Settings[key] )

	for header in translated_headers:
		all_data[ header ] = []

	for row in gradesreader:
		for header in translated_headers:
			index = header_to_index[ header ]
			all_data[ header ].append( row[index] )
			
	gradesfile.close()

	return all_data

def GetSettingsFile( directory_location ):
	all_data = {}
	filename = directory_location + '/Config.csv'

	settings_file = open( filename, 'r', newline = '' )
	settings_reader = csv.reader( settings_file, delimiter = ',' )

	for row in settings_reader:
		if( len(row) > 1 ):
			if( len(row) > 2 and row[2] is not '' ):
				all_data[row[0]] = row[1:]
			else:
				all_data[row[0]] = row[1]

	return all_data

def SaveSettingsFile( directory_location, settings, log ):
	temp_filename = directory_location + '/Config_tmp.csv'
	try:
		temp_settings_file = open( temp_filename, 'w', newline = '' )
	except: # File didn't open
		log( "Error opening " + temp_filename )
		return False

	temp_settings_writer = csv.writer( temp_settings_file, delimiter = ',' )
	for setting in settings.keys():
		full_row = [setting]
		if isinstance(settings[ setting ], list):
			full_row += settings[ setting ]
		else:
			full_row.append( settings[ setting ] )

		temp_settings_writer.writerow( full_row )

	temp_settings_file.close()

	filename = directory_location + '/Config.csv'

	if( False == AdvancedTryToRun( 5, os.remove, filename ) ):
		log( "Error removing old version of " + filename )
		return False

	if( False == AdvancedTryToRun( 5, os.rename, temp_filename, filename ) ):
		log( "Error renaming new version of " + temp_filename + " to " + filename )
		return False

	return True


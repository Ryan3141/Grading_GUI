import time


dtformat = '%Y-%m-%d %H:%M:%S' #format used for date-time visualization
dtformatexcel = '%m/%d/%Y %H:%M' #format excel likes to change the date-time to

def TimeToString( epoc ):
	return time.strftime(dtformat, time.localtime( epoc ))

def StringToTime( tstring ):
	try:
		t = time.strptime( tstring, dtformat )
	except ValueError:
		#try:
		#	t = time.strptime( tstring, dtformatexcel )
		#except ValueError:
		raise Exception( "Problem understanding date format, likely from pbworks or from resaving revisions file in excel: " + tstring )
			#t = time.strptime( '00', '%M' )
	return time.mktime( t )

def SortByTime( list_of_times ):
	sorted_list_of_times = []

	for time in list_of_times:
		sorted_list_of_times.append( StringToTime(time) )

	sorted_list_of_times.sort()
	sorted_list_of_times.reverse()

	output_list = []
	for time in sorted_list_of_times:
		output_list.append( TimeToString(time) )

	return output_list

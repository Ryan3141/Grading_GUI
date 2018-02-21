import numpy
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pylab

import re

def is_number( s ):
	try:
		float( s )
		return True
	except ValueError:
		return False


# turns stuff like '1-3' into '1,2,3'
def expand_string_to_list(m):
	first_number = int(m.group(1))
	last_number = int(m.group(2))
	list_of_strings = []
	for x in range(first_number, last_number + 1):
		list_of_strings.append( str(x) )

	list_as_string = ','.join( list_of_strings )
	return list_as_string

#import pyparsing as Literal,Word,ZeroOrMore,Forward,nums,oneOf,Group
from pyparsing import *
import pyparsing as pp
def ParseMath():
	#LPAR,RPAR = map(Suppress, '()')
	#expr = Forward()
	expop = Literal('^')
	signop = Word('-')
	multop = oneOf('* /')
	plusop = oneOf('+ -')
	variable = Literal("HW") | Literal("QZ") | Literal("GP") | Literal("PT") | Literal("LW")
	operand = Regex(r"-?\d+(\.\d*)?([Ee][+-]?\d+)?") | variable
	#factor = operand | Group(LPAR + expr + RPAR)
	#term = factor + ZeroOrMore( oneOf('* /') + factor )
	#expr << term + ZeroOrMore( oneOf('+ -') + term )
	expr = operatorPrecedence(operand,
		[(signop, 1, opAssoc.RIGHT),
		(multop, 2, opAssoc.LEFT),
		(plusop, 2, opAssoc.LEFT)] ) + StringEnd()
	return expr

def FindNeededVariables( find_in_me ):
	variables_to_find = ['HW','QZ','GP','PT','LW']
	variables_found = []
	for variable in variables_to_find:
		if( find_in_me.find( variable ) != -1 ):
			variables_found.append( variable )

	return variables_found

#def test(s):
#	expr = ParseMath()
#	results = expr.parseString( s )
#	print( str(s) + '->' + str(results) )

#def Fancy_Parsing():
#	test("(-1*(20 - 3 / 4 +5.5 * 0.9))+ 2/4")
#	test("(-1*(HW - 3 / 4 +5.5 * QZ))+ 2/4")
#	test("(1**2)")
#	test("(1--2test)")

def Get_Number( element, dictionary_of_data, week_number, index ):
	if is_number( element ):
		number = float( element )
	else:
		data_label = element + week_number
		number = float( dictionary_of_data[ data_label ][ index ] )

	return number

def Recursively_Solve( equation_to_evaluate, dictionary_of_data, week_number, index ):
	valid_operators = ['-','+','*','/']
	one_back = ''
	two_back = ''
	for element in equation_to_evaluate:
		if type( element ) is list:
			new_number = Recursively_Solve( element, dictionary_of_data, week_number, index )
		elif element not in valid_operators:
			new_number = Get_Number( element, dictionary_of_data, week_number, index )
		else:
			one_back = element
			two_back = one_back
			continue

		operator_to_use = one_back
		if( one_back == '-' ):
			if( two_back in valid_operators ):
				operator_to_use = two_back
				new_number = -new_number

		if( operator_to_use == '+' ):
			full_number += new_number
		elif( operator_to_use == '-' ):
			full_number -= new_number
		elif( operator_to_use == '*' ):
			full_number *= new_number
		elif( operator_to_use == '/' ):
			full_number /= new_number
		elif( operator_to_use == '' ):
			full_number = new_number

		one_back = element
		two_back = one_back

	return full_number


def Prepare_Data( dictionary_of_data, equation_to_evaluate, variables_needed, weeks_to_include, sections_to_include ):
	nuber_of_valid_scores = 0
	nuber_of_scores = 0
	all_data = []


	for index, current_student_section in enumerate( dictionary_of_data[ 'Section' ] ):
		for week_number in weeks_to_include:

			if current_student_section in sections_to_include:
				nuber_of_scores += 1

				valid_number = True
				for variable in variables_needed:
					data_type = variable + week_number
					if data_type in dictionary_of_data.keys():
						if not is_number( dictionary_of_data[data_type][index] ):
							valid_number = False

				if( not valid_number ):
					continue

				try: # try so if divide by zero error happens, we just don't use the individual element
					total_number = Recursively_Solve( equation_to_evaluate, dictionary_of_data, week_number, index )
					nuber_of_valid_scores += 1
					all_data.append( total_number )
				except:
					continue

	return all_data, nuber_of_valid_scores, nuber_of_scores

def Make_CDF( data, artificial_smooth = True ):
	x = []
	y = []

	if len( data ) < 2:
		return x, y

	sorted_data = sorted( data )

	total_number_of_data = len( sorted_data )
	previous_element = sorted_data[0]
	previous_index = 0
	previous_count = 0

	for index, element in enumerate( sorted_data ):
		if element != previous_element:
			bin_count = index - previous_index

			if not artificial_smooth:
				x.append( previous_element )
				y.append( previous_count / total_number_of_data )

			previous_count = previous_count + bin_count
			x.append( previous_element )
			y.append( previous_count / total_number_of_data )

			previous_element = element
			previous_index = index

	# It's possible that the last point was never added
	if sorted_data[ total_number_of_data - 1 ] == sorted_data[ total_number_of_data - 2 ]:
		if not artificial_smooth:
			x.append( sorted_data[ total_number_of_data - 1 ] )
			y.append( previous_count / total_number_of_data )

		x.append( sorted_data[ total_number_of_data - 1 ] )
		y.append( 1.0 )

	return x, y

def RemoveDictionaries( from_me ):
	if( type( from_me ) is str ):
		return from_me
	results = []
	for index in range( 0, len( from_me ) ):
		results.append( RemoveDictionaries( from_me[index] ) )

	return results


def Analyze( what_to_graph, dictionary_of_data, sections, histogram_weeks, artificial_smooth, log ):

	colors_to_use = ['r','g','b','#000000','#00ffff','#ff00ff','#ac731a','#ff8000','#6a0a60']
	linestyles=['-','--']

	# Can only graph so many unique looking lines
	if len(sections) > len(linestyles) * len(colors_to_use):
		return

	#num_bins = 500
	# the histogram of the data
	ax = plt.subplot(111)
	expanded_weeks = re.sub("(\d+)-(\d+)", expand_string_to_list, histogram_weeks)
	list_of_weeks = expanded_weeks.split( "," )
	try:
		variables_needed = FindNeededVariables( what_to_graph )
		parsed_expression = ParseMath().parseString( what_to_graph )
		equation_to_evaluate = RemoveDictionaries( parsed_expression )

		if( len( variables_needed ) == 0 ):
			raise Exception('')
	except:
		log( "Invalid request string" )
		return


	for index, section in enumerate( sections ):
		data,nuber_of_valid_scores,nuber_of_scores = Prepare_Data( dictionary_of_data, equation_to_evaluate, variables_needed, list_of_weeks, [section] )
		label_string = section + ": " + str(nuber_of_valid_scores) + "/" + str(nuber_of_scores)
		x, y = Make_CDF( data, artificial_smooth )
		ax.plot( x, y, label=label_string, linewidth=2,
		  color=colors_to_use[index%len(colors_to_use)], linestyle=linestyles[int(2*index/len(sections))])

	plt.xlabel('Score')
	plt.ylabel('Probability')
	plt.grid(b=True, which='major', color='b', linestyle='-')
	ax.set_yticks(numpy.arange(0,1,0.1) )
	#ax.set_yticks( [0.001, 0.01, 0.1, 1, 5, 25,50, 75, 95, 99, 99.9, 99.99, 99.999] )
	plt.title( what_to_graph + " : " + expanded_weeks )

	# Tweak spacing to prevent clipping of ylabel
	plt.subplots_adjust(left=0.15)

	# Adjust graph window bounds to fit everything best
	box = ax.get_position()
	box.x0 = 0.1
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	#plt.savefig('foo.png')
	plt.show()
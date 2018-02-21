try:
	import Statistics_Analysis
	science_libraries_available = True
except ImportError:
    science_libraries_available = False

#Here are basic imports which are necessary for various functions used throughout the code

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import CSV_Reader
import Time_Stuff
from datetime import datetime
from shutil import copyfile


class Window():
	def __init__(self, master):
		#Create a button to run the main routine for getting and storing grades
		self.tkmaster = master
		self.tkmaster.columnconfigure(0, weight=1)
		self.tkmaster.rowconfigure(0, weight=1)
		self.select_csv_file = tk.Button(master, text="Select File", command=self.find_file) #A button to bring up a directory selection dialog. Selected directory is where grade report is stored
		self.select_csv_file.grid(row=1,column=0, sticky='s,w', padx=5, pady=5)
		self.selected_csv_file = tk.Entry(master, width=50)#Display the currently selected directory
		self.selected_csv_file.grid(row=1,column=1, padx=5, pady=5, sticky='s,w,e,n')
		#self.selected_csv_file.insert( tk.INSERT, os.getcwd().replace( '\\', '/' ) + "/Data" )
		self.settings = CSV_Reader.GetSettingsFile( os.getcwd().replace( '\\', '/' ) )
		self.selected_csv_file.insert( tk.INSERT, self.settings['Previous_Directory'] )

		self.graph_options_frame = tk.Frame(master)
		self.graph_options_frame.grid(row=0, column=4, padx=5, pady=5)
		self.histogram_button = tk.Button(self.graph_options_frame, text="Histogram", command=self.show_histogram)
		self.histogram_button.grid(row=0, column=0)
		#self.graph_display = tk.Label(master, height=25, width=70, bg="white")
		#self.graph_display.grid(row=0, column=4, rowspan=3, padx=15, pady=15)

		self.histogram_request = tk.Entry(self.graph_options_frame, width=48)
		self.histogram_request.grid(row=1, column=0)
		self.histogram_request.insert( tk.INSERT, 'lw + pt + qz + hw + gp' )
		self.histogram_weeks = tk.Entry(self.graph_options_frame, width=48)
		self.histogram_weeks.grid(row=2, column=0)
		self.histogram_weeks.insert( tk.INSERT, '1-10' )
		self.histogram_sections = tk.Entry(self.graph_options_frame, width=48)
		self.histogram_sections.grid(row=3, column=0)
		self.histogram_sections.insert( tk.INSERT, ','.join( self.settings['List_Of_Secs'] ) )
		self.artifical_smooth = tk.BooleanVar()
		tk.Checkbutton(self.graph_options_frame, text="Use Artificial Smoothing", variable=self.artifical_smooth).grid(row=4, sticky='w')


	def show_histogram(self):
		'''Take a dictionary representing all grade data and create a histogram, displayed in self.graph_display (to be created)'''
		if science_libraries_available:
			request = self.histogram_request.get().replace(" ", "")
			sections_to_graph = self.histogram_sections.get().replace(" ", "")
			weeks_to_graph = self.histogram_weeks.get().replace(" ", "")
			try:
				most_up_to_date_data = CSV_Reader.GetBlackboardFormatData( self.selected_csv_file.get(), self.settings )
			except IOError as e:
				self.append_message( "I/O error({0}): {1}".format(e.errno, e.strerror) )
				self.append_message( "You should make sure the .csv files aren't open then try again." )
				return
			except:
				self.append_message('Unknown file opening error occurred.')
				return

			Statistics_Analysis.Analyze( request.upper(), most_up_to_date_data, sections_to_graph.upper().split(','), weeks_to_graph, self.artifical_smooth.get(), log=self.append_message )
		else:
			self.append_message( 'ERROR: Missing python science libraries matplotlib and numpy' )

	def append_message( self, msg, error_code ='', alert_level=2, add_newline=True ):
		pass

	def find_file(self):
		'''Open directory selection dialog display currently selected file to user'''
		file_options = {}
		current_location = self.settings['Previous_Directory']
		k = current_location.rfind("/")
		file_options['initialdir'] = current_location[0:k]
		file_location = filedialog.askopenfilename(**file_options)
		if( file_location is not '' ):
			self.selected_csv_file.delete(0, tk.END)
			self.selected_csv_file.insert( tk.INSERT, file_location )
			self.settings['Previous_Directory'] = file_location
			CSV_Reader.SaveSettingsFile( os.getcwd().replace( '\\', '/' ), self.settings, log=self.append_message )

tkmaster = tk.Tk()
tkmaster.title("Physics 106/108 Grading")
tkmaster.iconbitmap('uic.ico')
tkmaster.configure(background="#333333")
window = Window(tkmaster)
tk.mainloop()

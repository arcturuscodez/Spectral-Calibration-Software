import sys
import datetime
import globals
from optparse import OptionParser, OptionGroup

o = OptionParser(usage='main [-option] <directory>',
version=f'Program name: {globals.PROGRAM_NAME}, Version: {globals.PROGRAM_VERSION}, Creation date: {globals.PROGRAM_CREATION_DATE}')

# OPTION GROUPS

directory_group = OptionGroup(o, "Directory options", "Options for specifying the directory or filtering contained files")
filtering_group = OptionGroup(o, "Filtering options, Options for filtering files based on specified rules")
processing_group = OptionGroup(o, "Plotting options", "Various options for processing functionality")
plotting_group = OptionGroup(o, "Axes options", "Options for selecting data to plot in subplot 2")
utility_group = OptionGroup(o, "Utility options", "Miscellaneous utility options")
saving_group = OptionGroup(o, "File Saving options", "Options for saving data to a FITS file")

# Directory 

directory_group.add_option('-d', '--directory',
  dest='directory',
  type=str,
  default=None,
  metavar='<directory>',
  help='Specify a directory path to utilize and process in the software')

# Filtering

filtering_group.add_option('--fc', '--centrefreqrange',
  dest='cfreq',
  type=str,
  default='0:1e20',
  metavar='Lower:Upper [MHz]',
  help='Set a specified centre frequency range or value to process, Ex: 6668.5192:6669.5192 (Include specific range), 0:9000 (Include all below 9000), 4000:0 (Include all above 4000)')

filtering_group.add_option('-t', '--telescope',
  dest='telescope',
  type=str,
  default='MCA1',
  metavar='MCA2',
  help='Select files to process based on the observing telescope, Ex: MCA1, MCA2, MAINANT')

filtering_group.add_option('-s', '--starttime',
  dest='start',
  type=str,
  default='2000-01-01T01:01:01',
  metavar='2024-03-06T17:00:04 [YYYY:MM:DDTHH:MM:SS]',
  help='Define a starting date and time of which files to process, Ex: 2020-03-06T17:00:04')

filtering_group.add_option('-e', '--endtime',
  dest='end',
  type=str,
  default=datetime.datetime.max.strftime('%Y-%m-%dT%H:%M:%S'),
  metavar='2024-03-06T00:00:04 [YYYY:MM:DDTHH:MM:SS]',
  help='Define a ending date and time of which files to process, Ex: 2024-03-06T19:00:04')

filtering_group.add_option('--el', '--elevation',
  dest='elevation',
  type=int,
  default=0,
  metavar='50',
  help='Exclude files which are observed with an elevation less than this value, Ex. 50, 40, 5')

# Processing

processing_group.add_option('-c', '--channels',
  dest='channels',
  type=str, 
  default='0:4096',
  metavar='CH:CH',
  help='Set the range of channels to process, Ex: 350:3500')

processing_group.add_option('-p', '--polarization',
  dest='polarization',
  type=str,
  default='R',
  metavar='r, R, l, L, b, B',
  help='Specify the polarization to process, Ex: (r, R = Right) (l, L = Left) (b, B = Both)')

processing_group.add_option('--fr','--restfreq',
  dest='rfreq',
  type=float,
  default=6668.5192,
  metavar='6668.5192 [MHz]',
  help='Specify the rest frequency to calculate the velocity data on, Ex: 6668.5192')

processing_group.add_option('-b', '--bins',
  dest='bins',
  type=int,
  default='1000',
  metavar='500',
  help='Define the total channels(bins) to re-grid frequency & velocity data into, Ex: 500, 750, 5000')

processing_group.add_option('-m', '--median',
  dest='median',
  action='store_true',
  default=False,
  help='Enable a median calculation and remove the result from the signal data')

# Plotting

plotting_group.add_option('--RV', '--byregridvelo',
  dest='regridveloplot',
  action='store_true',
  default=False,
  help='Plot using regridded velocity data')

plotting_group.add_option('--RF', '--byregridfreq',
  dest='regridfreqplot',
  action='store_true',
  default=False,
  help='Plot using regridded frequency data')

plotting_group.add_option('--sumv', '--bysumvr',
  dest='sumvrplot',
  action='store_true',
  default=False,
  help='Plot the sum of regridded velocity')

plotting_group.add_option('--sumf', '--bysumfr',
  dest='sumfrplot',
  action='store_true',
  default=False,
  help='Plot the sum of regridded frequency')

plotting_group.add_option('-V', '--byvelocity',
  dest='veloplot',
  action='store_true',
  default=False,
  help='Plot using base velocity data (without regridding)')

plotting_group.add_option('-F', '--byfrequency',
  dest='freqplot',
  action='store_true',
  default=False,
  help='Plot the base frequency data (without regridding)')

plotting_group.add_option('-C', '--bychannels',
  dest='chanplot',
  action='store_true',
  default=False,
  help='Plot total channel count (unaffected by -c/--channels)')

plotting_group.add_option('-B', '--bybins',
  dest='binplot',
  action='store_true',
  default=False,
  help='Plot total frequency bins contributing to the regridding')

# Utility

processing_group.add_option('--fig', '--figuresize',
  dest='figsize',
  type=str, 
  default='10:6',
  metavar='X:Y',
  help='Set the size of the figure, Ex. 20:10')

utility_group.add_option('--gr', '--plotgrid',
  dest='grid',
  action='store_true',
  default=False,
  help='Enable a grid for both subplots on the figure')

utility_group.add_option('--md', '--plotmetadata',
  dest='plotmetadata',
  action='store_true',
  default=False,
  help='Display metadata on the figure')

utility_group.add_option('--dbg', '--debug',
  dest='debug',
  action='store_true',
  default=False,
  help='Debug and print relevant information from loaded FITS files')

utility_group.add_option('--sub', '--subplot',
  dest='subplotlabel',
  action='store_true',
  default=False,
  help='Add subplot labels to the subplots')

utility_group.add_option('--test', '--testrun',
  dest='testrun',
  action='store_true',
  default=False,
  help='Run the program without plotting or saving')

# File Saving 

saving_group.add_option('--sv', '--savedata',
  dest='savedata',
  action='store_true',
  default=False,
  help='Save the processed data to a FITS file')

saving_group.add_option('--pr', '--print',
  dest='printdata',
  action='store_true',
  default=False,
  help='Print the newly saved processed data to the terminal')

saving_group.add_option('-o', '--output',
  dest='output',
  type=str,
  default=None,
  metavar='output.fits',
  help='Save the processed data to a user defined FITS file, Ex: testfile, maser, G232')

# Add Option Group

o.add_option_group(directory_group)
o.add_option_group(filtering_group)
o.add_option_group(processing_group)
o.add_option_group(plotting_group)
o.add_option_group(utility_group)
o.add_option_group(saving_group)

# Parse Arguments

(o, args) = o.parse_args(sys.argv[1:])

__all__ = ['o', 'args']
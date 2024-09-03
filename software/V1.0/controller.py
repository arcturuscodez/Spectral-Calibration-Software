# Imports
import os
import sys
import time
import globals
import numpy as np
from datetime import datetime, timedelta
from astropy.io import fits
from astropy.table import Table
from options import o

class FITSHandler:
  # FITSHandler Constructor
  def __init__(self, directory): # Constructor
    try:
      # Set the directory attribute
      self.directory = directory
      # Validate that the provided directory is an actual directory
      if not os.path.isdir(self.directory):
        # If not a directory, raise NotADirectoryError
        raise NotADirectoryError(f'{self.directory}, is not a valid directory')
    
      # Intialize relevant attributes
      self.files = [] # List to store paths of FITS files
      self.frequencies = [] # List to store frequency data from FITS files
      self.channels = [] # List to store channel data from FITS files
      self.rhcp = [] # List to store RHCP data from FITS files
      self.lhcp = [] # List to Store LHCP dataa from FITS files
      # Initialize a directory to store metadata for each FITS file
      self.metadata = {}
      
      # Initialize counters and process start time
      self.filecount = 0 # Count of valid FITS files
      self.count = 0 # Count of processed FITS files
      self.process = time.time() # Record the start time of the processing 
      
      # Call methods to handle different tasks
      self.HandleDirectory() # Process the directory and gather FITS files
      self.HandleLoadMetaData() # Load metadata from the FITS files
      self.HandleFilterFiles() # Filter files based on certain criteria
      self.HandleLoadData() # Load data from the filtered FITS files
    except(NotADirectoryError, Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : {self.directory}.')
      quit()
    
  def HandleDirectory(self):
    try:
      # Walk through the directory tree from bottom to top
      for root, dirs, files in os.walk(self.directory, topdown=False):
        # Iterate over each file in the current directory
        for file in files:
          # Check if the file has a '.fits' extension
          if file.endswith('.fits'):
            # Construct the full path to the file
            full_path = os.path.join(root, file)
            # Add the full path to the list of FITS files
            self.files.append(full_path)
          else:
            # Inform that the file is not a FITS file and ignore it
            print(f'File: {file} is not a FITS file, it was ignored')
            continue
    except (Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : {self.directory}.')
      quit()
          
  def HandleLoadMetaData(self):
    try:
      # Iterate over the list of files with their index
      for idx, file in enumerate(self.files):
        # Check if the list of files is empty or not properly set  
        if self.files is None or self.files == 0:
          # Raise an error if no files are detected
          raise FileNotFoundError(f'No files detected: {self.files}')
        # Load metadata from the current FITS file
        metadata = self.LoadMetaData(file)
        # Check if metadata was successfully retrieved
        if metadata is not None:
          # Store the metadata in the dictionary with the file index as the key
          self.metadata[idx] = metadata
        else:
          # Raise an error if metadata is empty
          raise ValueError(f'Metadata is empty {metadata}')
    except (FileNotFoundError, ValueError, Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : {file}.')
      quit()
    
  def HandleFilterFiles(self):
    # Filter files method
    try:
      # Initialize lists and dictionaries to store valid files and their metadata
      valid_files = []
      valid_metadata = {}
      # Parse the center frequency range from options and convert to float 
      cfrl, cfru = o.cfreq.split(':')
      cfrl = float(cfrl) if cfrl else 0
      cfru = float(cfru) if cfru else 1e20
      lower_threshold, upper_threshold = float(cfrl), float(cfru)
      # Iterate over files and their corresponding metadata
      for idx, file in enumerate(self.files):
        metadata = self.metadata[idx]
        # Check if the file's observation dates are within the specified range
        if (metadata['DATE-OBS'] <= datetime.strptime(str(o.start),'%Y-%m-%dT%H:%M:%S') 
          or
          metadata['DATE-END'] >= datetime.strptime(str(o.end),'%Y-%m-%dT%H:%M:%S')):
          print(f'File: {file} ignored due to out of range start/end time: {metadata["DATE-OBS"]} - {metadata["DATE-END"]}')
          continue # Skip files that do not meet the time range criteria
        # Check if the file's center frequency is within the specified range
        elif not lower_threshold < metadata['FREQ'] < upper_threshold:
          print(f'File: {self.files[idx]} ignored due to out of range centre frequency: {metadata["FREQ"]}')
          continue # Skip files that do not meet the frequency range criteria
        # Check if the telescope used matches the specified telescope
        elif metadata['TELESCOP'] != o.telescope:
          print(f'File: {self.files[idx]} ignored due to incorrect telescope used: {metadata["TELESCOP"]}')
          continue # Skip files that do not match the specified telescope
        # Check if the elevation during observation meets the minimum required
        elif metadata['EL-BEG'] < o.elevation:
          print(f'File: {self.files[idx]} ignored due to elevation during observation: {metadata["EL-BEG"]}')
          continue # Skip files with insufficient elevation during observation
        else:
          # If all criteria are met, add the file and its metadata to the valid lists
          valid_files.append(self.files[idx])
          valid_metadata[len(valid_files) - 1] = metadata
      # If start or end time filters are specified, sort the valid files by their observation start time        
      if o.start or o.end:
        sorted_metadata = sorted(zip(valid_files, valid_metadata.values()), key=lambda x: x[1]['DATE-OBS'])
        valid_files, sorted_metadata = zip(*sorted_metadata)
        valid_metadata = {i: meta for i, meta in enumerate(sorted_metadata)}
      # Update the class attributes with the filtered lists of files and metadata
      self.files = list(valid_files)
      self.metadata = valid_metadata
      # Update file count and raise an error if no valid files are found 
      self.filecount = len(self.files)
      if self.filecount == 0:
        raise FileNotFoundError(f'No valid files with relevant data present, File Count: {self.filecount}')    
    except (FileNotFoundError, Exception) as e:
      # Handle errors that occur during file filtering
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith: {e}')
      quit()
    
  def HandleLoadData(self):
    # Handle the loading of data
    try:
      # Iterate over the list of valid FITS files
      for file in self.files:
        # Check if the file path is a valid file
        if not os.path.isfile(file):
          raise FileNotFoundError(f'File: {file} is not a file')
        # Check if the file has a '.fits' extension
        elif not file.endswith('.fits'):
          print(f'Warning: {file} is not a FITS file')
          continue # Ignore files that do not end with '.fits'
        else:
          # Load data from the FITS file
          frequency, channels, rhcp, lhcp = self.LoadFitsData(file)
          # Append the loaded data to the corresponding class attributes
          self.frequencies.append(frequency)
          self.channels.append(channels)
          self.rhcp.append(rhcp)
          self.lhcp.append(lhcp)
          # Increment the count of successfully processed files
          self.count += 1
      # Check if the number of processed files is less than 5        
      if len(self.files) < 5:
        print('Warning: Low file count, results may vary')
    except (FileNotFoundError, Exception) as e:
      # Handle errors
      print(f'Error: {e},\nOccured in: {sys._getframe().f_code.co_name},\nWith: {locals().get("file", "Unknown file")}.')
      quit()
            
  def LoadFitsData(self, file):
    # Load data
    try:
      # Open the FITS file
      with fits.open(file) as hdu:
        # Load data from the second HDU (hdu[1])
        data = Table(hdu[1].data)
      # Extract and process the 'frequency' column from the data
      frequency = data['frequency'] / 1e6 # Convert from Hz to MHz
      # Create an array of channel indicies based on the length of the frequency data
      channels = np.arange(len(data['frequency']))
      # Extract 'RHCPAVG' and 'LHCPAVG' data columns
      rhcp = data['rhcpavg']
      lhcp = data['lhcpavg']
      # Return the extracted data
      return frequency, channels, rhcp, lhcp
    except (Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : {file}.')
      quit()
          
  def LoadMetaData(self, file):
    # Load metadata
    time_differences = [] # List to store time differences between observation start and end times
    metadata = {}  # Dictionary to store extracted metadata
    try:
      # Open the FITS file
      with fits.open(file) as hdu:
        # Load metadata from the first HDU (hdu[0])
        header = hdu[0].header
        # Populate the metadata dictionary with values from the header
        metadata['file'] = file  # Path to the FITS file
        metadata['SAMPRATE'] = header['SAMPRATE']  # Sample rate
        metadata['FREQ'] = header['FREQ'] / 1e6  # Center frequency in MHz
        metadata['TELESCOP'] = header['TELESCOP']  # Telescope used
        metadata['OBJECT'] = header['OBJECT']  # Observed object
        metadata['RA'] = header['RA']  # Right Ascension
        metadata['DEC'] = header['DEC']  # Declination
        metadata['EL-BEG'] = header['EL-BEG']  # Elevation at the beginning of observation
        metadata['EL-END'] = header['EL-END']  # Elevation at the end of observation
        metadata['AZ-BEG'] = header['AZ-BEG']  # Azimuth at the beginning of observation
        metadata['AZ-END'] = header['AZ-END']  # Azimuth at the end of observation
        # Parse the observation start and end dates from the header
        metadata['DATE-OBS'] = datetime.strptime(header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S')
        metadata['DATE-END'] = datetime.strptime(header['DATE-END'], '%Y-%m-%dT%H:%M:%S')
        # Calculate the time difference between observation start and end
        time_difference = metadata['DATE-END'] - metadata['DATE-OBS']
        time_differences.append(time_difference)
      # Calculate the average observation time if there are any time differences 
      if time_differences:
        average_observation_time = sum(time_differences, timedelta(0)) / len(time_differences)
        average_observation_time_str = str(average_observation_time).split('.')[0]
        metadata['AVG-OBS'] = average_observation_time_str # Add average observation time to metadata
      else:
        # Raise an error if no valid time differences are found
        raise ValueError(f'Time differences: {time_differences}, are invalid or causing errors')  
      return metadata # Return the populated metadata dictionary
    except (ValueError, Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : {file}.')
      quit()
    
  def DebugFitsHandler(self):
    # Debug partially processed data
    print(f"FITSHandler Debug Output:")
    print(f"Directory: {self.directory}")
    print(f"Number of files: {len(self.files)}")
    print(f"Files: {self.files}")
    print(f"File Count: {self.filecount}")
    print(f"Count: {self.count}")
    print(f"Frequencies: {self.frequencies}")
    print(f"Channels: {self.channels}")
    print(f"Rhcp: {self.rhcp}")
    print(f"Lhcp: {self.lhcp}")
    print("Metadata:")
    # Access and print all metadata keys and values
    for key, value in self.metadata.items():
      print(f"{key}")
      print(f"{value}")
    print('Debugged FITSHandler, qutting program')
    quit()

class FITSSaver:
  # FITSSaver Constructor
  def __init__(self, fitsdata):
      self.fitsdata = fitsdata  # Store the FITS data object
      self.filename = os.path.basename(self.fitsdata.files[0])  # Extract the base filename from the first file  
  def SaveToFitsFile(self, regrid):
    try:
      # Determine the index of the last metadata entry
      finalvalue = len(list(self.fitsdata.metadata)) - 1
      # Create a new FITS Primary HDU (Header/Data Unit)
      pHDU = fits.PrimaryHDU()
      ph = pHDU.header  # Access the header of the primary HDU
      # Software Related Metadata
      ph['SW-VERS'] = (globals.PROGRAM_VERSION, "File created by software version")
      ph['SW-NAME'] = (globals.PROGRAM_NAME, "File created by software name")
      ph['DATE'] = (globals.CURRENT_DATE_TIME.strftime('%Y-%m-%dT%H:%M:%S'), "File creation date")
      # Observation Related Metadata
      ph['ORIGIN'] = (globals.ORIGIN_NAME, "Metsahovi Radio Observatory")
      ph['TELESCOP'] = (self.fitsdata.metadata[0]['TELESCOP'], "Telescope")
      ph['RA'] = (self.fitsdata.metadata[0]['RA'], "Right Ascension pointing (deg)")
      ph['DEC'] = (self.fitsdata.metadata[0]['DEC'], "Declination pointing (deg)")
      ph['EQUINOX'] = ("2000.0", "Equinox")
      ph['AVGINTEG'] = (self.fitsdata.metadata[0]['AVG-OBS'], "Average observation integration time")
      ph['OBJECT'] = (self.fitsdata.metadata[0]['OBJECT'], "Object")
      # Date Related Metadata
      ph['DATE-OBS'] = (self.fitsdata.metadata[0]['DATE-OBS'].strftime('%Y-%m-%dT%H:%M:%S'), "Observation start")
      ph['DATE-END'] = (self.fitsdata.metadata[int(finalvalue)]['DATE-END'].strftime('%Y-%m-%dT%H:%M:%S'), "Observation end")
      # Processing Related Metadata
      ph['SAMPRATE'] = (self.fitsdata.metadata[0]['SAMPRATE'], "Sample rate Hz")
      ph['NUMINPUT'] = (self.fitsdata.count, "Number of raw input files")
      ph['CHRANGE'] = (o.channels, "Range of channels to include in data processing")
      ph['POL'] = (o.polarization, "Polarization: R=Right, L=Left, B=Right+Left")
      ph['RESTFREQ'] = (o.rfreq, "Rest frequency [MHz]")
      ph['NUMBINS'] = (o.bins, "Number of re-grid bins")
      # Reference Related Metadata
      ph['TIMESYS'] = ("UTC", "Temporal Reference Frame")
      ph['REFFRAME'] = ('LSRK', "Reference Frame")
      # Define columns for velocity data
      velo_c1 = fits.Column(name='VELOCITY', format='E', array=regrid.velo_fr, unit='km/s')
      velo_c2 = fits.Column(name='AVG_POWER', format='E', array=regrid.average_vr, unit='ADU')
      velo_c3 = fits.Column(name='NUM_MEAS', format='E', array=regrid.count_vr)
      velo_c4 = fits.Column(name='SUM_POWER_AVG', format='E', array=regrid.sum_vr)
      # Define columns for frequency data
      freq_c1 = fits.Column(name='FREQUENCY', format='E', array=regrid.freq_fr, unit='MHz')
      freq_c2 = fits.Column(name='AVG_POWER', format='E', array=regrid.average_fr, unit='ADU')
      # Generate a filename with a timestamp and program stamp
      timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
      programstamp = 'calibrated'
      filename = f'{self.fitsdata.metadata[0]["OBJECT"]}_{timestamp}_{programstamp}.fits'
      # Create HDUs (Header/Data Units) for the velocity and frequency data
      self.velo_data = fits.BinTableHDU.from_columns([velo_c1, velo_c2, velo_c3, velo_c4], name='VELOCITY')
      self.freq_data = fits.BinTableHDU.from_columns([freq_c1, freq_c2], name='FREQUENCY')
      self.hdu = fits.HDUList([pHDU, self.velo_data, self.freq_data])
      # Output results
      print(f'Directory processed: {o.directory}')
      if o.output:
        self.hdu.writeto(f'{o.output}', overwrite=True) # Write to specified output file, overwrite if it exists
        print(f'Result saved as: {o.output}')     
        self.hdu.close() # Close the HDUList
      elif o.savedata:
        self.hdu.writeto(f'{filename}') # Write to generated filename
        print(f'Result saved as: {filename}')
        self.hdu.close() # Close the HDUList
      # Print data for debugging/testing purposes
      if o.printdata:
        self.LoadFitsFile()
      quit() # Exit the program after saving
    except (ValueError, IndexError, Exception) as e: 
      # Handle errors
      print(f'Error : {e},\nOccurred in : {sys._getframe().f_code.co_name},\nWith : {regrid}.') 
  def LoadFitsFile(self):
      self.hdu.info()  # Print information about the HDUList
      table_data = Table(self.hdu[1].data)  # Convert the second HDU (velocity data) to a Table
      print(table_data)  # Print the table data
      header = self.hdu[0].header  # Access the primary header
      print("Primary Header Metadata:")
      for key, value in header.items():  # Print all header items
          print(f"{key}: {value}")
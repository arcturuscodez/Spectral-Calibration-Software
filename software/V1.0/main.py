# Imports
import sys
import time
import plotting
import calibrations
import controller
import numpy as np
from options import o

# Main Module of the Spectral Calibration Software

class SpectralCalibrationSoftware:
  # SCS Class
  def __init__(self, directory):
    # Initialize the class with the directory where data is stored
    self.directory = directory
    # Create an instance of FITSHandler to manage FITS files in the specified directory
    self.fitsdata = controller.FITSHandler(self.directory) 
    # Initialize various calibration objects from the calibrations module
    # These objects will be used to perform different calibration tasks
    self.cut = calibrations.ChannelCalibration()
    self.pol = calibrations.PolarizationCalibration()
    self.median = calibrations.MedianCalibration()
    self.doppler = calibrations.VelocityCalibration(self.fitsdata)  # Pass FITSHandler instance for velocity calibration
    self.regrid = calibrations.RegridCalibration()
    # Call methods to perform initialization, processing, calibration, and utilization of data
    self.InitializeData()
    self.ProcessData()
    self.CalibrateData()
    self.UtilizeData()

  def InitializeData(self):
    # Initialize lists to hold data for frequency, channels, and polarization states
    # These lists will be populated with data during the processing stage
    self.frequency = [] # List to store frequency data
    self.channels = [] # List to store channel data
    self.rhcp = [] # List to store right-hand circular polarization data
    self.lhcp = [] # List to store left-hand circular polarization data

  def ProcessData(self):
    try:
      # Loop through all files in the FITS data
      for file in range(len(self.fitsdata.files)):
        # Append data from each FITS file to the corresponding list
        self.frequency.append(self.fitsdata.frequencies[file]) # Frequency data
        self.rhcp.append(self.fitsdata.rhcp[file]) # Right-hand circular polarization data
        self.lhcp.append(self.fitsdata.lhcp[file]) # Left-hand circular polarization data
        self.channels.append(self.fitsdata.channels[file]) # Channel data
      else:
        # After processing all files, convert lists to numpy arrays and slice them based on calibration
        self.frequency = np.array(self.frequency).T[self.cut.ch0:self.cut.ch1] # Transpose and slice frequency data
        self.channels = np.array(self.channels).T[self.cut.ch0:self.cut.ch1] # Transpose and slice channel data
        self.rhcp = np.array(self.rhcp).T[self.cut.ch0:self.cut.ch1] # Transpose and slice RHCP data
        self.lhcp = np.array(self.lhcp).T[self.cut.ch0:self.cut.ch1] # Transpose and slice LHCP data
        # Calculate and print the time taken to process the data
        self.processend = time.time() # End time of processing
        self.processtime = self.processend - self.fitsdata.process # Calculate processing time
        print(f"Time to process : {self.processtime:.4f}s") # Print processing time
      # Debug partially processed data if option is used
      if o.debug:
        self.fitsdata.DebugFitsHandler()
    except (FileNotFoundError, IndexError, Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : {self.fitsdata.files}.')

  def CalibrateData(self):
    try:
      # Perform polarization calibration using RHCP and LHCP data
      self.pol.Polarization(self.rhcp, self.lhcp) # Apply polarization calibration
      # Check if median calibration should be applied
      if o.median:
        self.median.Median(self.pol.ysignal) # Apply median calibration to the signal
      else:
        print('Warning: Median calibration was not utilized') # Warning if median calibration is not used
      # Apply Doppler velocity calibration using frequency data
      self.doppler.Velocity(self.frequency) # Perform velocity calibration
      # Perform regridding calibration
      self.regrid.Regrid(
        self.doppler.velocity, # Doppler-corrected velocity
        self.frequency, # Frequency data
        self.pol.ysignal, # Polarized signal
        self.fitsdata.count # FITS data count
      )
    except (ValueError, IndexError, Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : {self.ysignal}, {self.frequency}.')

  def UtilizeData(self):
    try:
      # Record the end time of the utilization process
      end = time.time()
      # Check if data should be saved or output
      if o.savedata or o.output:
        # Create a FITSSaver instance for saving FITS data
        self.save = controller.FITSSaver(self.fitsdata)
        # Save the regridded data to a FITS file
        self.save.SaveToFitsFile(self.regrid)
        # Print the time taken to save the data
        print(f"Time to save: {end - start:.4f}s")
      elif o.testrun:
        # If a test run is specified, print a message indicating successful processing
        print(f"Directory: {o.directory} was processed without errors")
        # Print the time taken for the test run
        print(f"Time to test: {end - start:.4f}s")
        # Stop the program after test run
        quit()
      else:
        # If no specific utilization option is used, plot the data
        print(f"Time to plot: {end - start:.4f}s")
        # Call PlotUI to generate and display plots
        plotting.PlotUI(
          self.fitsdata, # FITS data object
          self.regrid, # Regridded data
          self.doppler, # Doppler-corrected velocity
          self.frequency, # Frequency data
          self.channels, # Channel data
          self.pol.ysignal # Polarized signal
        )
    except (Exception) as e:
      # Handle errors
      print(f'Error : {e},\nOccured in : {sys._getframe().f_code.co_name},\nWith : Utilization of software')
      quit()

if __name__ == "__main__":
  try:
    # Check if a directory is provided through the options
    if o.directory:
      # Record the start time before initializing the software
      start = time.time()
      # Create an instance of SpectralCalibrationSoftware with the provided directory
      SpectralCalibrationSoftware(o.directory)
    else:
      # Raise an error if no directory is provided
      raise ValueError('Software missing commands, please use -h for help') 
  except (ValueError) as e: 
    # Handle errors
    print(f'Error : {e},\nOccured in : Spectral Calibration Software {sys._getframe().f_code.co_name},\nWith : Running software')
    quit()
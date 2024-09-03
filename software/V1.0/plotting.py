# Imports
import matplotlib.pyplot as plt
import os
import globals
from datetime import datetime
from options import o

class PlotUI:
  # Class to handle plotting of data using matplotlib
  def __init__(self, fitsdata, regrid, doppler, frequency, channels, ysignal):
    # Initialize the attributes with provided parameters
    self.fitsdata = fitsdata  # FITS data object containing metadata and data
    # Set the figure size if enabled by options
    self.figx, self.figy = o.figsize.split(':')
    self.figx, self.figy = int(self.figx), int(self.figy)
    self.fig, self.axes = plt.subplots(figsize=(self.figx,self.figy))
    # Set the label size for plot labels, capped at 25
    self.labelsize = min(25, 35 / (2 + 1))
    self.regrid = regrid  # RegridCalibration object
    self.doppler = doppler  # Doppler object (assumed to handle Doppler corrections)
    self.frequency = frequency  # Frequency data
    self.channels = channels  # Channels data
    self.ysignal = ysignal  # Signal data
    self.symbol = '-'  # Default line style for plots
    # Set up the plots with basic configurations
    self.PlotSetup()
    # Plot the actual data
    self.PlotData()
      
  def PlotSetup(self):
    # Adjust the top margin of the plot
    plt.subplots_adjust(top=0.92)
    # Adjust the spacing between subplots
    plt.subplots_adjust(hspace=0.3)
    # If grid option is enabled, add grid lines to each axis
    if o.grid:
      for ax in self.axes:
        ax.grid(True)
    # If subplot labels option is enabled, add labels to subplots
    if o.subplotlabel:
      for i, ax in enumerate(self.axes.flatten()):
        # Add label (a, b) to the top-right corner of each subplot
        ax.text(0.985, 0.955, str('(') + (chr(ord('a') + i)), transform=ax.transAxes, fontsize=14)
    
  def PlotData(self):
  # Main method to plot the data based on various conditions
    def PlotFeatures(ax, x, y, title, xlabel, ylabel):
      # Helper function to plot features on a given axis
      ax.plot(x, y)  # Plot x vs. y on the provided axis
      ax.set_title(title)  # Set the title of the plot
      ax.set_xlabel(xlabel)  # Set the x-axis label
      ax.set_ylabel(ylabel)  # Set the y-axis label  
    def PlotSupTitle():
      # Helper function to generate and set the super title for the figure
      first = None
      last = None
      objectname = None
      # Iterate over FITS files to determine the date range and object name
      for file in self.fitsdata.files:
        if file.endswith('.fits'):
          base_name = os.path.basename(file)
          split = base_name.split('_')[1]
          date = datetime.strptime(split, '%Y%m%d')
          if first is None or date < first:
            first = date  # Update the earliest date
          if last is None or date > last:
            last = date  # Update the latest date
          if objectname is None:
            objectname = base_name.split('_')[0]  # Extract the object name  
      # Format the date range for the super title
      if first == last:
        plotdate = first.strftime('%Y-%m-%d')
      else:
        plotdate = f"{first.strftime('%Y-%m-%d')} -> {last.strftime('%Y-%m-%d')}"  
      # Create and set the super title for the figure
      supertitle = f"{objectname.upper()}, {plotdate}"
      self.fig.suptitle(supertitle, fontsize=17, fontweight='bold')
    # Call the function to set the super title
    PlotSupTitle()
    # Plot regridded velocity data if the option is enabled
    if o.regridveloplot:
      PlotFeatures(self.axes,
        x=self.regrid.velo_fr,
        y=self.regrid.average_vr,
        title=None,
        xlabel=r'Gridded velocity, $v_\mathrm{LSRK}$ [km s$^{-1}$]',
        ylabel='Power [ADU]')
    elif o.regridfreqplot:
      # Plot regridded frequency data if the option is enabled
      PlotFeatures(self.axes,
        x=self.regrid.freq_fr,
        y=self.regrid.average_fr,
        title=None,
        xlabel='Gridded frequency [MHz]',
        ylabel='Power [ADU]')
    elif o.sumvrplot:
      # Plot cumulative average velocity data if the option is enabled
      PlotFeatures(self.axes,
        x=self.regrid.sum_vr,
        y=self.symbol,
        title=None,
        xlabel='Cumulative velocity average',
        ylabel='Power [ADU]')
      # Plot cumulative average frequency data if the option is enabled
    elif o.sumfrplot:
      PlotFeatures(self.axes,
        x=self.regrid.sum_fr,
        y=self.symbol,
        title=None,
        xlabel='Cumulative frequency Average',
        ylabel='Power [ADU]')
    elif o.veloplot:
      # Plot Doppler-corrected velocity data if the option is enabled
      PlotFeatures(self.axes,
        x=self.doppler.velocity,
        y=self.ysignal,
        title=None,
        xlabel=r'Velocity, $v_\mathrm{LSRK}$ [km s$^{-1}$]',
        ylabel='Power [ADU]')
    elif o.freqplot:
      # Plot frequency data if the option is enabled
      PlotFeatures(self.axes,
        x=self.frequency,
        y=self.ysignal,
        title=None,
        xlabel='Frequency [MHz]',
        ylabel='Power [ADU]')
    elif o.chanplot:
      # Plot channel data if the option is enabled
      PlotFeatures(self.axes,
        x=self.channels,
        y=self.ysignal,
        title=None,
        xlabel=f'Channels [{o.channels}]',
        ylabel='Power [ADU]')
    elif o.binplot:
      # Plot bin count data if the option is enabled
      PlotFeatures(self.axes,
        x=self.regrid.count_vr,
        y=self.symbol,
        title=None,
        xlabel='Bin number',
        ylabel='Number of measurements')
    else:
      # If no valid plot option is selected, clear the axis and show a message
      self.axes.cla()  # Clear the axis
      self.axes.text(0.5, 0.5, 'Data not plotted', ha='center', va='center', fontsize=12, color='red') # Print a data not plotted message
      self.axes.axis('off')  # Turn off the axis
    # Plot metadata if the option is enabled
    if o.plotmetadata:
      self.PlotMetaData()
    # Display the plot
    plt.show()
      
  def PlotMetaData(self):
      # Method to plot metadata information on the figure
      # Get the final index of the metadata
      finalvalue = len(list(self.fitsdata.metadata)) - 1
      # Retrieve relevant metadata information from the FITS data
      telescope = self.fitsdata.metadata[0]['TELESCOP']
      samplerate = self.fitsdata.metadata[0]['SAMPRATE']
      avgintegrate = self.fitsdata.metadata[0]['AVG-OBS']
      startdate = self.fitsdata.metadata[0]['DATE-OBS']
      enddate = self.fitsdata.metadata[int(finalvalue)]['DATE-END']
      # Determine the polarization type based on user input
      if o.polarization == 'b' or o.polarization == 'B':
        pol = 'RHCP+LHCP'  # Both Right Hand Circular Polarization and Left Hand Circular Polarization
      elif o.polarization == 'r' or o.polarization == 'R':
        pol = 'RHCP'  # Right Hand Circular Polarization
      elif o.polarization == 'l' or o.polarization == 'L':
        pol = 'LHCP'  # Left Hand Circular Polarization
      else:
        pol = None  # No polarization specified or error occured
      # Software-related information to display in the metadata
      software = f'''
      Program name: {globals.PROGRAM_NAME}
      Program version: {globals.PROGRAM_VERSION}
      Plot creation date: {datetime.now()}
      Directory: {o.directory}
      '''
      # Metadata information related to the observation and data
      metadata = f'''
      File count: {self.fitsdata.count}
      Telescope: {telescope}
      Sample rate: {samplerate}
      Channel range: {o.channels}
      Number of bins: {o.bins}
      Polarization: {pol}
      Observation start: {startdate}
      Observation end: {enddate}
      Average integration time: {avgintegrate} (HH:MM:SS)
      Centre frequency range: {o.cfreq} MHz
      Rest frequency: {o.rfreq} MHz
      '''
      # Add the software information text to the figure at the specified position
      self.fig.text(0.15, 0.001, software, fontsize=8)
      # Add the metadata information text to the figure at the specified position
      self.fig.text(0.001, 0.001, metadata, fontsize=8)
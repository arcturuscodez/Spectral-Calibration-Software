# Imports
import numpy as np
import sys
import globals
import astropy.units as u
from options import o
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, ICRS, LSRK, solar_system_ephemeris
from astropy import constants as const
solar_system_ephemeris.set('de432s')

class ChannelCalibration:
  # Class to handle channel calibration based on input options
  def __init__(self):
    # Extract the channel range from the options
    self.ch0, self.ch1 = o.channels.split(':')
    # If channels option is specified, set the channels
    if o.channels:
      self.SetChannels()  
  # Method to validate and set the channel range
  def SetChannels(self):
    try:
      # Convert channel range to integers
      self.ch0, self.ch1 = int(self.ch0), int(self.ch1)
      # Validate the channel range
      if self.ch0 < 0:
          raise ValueError(f'CH0 Value is invalid: {self.ch0}')  # CH0 should not be negative
      elif self.ch1 <= self.ch0:
          raise ValueError(f'CH1 Value is invalid: {self.ch1}, Cannot be less than CH0')  # CH1 should be greater than CH0
      elif self.ch1 >= 4097:
          raise ValueError(f'CH1 Value is too large: {self.ch1}, Minimum: 4096')  # CH1 should be within a valid range (less than 4097)
    except (ValueError, Exception) as e: 
      # Handle errors
      print(f'Error: {e},\nOccurred in: {sys._getframe().f_code.co_name},\nWith: {o.channels}.')
      quit()
   
class PolarizationCalibration:
  # Class to handle polarization calibration
  def __init__(self):
    # Initialize polarization value from options and convert to uppercase
    self.polarization = str(o.polarization).upper()
    self.pol_string = ''  # Initialize polarization string to empty
  def Polarization(self, rhcp, lhcp):
    # Define a dictionary to map polarization types to corresponding descriptions and functions
    polarization_map = {
      'R': ('Right Hand Polarization', lambda: rhcp),  # Right Hand Circular Polarization
      'L': ('Left Hand Polarization', lambda: lhcp),   # Left Hand Circular Polarization
      'B': ('Right and Left Hand Polarization', lambda: np.array((
          (lhcp - np.min(lhcp)) / (np.max(lhcp) - np.min(lhcp)),  # Normalize LHCP
          (rhcp - np.min(rhcp)) / (np.max(rhcp) - np.min(rhcp))   # Normalize RHCP
      )))
    }
    try:
      if self.polarization == 'B':
          # If polarization is 'B', combine both LHCP and RHCP
          _, ysignal = polarization_map[self.polarization]
          ysignal = ysignal()  # Get combined signal
          ysignal = np.add.reduce(ysignal, axis=0)  # Sum the signals along the first axis
          self.ysignal = ysignal
      elif self.polarization != 'B':
          # If polarization is not 'B', use the corresponding signal
          _, ysignal = polarization_map[self.polarization]
          ysignal = ysignal()  # Get the signal
          self.ysignal = ysignal
      elif o.polarization is None:
          # If no polarization is specified, default to RHCP
          _ = 'Right Hand Polarization'
          ysignal = rhcp
          self.ysignal = ysignal
      else:
          # If an invalid polarization is provided, print an error and exit
          print('Invalid polarization argument, Please use -h to see proper arguments.')
          quit()
    except (Exception) as e: 
      # Handle errors
      print(f'Error: {e},\nOccurred in: {sys._getframe().f_code.co_name},\nWith: {self.polarization}.')
      quit()
        
class MedianCalibration:
    # Class to handle the median calibration
    def __init__(self):
      # Initialize an empty list to store spectra
      self.spectra = []
    def Median(self, ysignal):
      try:
        # Subtract the mean of ysignal to center the data
        ysignal -= np.mean(ysignal, axis=0)
        # Append the centered ysignal to the spectra list
        self.spectra.append(ysignal)
        # Convert the spectra list to a NumPy array
        self.spectra_array = np.array(self.spectra)
        # Calculate the median of the spectra array
        self.median = np.median(self.spectra_array, axis=2)
        # Subtract the median (transposed) from the ysignal to remove median
        ysignal -= self.median.T
      except (Exception) as e: 
        # Handle errors
        print(f'Error: {e},\nOccurred in: {sys._getframe().f_code.co_name},\nWith: {self.spectra}.')
        quit() 

class VelocityCalibration:
    # Class to handle the velocity calibration
    def __init__(self, fitsdata):
      # Initialize an empty list to store velocity data
      self.velocity = []
      # Store the input FITS data
      self.fitsdata = fitsdata
      # Extract telescope name from FITS metadata
      self.telescope = self.fitsdata.metadata[0]['TELESCOP']
      # Extract right ascension (RA) from FITS metadata
      self.ra = self.fitsdata.metadata[0]['RA']
      # Extract declination (DEC) from FITS metadata
      self.dec = self.fitsdata.metadata[0]['DEC']
      # Retrieve telescope properties (latitude, longitude, height) from globals
      self.properties = globals.MCA_TELESCOPE_VALUES.get(self.telescope, None)
      self.latitude = self.properties['latitude']
      self.longitude = self.properties['longitude']
      self.height = self.properties['height']
      # Create EarthLocation object using telescope's geographic coordinates
      self.telescopelocation = EarthLocation.from_geodetic(lat=self.latitude,
                                                           lon=self.longitude,
                                                           height=self.height)    
      # Parse channel range from input options and calculate channel count
      ch0, ch1 = map(int, o.channels.split(':'))
      self.chancount = ch1 - ch0
    def Velocity(self, frequency):
      try:
        # Iterate over each file's metadata in the FITS data
        for file, metadata in self.fitsdata.metadata.items():
          # Convert observation start and end times to Time objects
          start_utc = Time(metadata['DATE-OBS'])
          stop_utc = Time(metadata['DATE-END'])
          # Calculate the mid-point of the observation time
          mid_utc = (stop_utc - start_utc) / 2 + start_utc
          # Create a SkyCoord object for the target coordinates (RA, DEC)
          sc = SkyCoord(self.ra * u.deg, self.dec * u.deg, frame='icrs')
          # Calculate the barycentric radial velocity correction for the mid observation time and telescope location
          barycentric = sc.radial_velocity_correction(kind='barycentric', obstime=mid_utc, location=self.telescopelocation)
          # Create an ICRS object with the barycentric radial velocity correction
          icrs = ICRS(sc.ra, sc.dec, pm_ra_cosdec=0 * u.mas / u.yr, pm_dec=0 * u.mas / u.yr, radial_velocity=barycentric, distance=1 * u.pc)
          # Transform the ICRS object to the LSRK frame to get the relative velocity
          relative_velocity = icrs.transform_to(LSRK()).radial_velocity
          # Convert the observed frequency to MHz
          observed_frequency = np.array([frequency]) * u.MHz
          # If a rest frequency is specified in the options, use it; otherwise, it defaults to None
          if o.rfreq:
              rest_frequency = o.rfreq * u.MHz
          # Calculate the Doppler shift (dr2) for the observed and rest frequencies
          dr2 = (observed_frequency / rest_frequency) ** 2
          # Calculate the observed velocity using the Doppler formula
          observed_velocity = const.c * (1 - dr2) / (1 + dr2)
          # Calculate the LSRK velocity by adding the relative velocity to the observed velocity
          vlsrk = observed_velocity + relative_velocity
          # Initialize an empty array for the velocities in km/s
          xvelo = np.array([]) * u.km / u.s
          # Append the LSRK velocities to the velocity array
          xvelo = np.append(xvelo, vlsrk)
          # Reshape the velocity array to match the number of channels and FITS data count
          self.velocity = xvelo.reshape((self.chancount, self.fitsdata.count))
      except (Exception) as e:
          # Handle errors
          print(f'Error: {e},\nOccurred in: {sys._getframe().f_code.co_name},\nWith: {frequency}.')
          quit()
            
class RegridCalibration:
  # Class to handle the re-grid calibration  
  def __init__(self):
    # Initialize sum_ch to None; it will store the sum of all y arrays
    self.sum_ch = None
    # Set the number of frequency and velocity bins from options, if specified
    if o.bins:
        self.num_freq, self.num_velo = o.bins, o.bins
    # Initialize the minimum and maximum frequency and velocity values
    self.min_freq = float('inf')
    self.max_freq = float('-inf')
    self.min_velo = float('inf')
    self.max_velo = float('-inf')
    # Initialize arrays to store the sum and count for frequency and velocity
    self.sum_fr = np.zeros(self.num_freq)
    self.sum_vr = np.zeros(self.num_velo)
    self.count_fr = np.zeros(self.num_freq, dtype=int)
    self.count_vr = np.zeros(self.num_velo, dtype=int)
    # Initialize variables to store the average frequency and velocity
    self.average_fr = None
    self.average_vr = None
    
  def MinMaxRange(self, x_v, x_f):
    # Calculate the minimum and maximum values for frequency and velocity from the input arrays
    get_min_freq, get_max_freq = np.min(x_f), np.max(x_f)
    get_min_velo, get_max_velo = np.min(x_v), np.max(x_v)
    # Update the class attributes to reflect the overall min and max values
    self.min_freq = min(self.min_freq, get_min_freq)
    self.max_freq = max(self.max_freq, get_max_freq)
    self.min_velo = min(self.min_velo, get_min_velo)
    self.max_velo = max(self.max_velo, get_max_velo)
    # Create evenly spaced arrays for frequency and velocity based on the min and max values
    self.freq_fr = np.linspace(self.min_freq, self.max_freq, self.num_velo)
    self.velo_fr = np.linspace(self.min_velo, self.max_velo, self.num_velo)
    
  def Regrid(self, x_v, x_f, y, filecount):
    try:
      # Initialize count to 0 for the first iteration
      count = 0
      # Update the min and max ranges for frequency and velocity
      self.MinMaxRange(x_v, x_f)
      # If this is the first iteration, copy y to sum_ch; otherwise, add y to sum_ch
      if count == 0:
        self.sum_ch = np.copy(y)
      else:
        self.sum_ch += y
      # Loop over the frequency channels in y
      for fch in range(len(y)):
        # Find the index in freq_fr where x_f[fch] should be inserted
        ffi = np.searchsorted(self.freq_fr, x_f[fch])
        # Update the sum and count arrays for frequency
        self.sum_fr[ffi] += y[fch]
        self.count_fr[ffi] += 1
      # Loop over the velocity channels in y
      for vch in range(len(y)):
        # Find the index in velo_fr where x_v[vch] should be inserted
        vfi = np.searchsorted(self.velo_fr, x_v[vch])
        # Update the sum and count arrays for velocity
        self.sum_vr[vfi] += y[vch]
        self.count_vr[vfi] += 1
      # Initialize an array to store the average values for channels
      average_ch = np.zeros_like(len(self.sum_ch))
      # Calculate the average values for channels
      for i in range(average_ch):
        average_ch[i] = self.sum_ch[i] / filecount
      # Suppress warnings for division by zero and invalid values
      with np.errstate(divide='ignore', invalid='ignore'):
        # Calculate the average frequency and velocity by dividing the sum by the count
        self.average_fr = np.divide(self.sum_fr, self.count_fr) 
        self.average_vr = np.divide(self.sum_vr, self.count_vr)
    except (Exception) as e:
      # Handle errors
      print(f'Error: {e},\nOccurred in: {sys._getframe().f_code.co_name},\nWith: {x_v}, {x_f}, {y}.')
      quit()
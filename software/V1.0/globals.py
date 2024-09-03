import astropy.units as u
from datetime import datetime

#Global variables unaffected by the software.

PROGRAM_NAME='Spectral Calibration Software'
PROGRAM_DESCRIPTION='Software used to calibrate spectral signals'
ORIGIN_NAME='Metsahovi'
PROGRAM_VERSION='1.0'
PROGRAM_CREATION_DATE='2024-08-01'
CURRENT_DATE_TIME=datetime.utcnow()
MCA_TELESCOPE_VALUES={
  'MAINANT':{
      'latitude':60.21780915277778*u.deg,
      'longitude':24.39311053055556*u.deg,
      'height':79.191*u.m
    },
  'MCA1':{
      'latitude':60.217366760*u.deg,
      'longitude':24.391763697*u.deg,
      'height':50*u.m
    },
  'MCA2':{
      'latitude':60.217493090*u.deg,
      'longitude':24.391763697*u.deg,
      'height':71.4*u.m    
    },
  'MCA3':{
      'latitude':None,
      'longitude':None,
      'height':None    
    },
  'MCA4':{
      'latitude':None,
      'longitude':None,
      'height':None    
    }
}
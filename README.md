# Spectral Calibration Software

<img src="https://www.metsahovi.fi/opendata/img/mhlogo.png" alt="Project Logo" width="200"/>

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Contact](#contact)

## Introduction
This software is developed to process and calibrate spectral data, specifically astrophysical maser emission data.

The software was developed during a thesis project for the developer's bachelor's degree.

The thesis can be viewed at this link : https://urn.fi/URN:NBN:fi:amk-2024090524798

The software is currently used by Metsähovi Radio Observatory for the calibration and isolation of astrophysical maser emissions.

## Features
- Process Spectral Data
- Calibrate Spectral Data
- Visualize Processed/Calibrated Spectral Data as Figures
- Output Processed/Calibrated Spectral Data as new FITS files

## Installation

### Prerequisites
- NumPy
- Astropy
- Matplotlib
- Python 3.8

### Steps

Note: These steps are only relevant for students at Aalto or Metsähovi Radio Observatory who have access to the GitLab. Otherwise clone and run the software in your personal environment as you would normally from this repository.

1. Clone the repository:
   ```sh
   git clone git@version.aalto.fi:student-projects/spectral-calibration.git
   cd /spectral-calibration/thesis_project/main/V1.0/
2. Run the software:
    ```sh
    /spectral-calibration/thesis_project/main/V1.0/python3 main.py -d "directory" -m -c 290:3800 -p b --sv 

## Configuration

Options can be viewed below, or in software through the use of -h

1.  Options Available 
    ```sh
    Usage: main [-option] <directory>

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit

      Directory options:
        Options for specifying the directory or filtering contained files

        -d <directory>, --directory=<directory>
                            Specify a directory path to utilize and process in the
                            software

      Filtering options, Options for filtering files based on specified rules:
        --fc=Lower:Upper [MHz], --centrefreqrange=Lower:Upper [MHz]
                            Set a specified centre frequency range or value to
                            process, Ex: 6668.5192:6669.5192 (Include specific
                            range), 0:9000 (Include all below 9000), 4000:0
                            (Include all above 4000)
        -t MCA2, --telescope=MCA2
                            Select files to process based on the observing
                            telescope, Ex: MCA1, MCA2, MAINANT
        -s 2024-03-06T17:00:04 [YYYY:MM:DDTHH:MM:SS], --starttime=2024-03-06T17:00:04 [YYYY:MM:DDTHH:MM:SS]
                            Define a starting date and time of which files to
                            process, Ex: 2020-03-06T17:00:04
        -e 2024-03-06T00:00:04 [YYYY:MM:DDTHH:MM:SS], --endtime=2024-03-06T00:00:04 [YYYY:MM:DDTHH:MM:SS]
                            Define a ending date and time of which files to
                            process, Ex: 2024-03-06T19:00:04
        --el=50, --elevation=50
                            Exclude files which are observed with an elevation
                            less than this value, Ex. 50, 40, 5

      Plotting options:
        Various options for processing functionality

        -c CH:CH, --channels=CH:CH
                            Set the range of channels to process, Ex: 350:3500
        -p r, R, l, L, b, B, --polarization=r, R, l, L, b, B
                            Specify the polarization to process, Ex: (r, R =
                            Right) (l, L = Left) (b, B = Both)
        --fr=6668.5192 [MHz], --restfreq=6668.5192 [MHz]
                            Specify the rest frequency to calculate the velocity
                            data on, Ex: 6668.5192
        -b 500, --bins=500  Define the total channels(bins) to re-grid frequency &
                            velocity data into, Ex: 500, 750, 5000
        -m, --median        Enable a median calculation and remove the result from
                            the signal data
        --fig=X:Y, --figuresize=X:Y
                            Set the size of the figure, Ex. 20:10

      Axes options:
        Options for selecting data to plot in subplot 2

        --RV, --byregridvelo
                            Plot using regridded velocity data
        --RF, --byregridfreq
                            Plot using regridded frequency data
        --sumv, --bysumvr   Plot the sum of regridded velocity
        --sumf, --bysumfr   Plot the sum of regridded frequency
        -V, --byvelocity    Plot using base velocity data (without regridding)
        -F, --byfrequency   Plot the base frequency data (without regridding)
        -C, --bychannels    Plot total channel count (unaffected by -c/--channels)
        -B, --bybins        Plot total frequency bins contributing to the
                            regridding

      Utility options:
        Miscellaneous utility options

        --gr, --plotgrid    Enable a grid for both subplots on the figure
        --md, --plotmetadata
                            Display metadata on the figure
        --dbg, --debug      Debug and print relevant information from loaded FITS
                            files
        --sub, --subplot    Add subplot labels to the subplots
        --test, --testrun   Run the program without plotting or saving

      File Saving options:
        Options for saving data to a FITS file

        --sv, --savedata    Save the processed data to a FITS file
        --pr, --print       Print the newly saved processed data to the terminal
        -o output.fits, --output=output.fits
                            Save the processed data to a user defined FITS file,
                            Ex: testfile, maser, G232

## Contributing

Sonny Holman (Developer), Derek McKay (Supervisor)

## Contact

### Email

sonnyholman@hotmail.com


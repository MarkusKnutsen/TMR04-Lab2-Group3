from apread import APReader
import scipy as sp
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import os
sns.set_context("paper")
sns.set_theme(style="darkgrid", palette="bright")

# 0   Channel "Time  1 - default sample rate" (9495 Entries)
# 1   Channel "1X" (9495 Entries)
# 2   Channel "1Y" (9495 Entries)
# 3   Channel "2X" (9495 Entries)
# 4   Channel "2Y" (9495 Entries)
# 5   Channel "3X" (9495 Entries)
# 6   Channel "3Y" (9495 Entries)
# 7   Channel "UL_WaterLevel" (9495 Entries)
# 8   Channel "Position" (9495 Entries)
# 9   Channel "Speed" (9495 Entries)

# Function for reading in the data from the .BIN files in directory of choosing


def read_bin(directory):
    reader = []
    for root, dirs, files in os.walk(directory):
        for filename in sorted(files):
            reader.append(APReader(os.path.join(root, filename)))
    return reader

# Function to filter the noise from the signal. The value of 50 is visually chosen, such that the noise is gone and the data is intact


def gauss_filter(data, sigma=50):
    gauss_filtered_signal = sp.ndimage.gaussian_filter1d(data, sigma)
    return gauss_filtered_signal

# Function to collect all the necessary variables for the plotting


def data_collecting_function(run, sensor):
    # Using the end time of the run to select the period. (Channel[0] is time, check the top of the code file)
    sample_period = run.Channels[0].data.max()
    # Using the time-channel to find out how many entries of data we have
    samples = run.Channels[0].length
    # Calculating the sample frequency of the run
    sample_fq = samples / sample_period
    # The x-axis will represent the number of sample points. to find the time, one could divide with the sample frequency
    x_axis = np.linspace(0, samples, samples)
    # The sensor variable, initialized on the top of the code file, selects the channel and gives the data. This code is for the Speed
    data = run.Channels[sensor].data
    # The name for use in the plot
    name = run.Channels[sensor].Name
    # The name of the file
    filename = run.fileName
    # Returns the filtered data
    f1 = gauss_filter(data)
    # Return the filtered speed data
    speed = gauss_filter(run.Channels[9].data)

    return (sample_fq, samples, sample_fq, x_axis, data, name, filename, f1, speed)

# Function to find the amplitude data from the oscillatory data


def peak_finder(data, h, prom, dist):
    # First the data is selected, for both the natural values, but also with a flipped sign. This is to collect the negative amplitudes
    # For this function, the positive data is in position 0, and the negative data in position 1
    amplitudes = [data.copy(), -(data.copy())]

    # Finding the peak indices
    peaks = [sp.signal.find_peaks(amplitudes[0], height=h, prominence=prom, distance=dist)[
        0], sp.signal.find_peaks(amplitudes[1], height=h, prominence=prom, distance=dist)[0]]

    # Initialazing the vector that will just contain the amplitudes, as to preform calculations on them
    amp_val = [[], []]

    # Initializing the vector containing the mean data of the amplitudes
    mean_amp = [0, 0]

    # Initializing the vector containing the maximum data of the amplitudes
    max_amp = [0, 0]

    # Used in the for loop to know what sign is being used
    signs = [0, 1]

    # Variable used for keeping track of the last peak that was investigated in the foor loop
    last_peak = 0

    # Iterating through the signs
    for sign in signs:

        # Iterating through the peak indices
        for peak in peaks[sign]:

            # The values between peaks are set to None, so that only the peaks show up in plots
            amplitudes[sign][last_peak+1:peak-1].fill(None)

            # Append the amplitude to the vector that will be used for calculations on the amplitudes. This cannot be done with elements that are 'None'
            amp_val[sign].append(amplitudes[sign][peak])

            # Updating the value for 'last_peak'
            last_peak = peak

        # amplitudes[sign][amplitudes[sign] == 0] = None
        # Calcuating the mean and the maximum values from the amplitudes
        mean_amp[sign] = np.array(amp_val[sign]).mean()
        max_amp[sign] = np.array(amp_val[sign]).max()

        # Returns the vector of amplitude data
    return [amplitudes[0], -amplitudes[1], mean_amp[0], -mean_amp[1], max_amp[0], -max_amp[1]]

# --- Amplitude Data Indices---
#   0 - Positive amplitudes vector. Used for plotting
#   1 - Negative amplitudes vector. Used for plotting
#   2 - Mean of the positive amplitudes
#   3 - Mean of the negative amplitudes
#   4 - Maximum of the positive amplitudes
#   5 - Minimum of the negative amplitudes
# -----------------------------


# Reading in the data
directory = './bin'
reader = read_bin(directory)

# The transverse data is the data in Y-direction. This data contains minimal noise and will not be filtered
transverse_sensors = [2, 4, 6]
# The inline data is the data in X-direction. This data contains noise and will be filtered
inline_sensors = [1, 3, 5, 8, 9]

sensors = [4]

# Iterating through the runs
for run in reader:
    for sensor in sensors:
        (sample_fq, samples,  sample_fq, x_axis, data,
         name, filename, f1, speed) = data_collecting_function(run, sensor)
        print(np.array(np.abs(data)).mean()*3)
        # Collecting the amplitude data
        amp_data = peak_finder(data, 1, np.array(np.abs(data)).mean()*3, None)

        # Plotting the peaks
        # plt.plot(x_axis[1900:12480], amp_data[0][1900:12480], 'ro')
        plt.plot(x_axis[1900:12480], -amp_data[1][1900:12480], 'bo')
        plt.plot(x_axis[1900:12480], -data[1900:12480], color='goldenrod')
        plt.plot(x_axis[1900:12480], speed[1900:12480], color='red')

        plt.hlines(amp_data[2], 1900, 12480)
        plt.hlines(amp_data[3], 1900, 12480)
        plt.title(name + ' Mean+ =' + str(np.round(amp_data[2], 3)) +
                  ', Mean- =' + str(np.round(amp_data[3], 3)) + ', Max =' + str(np.round(amp_data[4], 3)) + ', Min =' + str(np.round(amp_data[5], 3)) + ' ' + filename)
        plt.legend()
        plt.show()

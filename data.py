from apread import APReader
import scipy as sp
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import os
sns.set_context("paper")
sns.set_theme(style="darkgrid", palette="bright")

# Data for the cylinder used in the experiment
D1 = 0.029
D2 = 0.025
D3 = 0.032

diameter = [0, D1, D1, D2, D2, D3, D3, 0, 0, 0]

speed_levels = [0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.80, 0.80, 0.80, 0.80, 0.80, 0.8, 0.9, 1, 1.1, 1.15, 1.2, 1.3, 1.4, 1.5]

Re = [10000,12500,15000,16250,17500,18750,20000,20000,20000,20000,20000,21250,22500,25000,27500,28750,30000,32500,35000,37500]

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
    amplitudes = [data, -(data)]

    # Finding the peak indices
    peaks = [sp.signal.find_peaks(amplitudes[0], height=h, prominence=prom, distance=dist)[
        0], sp.signal.find_peaks(amplitudes[1], height=h, prominence=prom, distance=dist)[0]]
    
    print('PEAKS:', peaks[0][:20])

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

    plt.plot(amplitudes[0], 'ro')
    plt.title("Positive")
    plt.show()
    plt.plot(-amplitudes[1], 'bo')
    plt.title("Negative")
    plt.show()

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

# Sensors that we want to investigate
sensors = [4]

# Indices ues for the 2Y data. Data selected to remove the transient information
Y2 = [[3400, 11200], [3200, 9200], [3200, 8400], [3100, 7600], [3700, 7700], [3300, 7100], [3800, 6700], [3200, 6700], [4000, 7300], [3700, 7000], [3500, 6800], [3500, 5600], [3400, 6400], [4000, 5900], [3340, 5730], [4160, 5550], [4440, 5500], [4830, 5400], [3770, 4850], [3750, 4920]]

# List containing the index data
indices = [0, 0, 0, 0, Y2, 0, 0, 0, 0, 0]

# List for storing the largest forces
max_forces = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# List for storing the strouhal number
St = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
St2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Variable to keep track of the runs. rc stands for run counter
rc = 0

# Will comment the code tomorrow.

for run in reader:
    for sensor in sensors:

      s = indices[sensor]

      start = s[rc][0]
      end = s[rc][1]

      (sample_fq, samples,  sample_fq, x_axis, data, name, filename, f1, speed) = data_collecting_function(run, sensor)

      signal = gauss_filter(data[start:end], 4)

      m = 200

      vec_pos = []
      vec_neg = []
      for elem in signal:
          if elem < 0:
              vec_pos.append(0)
              vec_neg.append(elem)
          if elem >= 0:
              vec_pos.append(elem)
              vec_neg.append(0)
      mean_pos = np.round(np.array(vec_pos).mean(), 3)
      mean_neg = -np.round(np.array(vec_neg).mean(), 3)

      vec_neg = np.copysign(vec_neg, 1)

      added_signal = [value+m for value in signal]
      manipulated_signal = [(value*(-1))+m for value in signal]

      pos_peaks = sp.signal.find_peaks(added_signal, height=m*0.25, distance=30)[0]
      neg_peaks = sp.signal.find_peaks(manipulated_signal, height=m*0.25, distance=30)[0]

      pos_amplitude = [None]
      neg_amplitude = [None]

      vec_neg = np.copysign(vec_neg, -1)

      last_peak = 0
      for peak in pos_peaks:
        pos_amplitude.extend([None]*(peak-last_peak-1))
        if vec_pos[peak] > 0: pos_amplitude.append(vec_pos[peak])
        else: pos_amplitude.append(vec_neg[peak])
        last_peak = peak
      pos_amplitude.extend([None]*((end - start) - len(pos_amplitude)))

      last_peak = 0
      for peak in neg_peaks:
        neg_amplitude.extend([None]*(peak-last_peak-1))
        if vec_neg[peak] < 0: neg_amplitude.append(vec_neg[peak])
        else: neg_amplitude.append(vec_pos[peak])
        last_peak = peak
      neg_amplitude.extend([None]*((end - start) - len(neg_amplitude)))
      
      # --- Calculating the strouhal number manually ---
      peak_frequency = 1/(2*len(x_axis[start:end])/((len(pos_peaks) + len(neg_peaks))*sample_fq))

      # FFT ----
      from scipy.fft import fft, fftfreq
      N = end-start

      yf = fft(signal)
      abs_yf = np.abs(yf)
      xf = fftfreq(N, 1 / sample_fq)

      max_index = np.where(abs_yf==max(abs_yf))[0][0]
      
      if xf[max_index] == 0:
          abs_yf[max_index] = 0
      
      peak_frequency_2 = xf[np.where(abs_yf==max(abs_yf))[0][0]]

      strouhal = (peak_frequency * diameter[sensor])/speed_levels[rc]
      strouhal2 = (peak_frequency_2 * diameter[sensor])/speed_levels[rc]

      St[rc] = strouhal
      St2[rc] = strouhal2

      max_forces[rc] = max(max(signal), abs(min(signal)))
      # ----------------------------------------------------------------------

      x = x_axis[start:end]

      plt.plot(x, pos_amplitude, 'ro')
      plt.plot(x, neg_amplitude, 'bo')
      plt.plot(x, vec_pos, color='sandybrown')
      plt.plot(x, vec_neg, color='lightskyblue')
      plt.hlines(max(signal), start, end, color='lime')
      plt.hlines(min(signal), start, end, color='lime')
      plt.title(name + ' | Peaks = ' + str(len(pos_peaks) + len(neg_peaks)) + ' | Mean_pos = ' + str(mean_pos) + ', Mean_neg = ' + str(-mean_neg) 
                + ' | Max_pos = ' + str(np.round(max(signal), 3)) + ', Max_neg = ' + str(np.round(min(signal), 3)) + ' | Strouhal Number = ' + str(np.round(strouhal, 3)))
      plt.show()

      rc += 1

plt.plot(Re, St, color='hotpink', label='Manual method')
plt.plot(Re, St2, color='slateblue', label='FFT method')
plt.xlabel('Re')
plt.ylabel('St')
plt.title('Strouhal Number, ' + name)
plt.legend()
plt.show()

plt.plot(Re, max_forces, 'o', color='navy')
plt.plot(Re, max_forces, color='steelblue')
plt.ylabel('Nm')
plt.xlabel('Re')
plt.title('Bending Moment, ' + name)
plt.show()
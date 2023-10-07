from apread import APReader
from matplotlib import pyplot as plt
import scipy as sp
import numpy as np
import os

# Function for reading in the data from the .BIN files in directory of choosing


def read_bin(directory):
    reader = []
    for root, dirs, files in os.walk(directory):
        for filename in sorted(files):
            reader.append(APReader(os.path.join(root, filename)))
    return reader

# Function to filter the noise from the signal. The value of 50 is default and can be changed


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
    # The x-axis, for use in plotting. Represents sample points, but can be divided with the sample frequency to represent time
    x_axis = np.linspace(0, samples, samples)
    # The data from the selected channel
    data = run.Channels[sensor].data
    # The name of the sensor
    name = run.Channels[sensor].Name
    # The name of the file
    filename = run.fileName

    return (sample_fq, samples, sample_fq, x_axis, data, name, filename)

# Function for calculating the strouhal number and the lift-induced peak bending moment.


def transverse_data(signal, diameter, velocity, sample_fq, period):
    # Fast Fourier Transform to get the vortex shedding frequency
    yf = sp.fft.fft(signal)
    xf = sp.fft.fftfreq(period, 1 / sample_fq)
    abs_yf = np.abs(yf)

    # Finding the most prominent shedding frequency
    max_index = np.where(abs_yf == max(abs_yf))[0][0]

    # Remove the frequency if it is 0
    if xf[max_index] == 0:
        abs_yf[max_index] = 0

    # Selecting the most prominent non-zero shedding frequency
    peak_frequency = xf[np.where(abs_yf == max(abs_yf))[0][0]]

    # Calculating the Strouhal Number
    St = (peak_frequency * diameter)/velocity

    # The highest absolute value of the signal is selected as the max Bending Moment
    BendingMoment = max(max(signal), abs(min(signal)))

    return St, BendingMoment, peak_frequency

# Function for calculating the mean in-line force

def in_line_data(signal):
    # the mean value over the selected period 
    bending_moment = np.abs(np.mean(signal))
    return bending_moment

# Function for plotting the signal. The peaks are plotted, as well as the negative and positive bending moment


def plot_signal(signal, start, end, x_axis, name):
    # This is a weighting value to move the scale of the signal up from the 0-line. This is to avoid errors with signs
    m = 200

    # Vectors to store the positive and negative values of the signal are initialized
    vec_pos = []
    vec_neg = []

    # Iterating through the values in the signal and adding them to the correct vector. 0 is added if the value is not added to preserve the shape of the vectors in the plotting
    for elem in signal:
        if elem < 0:
            # 0 is added if the value is not the corresponding sign, to preserve the shape of the vectors in the plotting
            vec_pos.append(0)
            vec_neg.append(elem)
        if elem >= 0:
            vec_pos.append(elem)
            vec_neg.append(0)
    # The signal is elevated by m, such that all peaks are included, even those that might register below zero
    pos_weighted_signal = [value+m for value in signal]
    # The signal is flipped by multiplying with -1, and elevated by m. This is to turn all valleys in the signal to peaks
    neg_weighted_signal = [(value*(-1))+m for value in signal]

    # The indices of all the peaks and valleys are calculated
    pos_peaks = sp.signal.find_peaks(
        pos_weighted_signal, height=m*0.25, distance=30)[0]
    neg_peaks = sp.signal.find_peaks(
        neg_weighted_signal, height=m*0.25, distance=30)[0]

    # The vectors for the peaks and valleys are initialized. The value None is used in this part, since it does not show in plotting
    pos_amplitude = [None]
    neg_amplitude = [None]

    # Variable to keep track of the last selected peak index
    last_peak = 0

    # Iterating through the positive peaks
    for peak in pos_peaks:
        # Between the peaks, the value None is added where all other signal data was before. This way we only preserve the amplitudes of the peaks in the signal
        pos_amplitude.extend([None]*(peak-last_peak-1))

        # We add the amplitude to the vector
        if vec_pos[peak] > 0:
            pos_amplitude.append(vec_pos[peak])

        # If the value returns zero from the positive part of the signal, then we have a peak in the negative part of the signal
        else:
            pos_amplitude.append(vec_neg[peak])

        # The selected peak is updated to the last peak and the iteration is complete
        last_peak = peak

    # The remaining values of None is added to the end of the positive amplitude vector
    pos_amplitude.extend([None]*((end - start) - len(pos_amplitude)))

    # --- This is the same procedure as with the positive amplitudes. Only this time it is the negative amplitudes
    last_peak = 0
    for peak in neg_peaks:
        neg_amplitude.extend([None]*(peak-last_peak-1))
        if vec_neg[peak] < 0:
            neg_amplitude.append(vec_neg[peak])
        else:
            neg_amplitude.append(vec_pos[peak])
        last_peak = peak
    neg_amplitude.extend([None]*((end - start) - len(neg_amplitude)))
    # ---

    # \-- Plotting --/

    # The amplitudes are plotted as points
    plt.plot(x_axis, pos_amplitude, 'ro')
    plt.plot(x_axis, neg_amplitude, 'bo')

    # The positive and negative part of the signal is plotted
    plt.plot(x_axis, vec_pos, color='sandybrown')
    plt.plot(x_axis, vec_neg, color='lightskyblue')

    # A line is plotted where the maximum value is
    plt.hlines(max(signal), start, end, color='lime')
    plt.hlines(min(signal), start, end, color='lime')

    # Title is selected
    plt.title(name + ' | Peaks = ' + str(len(pos_peaks) + len(neg_peaks)) + ' | Max value = ' + str(np.round(max(signal), 3)) +
              ', Min value = ' + str(np.round(min(signal), 3)))
    plt.show()

def find_closest_number(target, number_list):
    # if not number_list:
    #     return None, None  # Return None for both closest_number and index if the list is empty

    closest_number = number_list[0]  # Initialize the closest_number with the first element
    min_difference = abs(target - closest_number)  # Initialize the minimum difference
    closest_index = 0  # Initialize the index of the closest number

    for index, number in enumerate(number_list):
        difference = abs(target - number)
        if difference < min_difference:
            min_difference = difference
            closest_number = number
            closest_index = index

    return closest_number, closest_index

def instant_freq(signal,index):
    # This is a weighting value to move the scale of the signal up from the 0-line. This is to avoid errors with signs
    m = 200

    # Vectors to store the positive and negative values of the signal are initialized
    vec_pos = []
    vec_neg = []

    # Iterating through the values in the signal and adding them to the correct vector. 0 is added if the value is not added to preserve the shape of the vectors in the plotting
    for elem in signal:
        if elem < 0:
            # 0 is added if the value is not the corresponding sign, to preserve the shape of the vectors in the plotting
            vec_pos.append(0)
            vec_neg.append(elem)
        if elem >= 0:
            vec_pos.append(elem)
            vec_neg.append(0)
    # The signal is elevated by m, such that all peaks are included, even those that might register below zero
    pos_weighted_signal = [value+m for value in signal]
    # The signal is flipped by multiplying with -1, and elevated by m. This is to turn all valleys in the signal to peaks
    #neg_weighted_signal = [(value*(-1))+m for value in signal]

    # The indices of all the peaks and valleys are calculated
    pos_peaks = sp.signal.find_peaks(
        pos_weighted_signal, height=m*0.25, distance=30)[0]
    #neg_peaks = sp.signal.find_peaks(
    #    neg_weighted_signal, height=m*0.25, distance=30)[0]
    
    # from index, find closest pos peak 
    closest_peak, closest_index=find_closest_number(index, pos_peaks)
    #print(closest_index)
    #find the distance to the next peak
    if closest_index>=len(pos_peaks)-1:   #little trick to stay inside the table, gives us the same frequency for the last two peaks
        #print('closest_index = ',closest_index)
        closest_index=closest_index-2
        
    period=pos_peaks[closest_index+1]-pos_peaks[closest_index]
    frequency=1/period
    return frequency, closest_peak, pos_peaks




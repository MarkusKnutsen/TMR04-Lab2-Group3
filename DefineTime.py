# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 11:30:30 2023
Script to plot the signals and define the relevant period to estimate the relevant time indices to estimate the data

@author: Yann
"""
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np

# Importing functions from ./function.py in this diectory
from functions import read_bin, gauss_filter, data_collecting_function, transverse_data, plot_signal, instant_freq

sns.set_context("paper")
sns.set_theme(style="darkgrid", palette="bright")

# \-- Channel Information --/
# 0   Channel "Time  1 - default sample rate" (9495 Entries)
# 1   Channel "1X" (9495 Entries)
# 2   Channel "1Y" (9495 Entries)
# 3   Channel "2X" (9495 Entries)
# 4   Channel "2Y" (9495 Entries)
# 5   Channel "3X" (9495 Entries)
# 6   Channel "3Y" (9495 Entries)
# 7   Channel "UL_WaterLevel" (9495 Entries)
# 8   Channel "Position" (9495 Entries)
# 9   Channel "velocity" (9495 Entries)

# \-- Data for the cylinders used in the experiment --/

# Diameter based on channel number
diameter = [0, 0.029, 0.029, 0.025, 0.025, 0.032, 0.032, 0, 0, 0]
# Velocity and Reynolds Number based on run number
velocity_levels = [0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.80, 0.80,
                   0.80, 0.80, 0.80, 0.8, 0.9, 1, 1.1, 1.15, 1.2, 1.3, 1.4, 1.5]
Re = [10000, 12500, 15000, 16250, 17500, 18750, 20000, 20000, 20000, 20000,
      20000, 21250, 22500, 25000, 27500, 28750, 30000, 32500, 35000, 37500]

# Reading in the data
directory = './bin'
reader = read_bin(directory)

# Sensors that we want to investigate
sensors = [2, 4, 6]

# We build the indexes list to have all the data
Y1 = np.zeros([(len(reader)), 2])
rc = 0
for run in reader:
    (sample_fq, samples, sample_fq, x_axis, data,
     name, filename) = data_collecting_function(run, 2)
    Y1[rc] = [0, samples]
    rc += 1
Y1 = [[int(num) for num in sublist] for sublist in Y1]
Y2 = Y1
Y3 = Y1
# List containing the index data
indices = [0, 0, Y1, 0, Y2, 0, Y3, 0, 0, Y1]

rc = 0

# %%
rc = 0
Vibration_freq = [[], [], []]
for run in reader:
    for sensor in sensors:
        # this index is the longest
        Vibration_freq[round(
            sensor/2)-1] = np.zeros([len(reader), indices[sensor][0][1]])
    rc += 1

# %%
# Iterating through the different runs
rc = 0
for run in reader:

    # Iterating through the different sensors we want to investigate in that run
    for sensor in sensors:

        print('sensor= ', sensor)

        # Selecting the steady state information indices to be used when processing the signal from the sensor
        start = indices[sensor][rc][0]
        end = indices[sensor][rc][1]

        # Calculating variables from the signal
        (sample_fq, samples, sample_fq, x_axis, data, name,
         filename) = data_collecting_function(run, sensor)

        # Filter the data slightly, to remove some high-frequency noise in the peaks and valleys of the signal
        signal = gauss_filter(data[start:end], 4)

        # Calculating the Strouhal Number and maximum bending moment from the signal
        strouhal, moment, freq = transverse_data(
            signal, diameter[sensor], velocity_levels[rc], sample_fq, end-start)

        # If un-commented, the signal can be plotted
        # plot_signal(signal, start, end, x_axis[start:end], name)
        for i in range(end):
            frequency, closest_peak, pos_peaks = instant_freq(signal, i)
            Vibration_freq[round(sensor/2)-1][rc][i] = frequency

        # Updating the run counter, and completing the iteration
    rc += 1
    print('rc =', rc)

# %%

# Get the velocities
Velocity = [[] for _ in range(len(reader))]
print(Velocity)

sensor = 9
rc = 0
# Iterating through the different runs
for run in reader:

    # Selecting the steady state information indices to be used when processing the signal from the sensor
    start = indices[sensor][rc][0]
    end = indices[sensor][rc][1]

    # Calculating variables from the signal
    (sample_fq, samples, sample_fq, x_axis, data, name,
     filename) = data_collecting_function(run, sensor)

    # Filter the data slightly, to remove some high-frequency noise in the peaks and valleys of the signal
    signal = gauss_filter(data[start:end], 4)

    # If un-commented, the signal can be plotted
    # plot_signal(signal, start, end, x_axis[start:end], name)
    Velocity[rc] = signal

    # Updating the run counter, and completing the iteration
    rc += 1
# %%
# Plots
rc = 0
sensors = [2, 4, 6]
for run in reader:
    for sensor in sensors:

        # plot against x, can be converted into time
        x = list(range(len(Velocity[rc])))

        # Sample data for the two quantities
        # Create a figure and the primary axis (left y-axis)
        fig, ax1 = plt.subplots()

        # Plot the first quantity on the primary axis (left y-axis)
        ax1.plot(x, Vibration_freq[round(
            sensor/2)-1][rc][:len(Velocity[rc])], color='red', label='oscillation freq')
        ax1.set_xlabel('x')
        ax1.set_ylabel('Frequency of oscillation (Hz)', color='red')
        # ax1.tick_params(axis='y', labelcolor='b')
        round_thousands = round(len(x)/1000)*1000
        nb_thousand = int(round_thousands/1000)
        ax1.set_xticks(np.linspace(0, round_thousands, nb_thousand+1))

        # Create a secondary axis (right y-axis) that shares the same x-axis
        ax2 = ax1.twinx()

        # Plot the second quantity on the secondary axis (right y-axis)
        ax2.plot(x, Velocity[rc], color='blue', label='Velocity')
        ax2.set_ylabel('Velocity (m/s)', color='blue')
        # ax2.tick_params(axis='y', labelcolor='r')

        # Adding legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines = lines1 + lines2
        labels = labels1 + labels2
        ax1.legend(lines, labels, loc='lower center')
        # ax2.legend(labels2, loc='lower center')

        plt.title(
            f'Frequency of oscillation and velocity, run ={rc}, sensor={sensor}')
        plt.show()

    rc += 1

from matplotlib import pyplot as plt
from functions import read_bin
import seaborn as sns
import numpy as np
import csv
import sys

sns.set_context("paper")
sns.set_theme(style="darkgrid", palette="bright")

# For testing. Enables the terminal to print more that a few elements in a long list
np.set_printoptions(threshold=sys.maxsize)

# Increasing the amount of data that can be written to a csv file
csv.field_size_limit(10000000)

# Reading in the data
directory = './decay-tests-bin'
reader = read_bin(directory)

# Function to write the data from the decay tests to a csv file


def decay_analysis(decay_run, decay_indices, material, plot=1):

    # Counter to keep track of what channel we are on. cc = channel counter
    cc = 0

    # Iterating the channels for the decay run we are investigating
    # The channels are listed in data.py, and we are using channel 1-6
    for channel in decay_run.Channels[1:7]:

        # Finding the start and end indices of the signal. This is where the data is relevant
        start = decay_indices[cc][0]
        end = decay_indices[cc][1]

        # Based on the indices, the data is sliced and selected
        data = channel.data[start:end]

        # The x-axis is sliced and selected
        x_axis = decay_run.Channels[0].data[start:end]
        # For the plotting, the x-axis is transformed to the time-axis
        time = [(point-x_axis[0])/200 for point in x_axis]

        # The title of the decay plot is selected, such that the signal is easy to identify
        plot_title = "Decay test in " + material + " | " + channel.Name

        # The filename for the CSV file for data storage is created
        csv_filepath = './decay-csv/' + material.lower() + '-' + channel.Name + '.csv'

        # Writing the data to the CSV file.
        # The data is represented as a list of string-values, and will have to be converted back to floats when used
        with open(csv_filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

        # Default value for plot is 1, but by changing the value, the plotting may be cancelled
        if plot == 1:
            plt.plot(x_axis, data)
            plt.title(plot_title)
            plt.ylabel("Bending Moment (Nm)")
            plt.xlabel("Time (s)")
            plt.show()

        # Updating the channel counter for the next iteration
        cc += 1
    return 0


# The indices selected for the decay in air. Selected manually from the decay time-series
decay_indices_air = [[5400, 47600], [51100, 120000], [
    121000, 203500], [203600, 308400], [308500, 370000], [380000, 434000]]

# Writing the decay data in air to a CSV file and plotting the decay, for every channel
air_decay = decay_analysis(
    reader[0], decay_indices_air, 'Air')

# The indices selected for the decay in water. Selected manually from the decay time-series
decay_indices_water = [[5700, 7500], [11500, 17000], [19100, 22900],
                       [34500, 41800], [43650, 45400], [47350, 49300]]

# Writing the decay data in water to a CSV file and plotting the decay, for every channel
water_decay = decay_analysis(
    reader[1], decay_indices_water, 'Water')

# The code below is used for reading the CSV files
# This can be ignored and is used for debugging and verifying the readability of the CSV files

# ----------------------------------------------------
# with open('./decay-csv/air-1X.csv', newline='') as f:
#     reader = csv.reader(f, delimiter=',')
#     raw_data = next(reader)
#     data = [eval(i) for i in raw_data]

#     plt.plot(data)
#     plt.show()
# ----------------------------------------------------

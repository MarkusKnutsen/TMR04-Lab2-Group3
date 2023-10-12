from matplotlib import pyplot as plt
from functions import read_bin
import seaborn as sns
import numpy as np
import csv
import sys

np.set_printoptions(threshold=sys.maxsize)

sns.set_context("paper")
sns.set_theme(style="darkgrid", palette="bright")

# Reading in the data
directory = './decay-tests-bin'
reader = read_bin(directory)

csv.field_size_limit(10000000)


def decay_analysis(decay_run, decay_indices, material, plot=1):
    rc = 0
    # Open the CSV file to insert the data
    for channel in decay_run.Channels[1:7]:
        start = decay_indices[rc][0]
        end = decay_indices[rc][1]
        data = channel.data[start:end]
        x_axis = decay_run.Channels[0].data[start:end]
        plot_title = "Decay test in " + material + " | " + channel.Name

        csv_filepath = './decay-csv/' + material.lower() + '-' + channel.Name + '.csv'

        with open(csv_filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

        if plot == 1:
            plt.plot(x_axis, data)
            plt.title(plot_title)
            plt.ylabel("Bending Moment (Nm)")
            plt.xlabel("Time (s)")
            plt.show()
        rc += 1
    return 0


decay_indices_air = [[5400, 47600], [51100, 120000], [
    121000, 203500], [203600, 308400], [308500, 370000], [380000, 434000]]

air_decay = decay_analysis(
    reader[0], decay_indices_air, 'Air', 0)

decay_indices_water = [[5700, 7500], [11500, 17000], [19100, 22900],
                       [34500, 41800], [43650, 45400], [47350, 49300]]

water_decay = decay_analysis(
    reader[1], decay_indices_water, 'Water', 0)

# with open('./decay-csv/air-1X.csv', newline='') as f:
#     reader = csv.reader(f, delimiter=',')
#     raw_data = next(reader)
#     data = [eval(i) for i in raw_data]

#     plt.plot(data)
#     plt.show()

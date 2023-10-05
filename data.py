from matplotlib import pyplot as plt
import seaborn as sns

# Importing functions from ./function.py in this diectory
from functions import read_bin, gauss_filter, data_collecting_function, transverse_data, plot_signal

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
sensors = [4]

# Indices ues for the 2Y data. Data selected to remove the transient information
Y2 = [[3400, 11200], [3200, 9200], [3200, 8400], [3100, 7600], [3700, 7700], [3300, 7100], [3800, 6700], [3200, 6700], [4000, 7300], [3700, 7000], [
    3500, 6800], [3500, 5600], [3400, 6400], [4000, 5900], [3340, 5730], [4160, 5550], [4440, 5500], [4830, 5400], [3770, 4850], [3750, 4920]]

# List containing the index data
indices = [0, 0, 0, 0, Y2, 0, 0, 0, 0, 0]

# List for storing the maximum value for the bending moment
BendingMoment = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# List for storing the strouhal number
St = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Variable to keep track of the runs. rc stands for run counter
rc = 0

# Iterating through the different runs
for run in reader:

    # Iterating through the different sensors we want to investigate in that run
    for sensor in sensors:

        # Selecting the steady state information indices to be used when processing the signal from the sensor
        start = indices[sensor][rc][0]
        end = indices[sensor][rc][1]

        # Calculating variables from the signal
        (sample_fq, samples, sample_fq, x_axis, data, name,
         filename) = data_collecting_function(run, sensor)

        # Filter the data slightly, to remove some high-frequency noise in the peaks and valleys of the signal
        signal = gauss_filter(data[start:end], 4)

        # Calculating the Strouhal Number and maximum bending moment from the signal
        strouhal, moment = transverse_data(
            signal, diameter[sensor], velocity_levels[rc], sample_fq, end-start)

        # Adding the Stouhal data, and maximum bending moment to the vectors containing that data. To be used for plotting
        St[rc] = strouhal
        BendingMoment[rc] = moment

        # If un-commented, the signal can be plotted
        # plot_signal(signal, start, end, x_axis[start:end], name)

        # Updating the run counter, and completing the iteration
        rc += 1

# \-- Plotting --/

# Plotting the Strouhal Number against the Reynolds number. Both lines and points are plotted
plt.plot(Re, St, color='hotpink', label='Strouhal Number')
plt.plot(Re, St, 'o', color='crimson')

# Labeling the units on the axis
plt.xlabel('Re')
plt.ylabel('St')

# Title is selected
plt.title('Strouhal Number, ' + name + ' ' + filename)

plt.legend()
plt.show()

# Plotting the Bending moment against the Reynolds number. Both lines and points are plotted
plt.plot(Re, BendingMoment, color='steelblue', label='Bending Moment')
plt.plot(Re, BendingMoment, 'o', color='navy')

# Labeling the units on the axis
plt.ylabel('Nm')
plt.xlabel('Re')

# Title is selected
plt.title('Bending Moment, ' + name + ' ' + filename)

plt.legend()
plt.show()

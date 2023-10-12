from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np

# Importing functions from ./function.py in this diectory
from functions import read_bin, gauss_filter, data_collecting_function, transverse_data, plot_signal, in_line_data

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
                   0.80, 0.80, 0.80, 0.85, 0.9, 1, 1.1, 1.15, 1.2, 1.3, 1.4, 1.5]

# Re is calculated for a diameter of 25mm for now, maybe will correct later
Re=np.zeros(len(velocity_levels))
for i in range(len(velocity_levels)):
    Re[i]=velocity_levels[i]*0.025/(10**-6)

# Reading in the data
directory = './bin'
reader = read_bin(directory)

# Sensors that we want to investigate
sensors = [2,4,6]

# Indices ues for the 2Y data. Data selected to remove the transient information, 
# to do so we use the combined plots of oscillation frequency and velocity against x provided
# with the code "DefineTime"

#   ---run 0---------1 --------run 2----------3-----------4-----------5-----------6-----------7-----------8-----------9-----
Y1=[[3600,11000],[3000,9500],[3000,8500],[3000,7800],[3800,7800],[3000,7100],[3800,7000],[3500,7000],[4000,7500],[3800,6800], [
    3500, 6800], [3800, 6700], [3000, 6400], [3800, 6300], [3300, 5600], [3200, 5300], [3200, 5400], [3500, 5400], [3500, 5000], [3900, 4900]]
#------10-------------11------------12------------13------------14-----------15-------------16------------17------------18------------19-----

Y2=[[3400,11200],[3200,9200],[3200,8400],[3100,7600],[3700,7700],[3000,7100],[3500,7000],[3400,6700],[4000,7500],[3300,7000], [
    3200, 6800], [3200, 5600], [3000, 6400], [3500, 6000], [3200, 5700], [3200, 5400], [4200, 5400], [4000, 5400], [3500, 5000], [3500, 4900]]

Y3=[[3500,11000],[3000,9500],[3000,8500],[3000,7800],[3800,7800],[3100,7100],[3200,7000],[3500,6700],[4000,7500],[3000,7000], [
    3000, 6800], [3000, 6800], [3800, 6300], [3400, 6300], [3200, 5500], [3200, 5400], [4000, 5000], [3500, 5400], [3500, 5000], [3500, 4900]]
X2=Y2
X1=Y1
X3=Y3

# List containing the index data
indices = [0, X1, Y1, X2, Y2, X3, Y3, 0, 0, 0]

# List for storing the maximum value for the cross-flow bending moment
BendingMoment1,BendingMoment2,BendingMoment3 = np.zeros([3,len(reader)])
BendingMoment=[BendingMoment1,BendingMoment2,BendingMoment3]

# List for storing the mean value for the in-flow bending moment
InLineBending=np.zeros([3,len(reader)])

# List for storing the strouhal number
St=np.zeros([3,len(reader)])

#List for storing the Lock-in frequency
Vibration_mean_freq=np.zeros([3,len(reader)])

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
        strouhal, moment, freq = transverse_data(
            signal, diameter[sensor], velocity_levels[rc], sample_fq, end-start)
        # Adding the Stouhal data, and maximum bending moment to the vectors containing that data. To be used for plotting
        #print(round(sensor/2)-1)
        St[round(sensor/2)-1][rc] = strouhal
        BendingMoment[round(sensor/2)-1][rc] = moment
        Vibration_mean_freq[round(sensor/2)-1][rc]=freq
        InLineBending[round(sensor/2)-1][rc]=in_line_data(signal)
        
        # If un-commented, the signal can be plotted
        #plot_signal(signal, start, end, x_axis[start:end], name)

    # Updating the run counter, and completing the iteration
    rc += 1

#%%
# \-- Plotting --/

# Creation of the different Reynolds number for each pipe
diameter=[0.029,0.025,0.032]
Re=np.zeros([3,len(velocity_levels)])
for i in [0,1,2]:
    for j in range(len(velocity_levels)):
        Re[i][j]=velocity_levels[j]*diameter[i]/(10**-6)


# Plotting the Strouhal Number against the Reynolds number. Both lines and points are plotted
plt.plot(Re[0], St[0], color='green', label='Pipe with Streaks')
plt.plot(Re[0], St[0], 'o', color='green')
plt.plot(Re[1], St[1], color='steelblue', label='Original Pipe')
plt.plot(Re[1], St[1], 'o', color='steelblue')
plt.plot(Re[2], St[2], color='hotpink', label='Perforated Pipe')
plt.plot(Re[2], St[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.xlabel('Re')
plt.ylabel('St')

# Title is selected
plt.title('Strouhal Number')

plt.legend()
plt.show()


# Plotting the Strouhal Number against the velocity level. Both lines and points are plotted
plt.plot(velocity_levels, St[0], color='green', label='Pipe with Streaks')
plt.plot(velocity_levels, St[0], 'o', color='green')
plt.plot(velocity_levels, St[1], color='steelblue', label='Original Pipe')
plt.plot(velocity_levels, St[1], 'o', color='steelblue')
plt.plot(velocity_levels, St[2], color='hotpink', label='Perforated Pipe')
plt.plot(velocity_levels, St[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.xlabel('velocity (m/s)')
plt.ylabel('St')

# Title is selected
plt.title('Strouhal Number')

plt.legend()
plt.show()

# Plotting the Bending moment against the Reynolds number. Both lines and points are plotted
plt.plot(Re[0], BendingMoment[0], color='green', label='Pipe with Streaks')
plt.plot(Re[0], BendingMoment[0], 'o', color='green')
plt.plot(Re[1], BendingMoment[1], color='steelblue', label='Original Pipe')
plt.plot(Re[1], BendingMoment[1], 'o', color='steelblue')
plt.plot(Re[2], BendingMoment[2], color='hotpink', label='Perforated Pipe')
plt.plot(Re[2], BendingMoment[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.ylabel('Bending moment (Nm)')
plt.xlabel('Re')

# Title is selected
plt.title('Cross Flow max Bending Moments')

plt.legend()
plt.show()

# Plotting the Bending moment against the velocity levels. Both lines and points are plotted
plt.plot(velocity_levels, BendingMoment[0], color='green', label='Pipe with Streaks')
plt.plot(velocity_levels, BendingMoment[0], 'o', color='green')
plt.plot(velocity_levels, BendingMoment[1], color='steelblue', label='Original Pipe')
plt.plot(velocity_levels, BendingMoment[1], 'o', color='steelblue')
plt.plot(velocity_levels, BendingMoment[2], color='hotpink', label='Perforated Pipe')
plt.plot(velocity_levels, BendingMoment[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.ylabel('Bending moment (Nm)')
plt.xlabel('velocity level (m/s)')

# Title is selected
plt.title('Cross Flow max Bending Moments')

plt.legend()
plt.show()

# Plotting the in line Bending moment against the Reynolds number. Both lines and points are plotted
plt.plot(Re[0], InLineBending[0], color='green', label='Pipe with Streaks')
plt.plot(Re[0], InLineBending[0], 'o', color='green')
plt.plot(Re[1], InLineBending[1], color='steelblue', label='Original Pipe')
plt.plot(Re[1], InLineBending[1], 'o', color='steelblue')
plt.plot(Re[2], InLineBending[2], color='hotpink', label='Perforated Pipe')
plt.plot(Re[2], InLineBending[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.ylabel('Bending moment (Nm)')
plt.xlabel('Re')

# Title is selected
plt.title('In line mean Bending Moment')

plt.legend()
plt.show()

# Plotting the in line Bending moment against the velocity levels. Both lines and points are plotted
plt.plot(velocity_levels, InLineBending[0], color='green', label='Pipe with Streaks')
plt.plot(velocity_levels, InLineBending[0], 'o', color='green')
plt.plot(velocity_levels, InLineBending[1], color='steelblue', label='Original Pipe')
plt.plot(velocity_levels, InLineBending[1], 'o', color='steelblue')
plt.plot(velocity_levels, InLineBending[2], color='hotpink', label='Perforated Pipe')
plt.plot(velocity_levels, InLineBending[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.ylabel('Bending moment (Nm)')
plt.xlabel('velocity (m/s)')

# Title is selected
plt.title('In line mean Bending Moment')

plt.legend()
plt.show()

# Plotting the Vibration freqency against the velocity. Both lines and points are plotted
plt.plot(velocity_levels, Vibration_mean_freq[0], color='green', label='Pipe with Streaks')
plt.plot(velocity_levels, Vibration_mean_freq[0], 'o', color='green')
plt.plot(velocity_levels, Vibration_mean_freq[1], color='steelblue', label='Original Pipe')
plt.plot(velocity_levels, Vibration_mean_freq[1], 'o', color='steelblue')
plt.plot(velocity_levels, Vibration_mean_freq[2], color='hotpink', label='Perforated Pipe')
plt.plot(velocity_levels, Vibration_mean_freq[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.xlabel('velocity (m/s)')
plt.ylabel('vibration frequency (Hz)')

# Title is selected
plt.title('Vibration frequency')

plt.legend()
plt.show()

# Plotting the Vibration freqency against the velocity. Both lines and points are plotted
plt.plot(Re[0], Vibration_mean_freq[0], color='green', label='Pipe with Streaks')
plt.plot(Re[0], Vibration_mean_freq[0], 'o', color='green')
plt.plot(Re[1], Vibration_mean_freq[1], color='steelblue', label='Original Pipe')
plt.plot(Re[1], Vibration_mean_freq[1], 'o', color='steelblue')
plt.plot(Re[2], Vibration_mean_freq[2], color='hotpink', label='Perforated Pipe')
plt.plot(Re[2], Vibration_mean_freq[2], 'o', color='hotpink')

# Labeling the units on the axis
plt.xlabel('Re')
plt.ylabel('vibration frequency (Hz)')

# Title is selected
plt.title('Vibration frequency')

plt.legend()
plt.show()

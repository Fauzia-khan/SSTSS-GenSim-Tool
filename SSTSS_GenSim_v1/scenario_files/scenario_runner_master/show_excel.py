import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('full_speed_data.csv')

plt.plot(df['time'].values, df['linear_x'].values, label='Linear X')
plt.plot(df['time'].values, df['carla_speed'].values, label='Carla', linestyle='--')
plt.plot(df['time'].values, df['dashboard'].values, label='Dashboard')

plt.xlabel('time (s)')
plt.ylabel('Speed (km/h)')

plt.legend()
plt.show()

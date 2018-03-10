"""
Generate Gaussian distributed random datetimes so we can play with plotting date along the x-axis
and time of day up the y-axis
"""

import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DAYS_PER_YEAR = 365
SIGMA = 1800
MAX_POINTS_PER_DAY = 10

times = []

start = datetime.date(2017, 1, 1)
colours = {'Seagrave': 'red', 'Athorpe': 'yellow', 'Hatfield': 'green', 'Osborne': 'blue'}
for d in range(DAYS_PER_YEAR):
    date = start + datetime.timedelta(days=d)
    for i in range(np.random.randint(MAX_POINTS_PER_DAY)):
        t = datetime.datetime.combine(date, datetime.time(18, 0, 0)) + datetime.timedelta(seconds=np.random.normal(0.0, SIGMA))
        c = np.random.choice(list(colours.keys()), p=[0.4, 0.4, 0.1, 0.1])
        times.append({'start': t, 'colour': c})
df = pd.DataFrame(times)
df['datetime'] = df['start'].astype(datetime.datetime)
df['time'] = df['start'].dt.hour + df['start'].dt.minute/60
fig, ax = plt.subplots()
for house, colour in colours.items():
    df2 = df[df['colour'] == house]
    plt.plot(df2['datetime'], df2['time'], '.', color=colour)
plt.show()

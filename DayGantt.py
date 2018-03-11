"""
Playing with a Gantt-style display of events within an arbitrary day.

The idea is to be able to produce a plot of scheduled events -
cron jobs and MySQL scheduled events - for a particular system.
This script plays with the display of such data.
"""

import datetime
import itertools
import random
import logging
from bokeh.plotting import figure, show, output_file
import pandas as pd

class Event:
    """
    An event for us to handle/plot
    """
    counter = itertools.count()

    def __init__(self, description, owner):
        """

        :param description: What the event is (string)
        :param owner: What initiates the event e.g. cron (Owner object)
        :param time: When does it fire (datetime.time)
        """
        self.id = next(Event.counter)
        self.description = description
        self.owner = owner
        self.schedule = []

    def __repr__(self):
        return "[{}] Event: {} Owner: {} Occurrences: {}".format(self.id, self.description, self.owner, len(self.schedule))

    def __lt__(self, other):
        if self.owner == other.owner:
            return self.description < other.description
        else:
            return self.owner < other.owner

    def __iter__(self):
        for t in sorted(self.schedule):
            yield t

    def AddInstance(self, time, duration=None):
        """
        Adds an instance of a particular event.
        :param time:
        :param duration:
        :return:
        """
        if type(time) is datetime.time:
            time = datetime.datetime.combine(datetime.datetime.today(), time)
        if type(time) is datetime.datetime:
            if self.schedule and time < self.schedule[-1].start:
                logging.warning('Inserting event in to {} at {} when last entry is {}'.format(
                                            self.description, time, self.schedule[-1].start))
            if time in [i.start for i in self.schedule]:
                logging.warning('Event {} already has an entry for {}. Ignoring'.format(self.description, time))
            else:
                self.schedule.append(Instance(time, duration))
        else:
            logging.error('Schedule entries must be of type datetime.datetime')


class Instance:
    """
    An instance of a particular event.
    """
    def __init__(self, time, duration=None):
        self.start = time
        self.duration = duration
        if self.duration:
            self.end = self.start + self.duration
        else:
            self.end = self.start

    def __repr__(self):
        if self.duration:
            return "{}-{}".format(self.start, self.end)
        else:
            return "{}".format(self.start)

    def __lt__(self, other):
        return self.start < other.start

class Owner:
    """
    The owner of an event. Colours and shapes are for plotting on
    the timeline using matplotlib
    """
    colours = itertools.cycle("rybgcm")
    shapes = itertools.cycle("ov<>^sD")
    counter = itertools.count()

    def __init__(self, name, rank=100):
        self.id = next(Owner.counter)
        self.name = name
        self.rank = rank
        self.marker = next(Owner.colours)+next(Owner.shapes)

    def __repr__(self):
        return "[{}] {} {} {}".format(self.id, self.name, self.rank, self.marker)

    def __lt__(self, other):
        if self.rank == other.rank:
            return self.name < other.name
        else:
            return self.rank < other.rank


snowy = Owner('Snowy the Wonderdog')
events = [Event(e, snowy) for e in ['Bury bone', 'Attack postman', 'Chase squirrel', 'Dig bone up again']]

for index, event in enumerate(events):
    for hour in range(8,24,4):
        for minute in range(0,60,30):
            event.AddInstance(datetime.time(hour+index, minute), datetime.timedelta(minutes=15*(index+1)))

output_file('rectangles.html')

p = figure(plot_width=1000, plot_height=100*len(events), title="Scheduled Events",
           x_axis_type="datetime", y_range=[event.description for event in reversed(events)])
for index, event in enumerate(reversed(events)):
    y = index + 0.5
    for instance in event.schedule:
        p.hbar(y=y, left=instance.start, right=instance.end, height=0.1, line_color="black", fill_color="firebrick", alpha=0.5)
show(p)
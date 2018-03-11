"""
Playing with a Gantt-style display of events within an arbitrary day.

The idea is to be able to produce a plot of scheduled events -
cron jobs and MySQL scheduled events - for a particular system.
This script plays with the display of such data.
"""

import datetime
import itertools
import logging
from bokeh.plotting import figure, show, output_file

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
        if self.schedule and other.schedule:
            if self.schedule[0].start == other.schedule[0].start:
                if self.owner == other.owner:
                    return self.description < other.description
                else:
                    return self.owner < other.owner
            else:
                return self.schedule[0].start < other.schedule[0].start
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
                self.schedule.sort()
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
    the timeline using Bokeh
    """
    colours = itertools.cycle(["red", "yellow", "green", "blue", "cyan", "magenta"])
    counter = itertools.count()

    def __init__(self, name, rank=100):
        self.id = next(Owner.counter)
        self.name = name
        self.rank = rank
        self.colour = next(Owner.colours)

    def __repr__(self):
        return "[{}] {} {}".format(self.id, self.name, self.rank)

    def __lt__(self, other):
        if self.rank == other.rank:
            return self.name < other.name
        else:
            return self.rank < other.rank

def PlotEvents(events, filename, title):
    AspectRatio = 16/9
    EventHeight = 50
    TitleHeight = 50
    EventSizeRatio = 1/3

    events = sorted(events)
    output_file(filename, title=title)

    height = int(TitleHeight + EventHeight * len(events))
    width  = int(height*AspectRatio)
    p = figure(plot_width=width, plot_height=height, title=title,
               x_axis_type="datetime", y_range=[event.description for event in reversed(events)])
    size = EventHeight*EventSizeRatio
    for index, event in enumerate(reversed(events)):
        y = index + 0.5
        for instance in event.schedule:
            if instance.duration:
                p.hbar(left=instance.start, right=instance.end, y=y, height=EventSizeRatio,
                       line_color="black", fill_color=event.owner.colour,
                       alpha=0.75, legend=event.owner.name)
            else:
                p.diamond(y=y, x=instance.start, line_color="black", fill_color=event.owner.colour, size=size,
                          alpha=0.75, legend=event.owner.name)
    show(p)

if __name__ == '__main__':

    snowy = Owner('Snowy the Wonderdog')
    tim = Owner('The Fat Controller')
    ming = Owner('Ming the merciless')
    events  = [Event(e, snowy) for e in ['Attack postman', 'Bury bone', 'Chase squirrel', 'Dig bone up again', 'Eat dinner']]
    events += [Event(e, tim) for e in ['Arcati', 'Baking', 'Cooking']]
    for index, event in enumerate(events):
        for hour in range(8,16,4):
            for minute in range(0,60,30):
                event.AddInstance(datetime.time(hour+index, minute), datetime.timedelta(minutes=15*(index)))
                event.AddInstance(datetime.time(hour, minute))
    events += [Event(e, ming) for e in ['World Domination']]
    events[-1].AddInstance(datetime.time(3,0))
    events[-1].AddInstance(datetime.time(4,0), datetime.timedelta(hours=2))
    events[-2].AddInstance(datetime.time(5,30), datetime.timedelta(minutes=30))
    PlotEvents(events, 'events.html', 'Stuff happening')

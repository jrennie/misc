#!/usr/bin/env python

from __future__ import division

import argparse
import datetime
import numpy
import scipy
import sqlite3
import time

TABLE = 'outTemp'

parser = argparse.ArgumentParser(description='Compute seasonal weewx statistics.')
parser.add_argument('filename', metavar='FILE', help='Weewx stats database file to use')
#parser.add_argument('table', metavar='TABLE', default='outTemp',
#                    help='Name of table containing outside temperatures')
args = parser.parse_args()

class YearData(object):
  days = 365

  def __init__(self):
    self.high = numpy.zeros((self.days,))
    self.avg = numpy.zeros((self.days,))
    self.low = numpy.zeros((self.days,))
    self.count = numpy.zeros((self.days,))

  def add(self, yday, dt, high, avg, low):
    if yday > self.days:
      print "Skipping yday=%d %s high=%s avg=%.1f low=%s" % (yday, dt, high, avg, low)
      return
    self.high[yday-1] += high
    self.avg[yday-1] += avg
    self.low[yday-1] += low
    self.count[yday-1] += 1

  def show(self):
    for i in xrange(self.days):
      print "%03d: %.1f/%.1f/%.1f" % (i, self.high[i]/self.count[i],
                                      self.avg[i]/self.count[i],
                                      self.low[i]/self.count[i]),
      if i % 10 == 9:
        print
      
data = YearData()
conn = sqlite3.connect(args.filename)
c = conn.cursor()
c.execute('SELECT dateTime, min, max, sum, count FROM %s' % (TABLE,))
r = True
while True:
    r = c.fetchone()
    if r is None:
        break
    timestamp, low, high, sum, count = r
    # skip days with relatively few observations
    if count < 24:
        continue
    year, month, mday, hour, min, sec, wday, yday, _ = time.localtime(timestamp)
    dt = datetime.datetime(year, month, mday, hour, min, sec)
    data.add(yday, dt, high, sum/count, low)
c.close()
data.show()

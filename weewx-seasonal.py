#!/usr/bin/env python

from __future__ import division

__author__ = 'Jason Rennie'

import argparse
import datetime
import matplotlib.pyplot as plt
import numpy
import scipy
import scipy.optimize
import smoothregression
import sqlite3
import time

TABLE = 'outTemp'
MIN_COUNT = 24  # skip days with few observations
NUM_DAYS = 365

def load_data(f):
  meanBuilder = smoothregression.DataBuilder()
  highBuilder = smoothregression.DataBuilder()
  lowBuilder = smoothregression.DataBuilder()
  conn = sqlite3.connect(f)
  c = conn.cursor()
  c.execute("""SELECT dateTime, min, max, sum, count FROM %s where count >= %d""" % (TABLE, MIN_COUNT))
  r = True
  while True:
    r = c.fetchone()
    if r is None:
      break
    timestamp, valLow, valHigh, valSum, valCount = r
    year, month, mday, hour, min, sec, wday, yday, _ = time.localtime(timestamp)
    dt = datetime.datetime(year, month, mday, hour, min, sec)
    if yday <= NUM_DAYS:
      meanBuilder.add([yday-1], [1], valSum/valCount)
      highBuilder.add([yday-1], [1], valHigh)
      lowBuilder.add([yday-1], [1], valLow)
  c.close()
  return meanBuilder, highBuilder, lowBuilder

def estimate(X, y, gamma):
  fit = smoothregression.SmoothRegression(X, y, gamma)
  w0 = numpy.random.randn(NUM_DAYS)
  smoothregression.checkgrad2(fit.obj_grad, w0)
  obj0, grad0 = fit.obj_grad(w0)
  print "obj0=%.4e grad0=%.4e" % (obj0, numpy.linalg.norm(grad0))
  (w1, obj1, info) = scipy.optimize.fmin_l_bfgs_b(fit.obj_grad, w0)
  if info['warnflag'] != 0:
    print "***** Failed to converge"
    if info['warnflag'] == 1:
      print "Too many iterations"
    else:
      print "Stopped because: " % (info['task'],)
  grad1 = info['grad']
  print "obj1=%.4e grad1=%.4e" % (obj1, numpy.linalg.norm(grad1))
  print "%d obj_grad calls" % (info['funcalls'],)
  return w1

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Compute seasonal weewx statistics.')
  parser.add_argument('filename', metavar='FILE', help='Weewx stats database file to use')
  #parser.add_argument('table', metavar='TABLE', default='outTemp',
  #                    help='Name of table containing outside temperatures')
  args = parser.parse_args()

  meanBuilder, highBuilder, lowBuilder = load_data(args.filename)
  wMeanRaw = estimate(*meanBuilder.build()[0], gamma=1)
  wHighRaw = estimate(*highBuilder.build()[0], gamma=1)
  wLowRaw = estimate(*lowBuilder.build()[0], gamma=1)

  plt.scatter(xrange(NUM_DAYS), wMeanRaw, s=2, marker='.')
  plt.scatter(xrange(NUM_DAYS), wHighRaw, s=2, marker='.')
  plt.scatter(xrange(NUM_DAYS), wLowRaw, s=2, marker='.')
  plt.axis([0, 365, 0, 100])
  plt.grid(True)
  #plt.bar(xrange(NUM_DAYS), w1)
  plt.show()

  wMeanSmooth = estimate(*meanBuilder.build()[0], gamma=1e6)
  wHighSmooth = estimate(*highBuilder.build()[0], gamma=1e6)
  wLowSmooth = estimate(*lowBuilder.build()[0], gamma=1e6)

  plt.scatter(xrange(NUM_DAYS), wMeanSmooth, s=2, marker='.')
  plt.scatter(xrange(NUM_DAYS), wHighSmooth, s=2, marker='.')
  plt.scatter(xrange(NUM_DAYS), wLowSmooth, s=2, marker='.')
  plt.axis([0, 365, 0, 100])
  plt.grid(True)
  #plt.bar(xrange(NUM_DAYS), w1)
  plt.show()

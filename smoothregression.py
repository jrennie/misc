#!/usr/bin/env python

from __future__ import division

import math
import numpy
import scipy.sparse

__author__ = 'Jason Rennie'

def checkgrad2(obj_grad, w):
  if len(w.shape) != 1:
    raise Exception("w must be a 1-d array; w.shape=%s" % (w.shape,))
  n = w.shape[0]
  print "n=%d" % (n,)
  eps = 1e-6
  obj, grad = obj_grad(w)
  d = eps * numpy.random.randn(n)
  obj2, grad2 = obj_grad(w + d)
  obj1, grad1 = obj_grad(w - d)
  ratio = (obj2 - obj1)/(2*d.dot(grad))
  if numpy.abs(1-ratio) > eps:
    raise Exception("Analytic gradient does not match empirical gradient; ratio=%.4e" % (ratio,))
  print "ratio=%.10f (should be very close to unity)" % (ratio,)


class SmoothRegression(object):

  def __init__(self, X, y, gamma=0.1):
    """
    @param X: independent variables
    @param y: dependent variable
    """
    self.X = X
    self.y = y
    self.gamma = gamma

  def obj_grad(self, w):
    diff = self.X.dot(w) - self.y
    penalty = 2*w - numpy.roll(w, 1) - numpy.roll(w, -1)
    obj = numpy.dot(diff, diff) / 2 + self.gamma * numpy.dot(penalty, penalty) / 2
    penalty_grad = (numpy.roll(w, 2) - 4 * numpy.roll(w, 1) + 6 * w
                    - 4 * numpy.roll(w, -1) + numpy.roll(w, -2))
    grad = self.X.T.dot(diff) + self.gamma * penalty_grad
    return obj, grad


class DataBuilder(object):

  def __init__(self):
    self.cur_row = -1
    self.row = []
    self.column = []
    self.value = []
    self.y = []

  def add(self, cols, vals, y):
    if len(cols) != len(vals):
      raise Exception("len(cols)=%d != len(vals)" % (len(cols), len(vals)))
    self.cur_row += 1
    self.row.extend([self.cur_row]*(len(cols)))
    self.column.extend(cols)
    self.value.extend(vals)
    self.y.append(y)

  def build(self, sizes=[1.0]):
    """@param sizes: list of floats which are nonnegative and sum to 1.0"""
    cumulative = 0.0
    ret = []
    tot = len(self.y)
    end = 0
    for s in sizes:
      cumulative += s
      start = end
      end = int(math.ceil(tot*cumulative))
      ret.append((scipy.sparse.csr_matrix((self.value[start:end], (self.row[start:end], self.column[start:end]))),
                  numpy.array(self.y[start:end])))
    return ret

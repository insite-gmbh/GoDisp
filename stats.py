#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C0303
# pylint: disable=W0621
# pylint: disable=W0312

import math
import queue

class statistics:

    _avgX = 0.0
    _avgY = 0.0
    _deviation = 0.0
    _slope = 0.0
    _yintercept = 0.0
    _maxSampleCount = 0
    _needsRecalc = True
    _samples = []
    
    def __init__(self, maxSampleCount):
        self._maxSampleCount = maxSampleCount

    def getSlope(self):
        self.RecalcAllifNeeded()
        return self._slope
    
    def setMaxSampleCount(self, count):
        self._maxSampleCount = count
    
    def getAvgY(self):
        self.RecalcAllifNeeded()
        return self._avgY

    def getAvgX(self):
        self.RecalcAllifNeeded()
        return self._avgX
    
    def getCountSamples(self):
        return len(self._samples)

    def reset(self):
        print("RESET STATS")
        self._avgX = 0.0
        self._avgY = 0.0
        self._deviation = 0.0
        self._slope = 0.0
        self._needsRecalc = True
        del self._samples[:]
    
    def addSample(self, sample):
        if len(self._samples) >= self._maxSampleCount:
            del self._samples[0]
        self._samples.append(sample)
        self._needsRecalc = True
        
    def RecalcAllifNeeded(self):
        if self._needsRecalc is True:
            self.CalcAverageY()
            self.CalcAverageX()
            self.CalcDeviation()
            self.CalcSlope()
            self._needsRecalc = False
    
    def CalcAverageY(self):
        if len(self._samples) > 0:
            sumY = 0.0
            for i in range(0, len(self._samples)):
                sumY += self._samples[i]
            self._avgY = sumY / len(self._samples)
        else:
            self._avgY = 0.0
    
    def CalcAverageX(self):
        if len(self._samples) > 0:
            sumX = 0.0
            for i in range(0, len(self._samples)):
                sumX += i
            self._avgX = sumX / len(self._samples)
        else:
            self._avgX = 0.0
    
    def CalcDeviation(self):
        if len(self._samples) > 1:
            fs = 0.0
            for val in self._samples:
                fs += math.pow(val - self._avgY, 2)
            self._deviation = math.sqrt(fs / (len(self._samples) - 1))
        else:
            self._deviation = 0.0
        
    def CalcSlope(self):
        if len(self._samples) > 1:
            nominator = 0.0
            denominator = 0.0
            x = 0
            for val in self._samples:
                nominator += (x - self._avgX) * (val - self._avgY)
                denominator += math.pow(x - self._avgX, 2)
                x += 1
            self._slope = nominator / denominator
            self._yintercept = self._avgY - self._slope * self._avgX
        else:
            self._slope = 0.0
            self._yintercept = 0.0

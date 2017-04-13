#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0621
# pylint: disable=W0312

import csv
from stats import statistics
from Util.Synchronization import synchronized

class Calibration:

    _SAMPLEWINDOWSIZE = 5
    _SLOPERANGE = 30  #Defines maximum Slope Deviation from 0 
    opening = 35
    increment = 10
    zeroFlowCounter = 0
    running = False

    def __init__(self, flowdetection, gate):
        self.statistics = statistics(self._SAMPLEWINDOWSIZE)
        self.flowdetection = flowdetection
        self.gate = gate
        
    def start(self):
        print("START CALIBRATION")
        self.running = True
        self.flowdetection.subscribe("FlowChanged", self)
        self.gate.execute(["P", self.opening])
            
    def stop(self):
        print("END CALIBRATION")
        self.running = False
        self.gate.execute(["C"])
        
    def onFlowChanged(self, flow):
        if self.running:
            synchronized(self._internalOnFlowChanged(flow))

    def _internalOnFlowChanged(self, flow):
        print("Adding Sample: ",flow)
        self.statistics.addSample(flow)
        if(self.statistics.getCountSamples() == self._SAMPLEWINDOWSIZE and self.checkSlope() is True):
            avgflow = self.statistics.getAvgY()
            self.writeCSV([avgflow,self.opening])
            self.statistics.reset()
            self.nextOpening()
            
    def nextOpening(self):
        self.opening += self.increment
        if self.opening <= 100:
            self.gate.execute(["P", self.opening])
        else:
            self.stop()

    def checkSlope(self):
        slope = abs(self.statistics.getSlope())
        if slope <= self._SLOPERANGE:
            print("Slope of ", self.statistics.getCountSamples(), "Samples = ", round(slope,2) ," GOOD")
            return True
        print("Slope of ", self.statistics.getCountSamples(), "Samples = ", round(slope,2) ," BAD")
        return False
            
    def writeCSV(self, row):
        if row[1] <= 100 and row[1] >= 0:
            with open('flow.csv', "r") as csvfile:
                reader = csv.reader(csvfile)
                duplicate = False
                temp = []
                for line in reader:
                    if line != [] and int(line[1]) == int(row[1]):
                        duplicate = True
                        if float(line[0]) < float(row[0]):
                            temp.append([str(round(row[0], 0)), str(row[1])])
                        else:
                            temp.append(line)
                    else:
                        temp.append(line)
                if duplicate is False:
                    temp.append([str(round(row[0], 0)), str(row[1])])
                with open('flow.csv', "w", newline='') as csvappend:
                    writer = csv.writer(csvappend)
                    for line in temp:
                        writer.writerow(line)


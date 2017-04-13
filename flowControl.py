#!/usr/bin/python
# coding=utf-8
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0621
# pylint: disable=W0312

import csv
import time
from gate import Gate
from Util.Synchronization import synchronized, Synchronization
from numpy.distutils.fcompiler import none
from flowDetection import FlowDetection
from stats import statistics


class FlowControl():
    
    gate = None
    FlowDetection = None
    statistics = None
    _sampleCount = 5
    _targetFlow = 0
    _csvData = {}
    _flowDiff = 0
    _gateOpening = 0
    _gateincrement = 1
    _initialGateOpening = 50
    _toleranceInPercent = 5
    _flows = []
    _ZeroFlowCount = 0
    _rumblemode = "coarse"
    _rumbleintverval = 2
        
    def __init__(self, gate, flowDetection, rumbler):
        self.rumbler = rumbler
        self.gate = gate
        self.flowDetection = flowDetection
        self.statistics = statistics(self._sampleCount)

        
    def start(self):
        self._rumbleintverval = 2
        print("STARTING FLOW CONTROL")
        self.setRumbleMode("coarse")
        try:
            self.readCSV("flow.csv")
            self._gateOpening = self.findGateOpeningCSV()
        except IOError:
            self._gateOpening = self._initialGateOpening
        self.setGate(self._gateOpening)
        self.statistics.reset()
        del self._flows[:]
        self.flowDetection.subscribe("FlowChanged", self)
    
    def setRumbleMode(self, mode):
        if mode == "fine" or mode == "coarse":
            self._rumblemode = mode
    
    def rumble(self):
        self._ZeroFlowCount = 0
        if self._rumblemode == "fine":
            self.rumbler.fine()
        elif self._rumblemode == "coarse":
            self.rumbler.coarse()
    
    def stop(self):
        self.setGate(0)
        self._gateOpening = 0
        self.flowDetection.unsubscribe("FlowChanged", self)
        self.statistics.reset()
    
    def setGate(self, perc):
        self._gateOpening = perc
        self.gate.execute(["P", perc])
    
    def GateUp(self):
        self._gateOpening += self._gateincrement
        self.setGate(self._gateOpening)
    
    def GateDown(self):
        self._gateOpening -= self._gateincrement
        self.setGate(self._gateOpening)
    
    def setTargetFlow(self, target):
        print("TARGET FLOW CHANGED TO :", target)
        self.statistics.reset()
        del self._flows[:]
        self._targetFlow = target
        
    def getTargetFlow(self):
        return float(self._targetFlow)
    
    def getAvgFlow(self):
        return self.statistics.getAvgY()
    
    def setIncrement(self, inc):
        print("SETTING GATEs INCREMENT TO",inc)
        self._gateincrement = inc
        
    def setSampleCount(self,cnt):
        self._sampleCount = cnt
        self.statistics.setMaxSampleCount(cnt)
    
    def getFlows(self):
        return self._flows
    
    def getTolerance(self):
        return ((float(self.getTargetFlow())/100) * self._toleranceInPercent)
    
    def onFlowChanged(self, flow):
        synchronized(self._internalOnFlowChanged(flow))
    
    def _internalOnFlowChanged(self, flow):
        if self._ZeroFlowCount >= self._rumbleintverval:
            self.rumble()
            return
        self.statistics.addSample(flow)
        self.findOpeningForFlow(self.statistics.getAvgY())
    
    def findOpeningForFlow(self, flow):
        if flow == 0:
            self._ZeroFlowCount += 1
        if self._targetFlow == 0:
            self.setGate(0)
        else:
            self._flows.append(flow)
            if not((float(self._targetFlow) + self.getTolerance()) >= float(flow) and float(flow) >= (float(self._targetFlow) - self.getTolerance())):
                if(self._targetFlow < flow and self._gateOpening >= self._gateincrement):
                    self.GateDown()
                    print("GATE DOWN", self._gateOpening, "Flow:", flow ,"(",self._targetFlow,")")
                elif self._targetFlow > flow and self._gateOpening <= 100-self._gateincrement:
                    print("GATE UP", self._gateOpening, "Flow:", flow ,"(",self._targetFlow,")")
                    self.GateUp()
            else:
                print("FLOW OK:", flow ,"(",self._targetFlow,")")
    
    def findGateOpeningCSV(self):
        print(len(self._csvData))
        for flow, opening in self._csvData.items():
            if flow == self._targetFlow:
                return opening
        return self._initialGateOpening
    
    def readCSV(self, path):
        with open(path , "r") as csvfile:
            reader = csv.reader(csvfile)
            self._csvData = {rows[0]:rows[1] for rows in reader}
        
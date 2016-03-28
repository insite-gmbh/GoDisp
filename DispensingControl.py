#!/usr/bin/python
# coding=utf-8
import time
from Util.Publisher import Publisher
from Util.Synchronization import *
import threading

class DispensingControl(Publisher, Synchronization):

	class ForceFlowChange(threading.Thread):
		def __init__(self, event, parent=None):
			threading.Thread.__init__(self)
			self.stopped = event
			self.parent = parent

		def run(self):
			while not self.stopped.wait(1.0):
				self.parent and self.parent.forceFlowChanges()

			
	CountSamples = 3
	Samples = []
	LastFlow = 0

	def __init__(self, scales, gate):
		Publisher.__init__(self, ["FlowChanged"])
		self.scales = scales
		self.gate = gate
		self.scales.subscribe("WeightChanged", self)
		Publisher.dispatch(self, "FlowChanged", self.LastFlow)
		self.stopFlowChangeForcer = threading.Event()
		self.flowChangeForcer = DispensingControl.ForceFlowChange(self.stopFlowChangeForcer, self)
		self.flowChangeForcer.start()

	def __del__(self):
		self.stopFlowChangeForcer.set()

	def forceFlowChanges(self):
		synchronized(self._internalForceFlowChanges())
		
	def _internalForceFlowChanges(self):
		if len(self.Samples) > 0:
			currentTS = int(round(time.time() * 1000))
			ts, w = self.Samples[len(self.Samples) - 1]
			if (currentTS - ts) >= 1000:
				print("appending artificial sample")
				self.Samples.append([currentTS, w])
				self._fireFlowEventIfNeeded()
		
	def onWeightChanged(self, weightAndState):
		synchronized(self._internalOnWeightChanged(weightAndState))

	def _internalOnWeightChanged(self, weightAndState):
		weight = weightAndState[0]
		self.Samples.append([int(round(time.time() * 1000)), weight])
		self._fireFlowEventIfNeeded()

	def _fireFlowEventIfNeeded(self):
		print("_fireFlowEventIfNeeded", len(self.Samples))
		if len(self.Samples) >= self.CountSamples:
			newFlow = self._calculateFlow()
			if newFlow != self.LastFlow:
				Publisher.dispatch(self, "FlowChanged", self._calculateFlow())
				self.LastFlow = newFlow
			while len(self.Samples) >= self.CountSamples:
				del self.Samples[0]
		print("EXIT _fireFlowEventIfNeeded", len(self.Samples))
		
	def _calculateFlow(self):
		count = 0
		flowSum = 0
		for i in range(1, len(self.Samples)):
			ts0, w0 = self.Samples[i - 1]
			ts1, w1 = self.Samples[i]
			print(ts0, w0)
			print(ts1, w1)
			flowSum += ((w1 - w0) * 1000000) // (ts1 - ts0)
			print("flowSum", flowSum)
			count += 1
		avg = int(flowSum / (count * 1000) + 0.5)
		print("avg", avg, "(", count, ")")
		return avg
	




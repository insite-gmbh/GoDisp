#!/usr/bin/python
# coding=utf-8
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0621
# pylint: disable=W0312

import threading
import time
from Util.Publisher import Publisher
from Util.Synchronization import synchronized, Synchronization


class FlowDetection(Publisher, Synchronization):

	class ForceFlowChange(threading.Thread):
		def __init__(self, event, parent=None):
			threading.Thread.__init__(self)
			self.stopped = event
			self.parent = parent

		def run(self):
			while not self.stopped.wait(1):
				self.parent and self.parent.forceFlowChanges()

	LastFlow = 0
	unchangedCount = 0
	Samples = []

	def __init__(self, scales):
		Publisher.__init__(self, ["FlowChanged"])
		self.scales = scales
		self.scales.subscribe("WeightChanged", self)
		Publisher.dispatch(self, "FlowChanged", self.LastFlow)
		self.stopFlowChangeForcer = threading.Event()
		self.flowChangeForcer = FlowDetection.ForceFlowChange(self.stopFlowChangeForcer, self)
		self.flowChangeForcer.start()

	def __del__(self):
		self.stopFlowChangeForcer.set()

	def forceFlowChanges(self):
		synchronized(self._internalForceFlowChanges())

	def _internalForceFlowChanges(self):
		if len(self.Samples) > 0:
			ts = time.time()
			tsLast = self.Samples[(len(self.Samples) - 1)][0]
			if (ts - tsLast > 1):
				wLast = self.Samples[(len(self.Samples) - 1)][1]
				print("Artificial Weight Sample:", ts, wLast)
				self.Samples.append([ts, wLast])
				self._fireFlowEvent()

	def onWeightChanged(self, weightAndState):
		synchronized(self._internalOnWeightChanged(weightAndState))

	def _internalOnWeightChanged(self, weightAndState):
		weight = weightAndState[0]
		self.Samples.append([time.time(), weight])
		self._fireFlowEvent()

	def _fireFlowEvent(self):
		if len(self.Samples) >= 2:
			newFlow = self._calculateFlow()
			Publisher.dispatch(self,"FlowChanged", newFlow)
			self.LastFlow = newFlow
			while len(self.Samples) >= 2:
				del self.Samples[0]

	def _calculateFlow(self):
		ts0, w0 = self.Samples[0]
		ts1, w1 = self.Samples[1]
		flow = (w1 - w0)
		passedtime = ts1 - ts0
		if flow > 0:
			fpm = (flow / passedtime) * 60
		else:
			fpm = 0
		return fpm





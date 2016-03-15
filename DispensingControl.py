#!/usr/bin/python
# coding=utf-8
import time
from Util.Publisher import Publisher

class DispensingControl(Publisher):
	
	CountSamples = 3
	Samples = []
	LastFlow = 0

	def __init__(self, scales, gate):
		Publisher.__init__(self, ["FlowChanged"])
		self.scales = scales
		self.gate = gate
		self.scales.subscribe("WeightChanged", self)
		Publisher.dispatch(self, "FlowChanged", self.LastFlow)

	def onWeightChanged(self, weightAndState):
		stable = weightAndState[1]
		if stable:
			Publisher.dispatch(self, "FlowChanged", 0)
			self.Samples = []
			return
		
		weight = weightAndState[0]
		
		self.Samples.append([int(round(time.time() * 1000)), weight])
		# print(len(self.Samples))
		if len(self.Samples) == self.CountSamples:
			newFlow = self._calculateFlow()
			if newFlow != self.LastFlow:
				Publisher.dispatch(self, "FlowChanged", self._calculateFlow())
				self.LastFlow = newFlow
			del self.Samples[0]

	def _calculateFlow(self):
		count = 0
		flowSum = 0
		for i in range(1, len(self.Samples)):
			ts0, w0 = self.Samples[i - 1]
			ts1, w1 = self.Samples[i]
			# print(ts0, w0)
			# print(ts1, w1)
			flowSum += ((w1 - w0) * 1000) // (ts1 - ts0)
			# print("flowSum", flowSum)
			count += 1
		avg = int(flowSum / count + 0.5)
		# print("avg", avg, "(", count, ")")
		return avg
	




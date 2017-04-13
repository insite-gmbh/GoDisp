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

class DispensingControl(Publisher, Synchronization):

	def __init__(self, dispensingRule, flowControl, scales):
		Publisher.__init__(self, ["DispensingStarted","DispensingFinished","PercentageReached","DispensingError"])
		self._dispensingRule = dispensingRule
		self._FlowControl = flowControl
		self._scales = scales
		self._currentWeight = 0
		self._targetWeight = None
		
	def start(self):
		print("START DISPENSING")
		self._rumblecounter = 0
		self._FlowControl.setSampleCount(self._dispensingRule.getSampleCountSetting())
		self._FlowControl.setIncrement(self._dispensingRule.getIncrementSetting())
		self._scales.subscribe("WeightChanged", self)
		self._FlowControl.setTargetFlow(self._dispensingRule.getFlowForWeight(0))
		self._targetWeight = self._dispensingRule.GetDestinationWeight()
		self._FlowControl.start()
		
	
	def stop(self):
		print("STOPPING DISPENSING CONTROL")
		self._FlowControl.stop()
		Publisher.dispatch(self, "DispensingFinished", True )
		self._scales.unsubscribe("WeightChanged", self)
		Publisher.dispatch(self,"PercentageReached", 100)
		
		
	def onWeightChanged(self,weight):
		synchronized(self._internalonWeightChanged(weight[0]))
		
	def _internalonWeightChanged(self,weight):
		self._currentWeight = weight
		if weight < self._targetWeight:
			if(self._targetWeight - weight > 10):
				self._FlowControl.setTargetFlow(int(self._dispensingRule.getFlowForWeight(weight)))
				self.firePercentageEvent(weight)
			else:
				self._FlowControl._rumbleintverval = 0
		else:
			self.stop()
			
	def firePercentageEvent(self,weight):
		if weight > 0:
			percentage = 100 / (self._targetWeight / weight);
			if(percentage % 5 < 1):
				if percentage < 95:
					Publisher.dispatch(self,"PercentageReached", percentage)
				elif percentage < 100:
					Publisher.dispatch(self,"PercentageReached", percentage)
				else:
					Publisher.dispatch(self,"PercentageReached", 100)
		else:
			Publisher.dispatch(self,"PercentageReached", 0)
	
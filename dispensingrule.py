#!/usr/bin/python
# coding=utf-8

class DispensingRule:

	@property
	def destinationWeight(self):
		return self.__destinationWeight
		
	@destinationWeight.setter
	def	destinationWeight(self, val):
		self.__destinationWeight = val
		
	def __init__(self):
		self.destinationWeight = 200
		
	def load(self):
		return
			
	def getOpeningForWeight(self, weight):
		percentageWeight = int(weight / self.destinationWeight * 100.0 + 0.5)
		if percentageWeight > 100:
			return 0
		else:	
			return 100 - percentageWeight
		
	def asString(self):
		s = ""
		for i in range(0, self.__destinationWeight, int(self.__destinationWeight / 10)):
			s += str(i)
			s += " - "
			s += str(self.getOpeningForWeight(i))
			s += "\n"
		s += str(self.__destinationWeight)
		s += " - "
		s += str(self.getOpeningForWeight(self.__destinationWeight))
		s += "\n"
		return s

#!/usr/bin/python
# coding=utf-8

# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0621
# pylint: disable=W0312

import sys
import csv

class DispensingRule:

	max_deviation = 0.02
	_table = []
	__destinationWeight = 0
	_settings = []

	def GetDestinationWeight(self):
		return self.__destinationWeight

	def	setDestinationWeight(self, val):
		print("NEW DESTINATION WEIGHT: ", val)
		self.__destinationWeight = val
	
	def getMaxDestinationWeight(self):
		return self._table[len(self._table)-1]

	def __init__(self, destWeight):
		self.__destinationWeight = destWeight
	
	def getIncrementSetting(self):
		if len(self._settings) > 0 and self._settings and int(self._settings[0][0]) > 0: 
			return int(self._settings[0][0])
		else:
			return 1
	
	def getSampleCountSetting(self):
		if len(self._settings) > 1 and self._settings and int(self._settings[0][1]) > 0: 
			return int(self._settings[0][1])
		else:
			return 5
				
	def load(self):
		print("LOADING DISPENSING RULE")
		self._table = []
		with open("rule.csv" , "r") as csvfile:
			reader = csv.reader(csvfile)
			self._settings.append(next(reader))
			print("Settings: ",self._settings[0][0], self._settings[0][1])
			for data in reader:
				self._table.append((data[0],data[1]))
	
	def getFlowForWeight(self, weight):
		for tuple in reversed(self._table):
			if(int(tuple[0]) <= float(weight)):
				print("weight ", float(weight), " targetFlow: ", int(tuple[1]))
				return int(tuple[1])
	
	def asString(self):
		s = "Target Weight: "
		s += str(self.__destinationWeight) + "\n"
		s += str("Gate Increment:"+str(self._settings[0][0]) +" \n")
		s += str("Flow Samples:"+str(self._settings[0][1]) +" \n")
		s += str("____________________\n")
		for tuple in self._table:
			s += str(tuple[0])
			s += " - "
			s += str(tuple[1])
			s += "\n"
		return s

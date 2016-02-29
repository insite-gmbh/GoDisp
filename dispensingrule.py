#!/usr/bin/python
# coding=utf-8
import sys
import csv

class DispensingRule:

	max_deviation = 0.02 
	
	@property
	def destinationWeight(self):
		return self.__destinationWeight
		
	@destinationWeight.setter
	def	destinationWeight(self, val):
		self.__destinationWeight = val
		self.__minTolerance = val 
		self.__maxTolerance = val + val * self.max_deviation
		
	def __init__(self):
		self.destinationWeight = 200
		self.table = [[0, 100], [100, 50], [150, 25], [190, 10], [195, 5]]
		
	def getTupleSortKey(self, tuple):
		return tuple[0]
		
	def load(self):
		print("in load")
		try: 
			self.table = []
			with open("./rule.csv") as f:
				firstLine = True
				c = csv.reader(f, delimiter=";")
				for line in c:
					if firstLine:
						self.destinationWeight = int(line[0])
						firstLine = False
					else:
						self.table.append([int(line[0]), int(line[1])])
			return
		except:
			e = sys.exc_info()[0]
			print( "Error: ", e)
			
	def getOpeningForWeight(self, weight):
		if weight > self.__maxTolerance:
			print("Destination weight ", self.__maxTolerance, " exceeded! BAD!")
			return -1

		if weight >= self.__minTolerance and weight <= self.__maxTolerance:
			print("Destination weight ", weight, " within tolerance (", self.__minTolerance, ", ", self.__maxTolerance, "). GOOD!")
			return -1
			
		for tuple in sorted(self.table, key=self.getTupleSortKey, reverse=True):
			print(tuple[0], tuple[1])
			if weight >= tuple[0]:
				print("weight ", weight, " returning ", tuple[1])
				return tuple[1]
		return 0
		
	def asString(self):
		s = "Destination weight: "
		s += str(self.destinationWeight) + "\n"
		for tuple in sorted(self.table, key=self.getTupleSortKey):
			s += str(tuple[0])
			s += " - "
			s += str(tuple[1])
			s += "\n"
		return s

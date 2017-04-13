#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2015  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0621
# pylint: disable=W0312

from tkinter import *
import time
import threading
import queue

from gate import Gate
from scales import Scales
from gui import GuiPart
from flowDetection import FlowDetection
from calibration import Calibration
from flowControl import FlowControl
from DispensingControl import DispensingControl
from DispensingRule import DispensingRule
from rumbler import rumbler
from lib2to3.pgen2.token import PERCENT

class ThreadedClient:

	gate = None
	scales = None
	FlowDetection = None
	DispensingRule = None
	DispensingControl = None
	calibration = None
	Rumbler = None
	flowControl = None
	tickCounter = 0
	_targetWeight = 200

	"""
	Launch the main part of the GUI and the worker thread. periodicCall and
	endApplication could reside in the GUI part, but putting them here
	means that you have all the thread controls in a single place.
	"""
	def __init__(self, master):
		"""
		Start the GUI and the asynchronous threads. We are in the main
		(original) thread of the application, which will later be used by
		the GUI. We spawn a new thread for the worker.
		"""
		self.master = master
		self.running = 1
		self.dispensing_state = 0

		# Create the queue
		self.queue = queue.Queue()

		# Set up the GUI part
		self.gui = GuiPart(master, self.queue, self.onEndApplication, self.onGUIMouseEvent, self.onGUIKeyEvent)

		self.gate = Gate(self.processOpeningChange)
		self.gate.start()
		self.gate.execute(["Z"])

		self.scales = Scales()
		self.scales.subscribe("WeightChanged", self)
		self.scales.start()
		self.scales.execute("T")
		self.scales.execute("Z")

		self.FlowDetection = FlowDetection(self.scales)
		self.FlowDetection.subscribe("FlowChanged", self)
		
		self.Rumbler = rumbler(self.gate)
		self.flowControl = FlowControl(self.gate, self.FlowDetection,self.Rumbler)
		
		self.DispensingRule = DispensingRule(self._targetWeight)
		self.DispensingRule.load()
		self.DispensingControl = DispensingControl(self.DispensingRule, self.flowControl, self.scales)
		self.DispensingControl.subscribe("DispensingFinished", self)
		self.DispensingControl.subscribe("PercentageReached", self)
				
		
		# Start the periodic call in the GUI to check if the queue contains
		# anything
		self.periodicCall()
		
	def updateTargetWeight(self, weight):
		self.DispensingRule.setDestinationWeight(int(weight))

	def processOpeningChange(self, sender, openingData):
		self.gui.update(["OpeningPercentage", openingData[0]])
		#self.gui.update(["OpeningSteps", openingData[1]])

	def onWeightChanged(self, weightAndState):
		weight = weightAndState[0]
		self.gui.update(["ActualWeight", weight])
	
	def onPercentageReached(self, percentage):
		print("GETTING PERCENTAGE REACHED:", percentage)
		if percentage >= 85:
			self.flowControl.setRumbleMode("fine")
		self.gui.update(["Progress",int(percentage)])
	
	def onDispensingFinished(self, success):
		self.dispensing_state = 0
		self.gui.update(["DispensingState", self.dispensing_state])

	def onFlowChanged(self, flow):
		self.gui.update(["ActualFlow", flow])
		if len(self.flowControl.getFlows()) > 0:
			flowsum = 0
			for i in self.flowControl.getFlows():
				flowsum += i
			avgFlow = flowsum / len(self.flowControl.getFlows())
			self.gui.update(["AverageFlow", avgFlow])
		else:
			self.gui.update(["AverageFlow", 0])

	def periodicCall(self):
		"""
		Check every 100 ms if there is something new in the queue.
		"""
		self.gui.processIncoming()
		if not self.running:
			# This is the brutal stop of the system. You may want to do
			# some cleanup before actually shutting it down.
			import sys
			print("Exiting Program")
			sys.exit(1)
		self.master.after(100, self.periodicCall)

	def onEndApplication(self):
		self.gate.execute(["C"])
		self.gate.execute("X")
		self.scales.execute("X")
		self.FlowDetection.__del__()
		print("before join")

		self.gate.join()
		self.scales.join()

		print("ready")

		self.running = 0

	def onGUIMouseEvent(self, event):
		if isinstance(event.widget, Button):
			btn_text = event.widget.cget("text")
			if btn_text == "Down":
				self.btn_down_click()
			if btn_text == "Rumble":
				self.btn_rumble_click()
			elif btn_text == "Up":
				self.btn_up_click()
			elif btn_text == "TickDn":
				self.btn_tickdown_click()
			elif btn_text == "TickUp":
				self.btn_tickup_click()
			elif btn_text == "Zero":
				self.btn_zero_click()
			elif btn_text == "Open":
				self.btn_open_click()
			elif btn_text == "Close":
				self.btn_close_click()
			elif btn_text == "Start":
				self.btn_startdispensing_click()
			elif btn_text == "Stop":
				self.btn_stopdispensing_click()
			elif btn_text == "Tare":
				self.btn_tare_click()
			elif btn_text == "Load Rule":
				self.btn_loadRule_click()
			elif btn_text == "set":
				self.btn_set_click()
			elif btn_text == "Recalibrate":
				self.btn_recalibrate_click()
			elif btn_text == "+":
				self.btn_plus_click()
			elif btn_text == "-":
				self.btn_minus_click()
		else:
			print("OnGUIMouseEVent error")
			print("widgetType = ", event.widget, ", x= ", event.x, ", y = ", event.y, ", num = ", event.num)
			
	def onGUIKeyEvent(self, event):
		if isinstance(event.widget, Button):
			btn_text = event.widget.cget("text")
			if btn_text == "+":
				self.btn_shift_plus_click()
			elif btn_text == "-":
				self.btn_shift_minus_click()
		else:
			print("onGUIKEyEvent Error")

	def btn_down_click(self):
		self.gate.execute(["S", 10])
	
	def btn_rumble_click(self):
		self.flowControl.rumble();

	def btn_up_click(self):
		self.gate.execute(["S", -10])

	def btn_tickdown_click(self):
		self.gate.execute(["S", 1])

	def btn_tickup_click(self):
		self.gate.execute(["S", -1])

	def btn_zero_click(self):
		self.gate.execute(["Z"])
		self.gui.update(["OpeningPercentage", 0])
		#self.gui.update(["OpeningSteps", 0])
	
	def btn_set_click(self):
		print("SET CLICKED")
		weight = int(self.gui.entry.get())
		self.gui.targetWeight = weight
		self.updateTargetWeight(weight)
		self.btn_loadRule_click()

	def btn_open_click(self):
		self.gate.execute(["O"])

	def btn_close_click(self):
		self.gate.execute(["C"])

	def btn_startdispensing_click(self):
		if self._targetWeight > 0:
			self.Rumbler.unblock()
			self.btn_tare_click()
			self.btn_set_click()
			self.btn_loadRule_click()
			self.DispensingControl.start()
			self.dispensing_state = 1
			self.gui.update(["AverageFlow", 0])
			self.gui.update(["DispensingState", self.dispensing_state])
		# self.periodicWeight()

	def btn_stopdispensing_click(self):
		self.DispensingControl.stop()
		self.dispensing_state = 0
		self.gui.update(["AverageFlow", 0])
		self.gui.update(["DispensingState", self.dispensing_state])

	def btn_tare_click(self):
		self.gui.update(["ActualWeight",0])
		self.scales.execute("T")

	def btn_loadRule_click(self):
		self.DispensingRule.load()
		self.gui.update(["LoadRule", self.DispensingRule.asString()])

	def btn_recalibrate_click(self):		
		self.clearCSV()
		self.startCalibration()
		
	def btn_shift_plus_click(self):
		self.flowControl.setTargetFlow(self.flowControl.getTargetFlow() + 100)
		self.gui.update(["Plus",self.flowControl.getTargetFlow()])
		
	def btn_shift_minus_click(self):
		if(self.flowControl.getTargetFlow() >= 100):
			self.flowControl.setTargetFlow(self.flowControl.getTargetFlow() - 100)
			self.gui.update(["Minus",self.flowControl.getTargetFlow()])
	
	def btn_plus_click(self):
		self.flowControl.setTargetFlow(self.flowControl.getTargetFlow() + 10)
		self.gui.update(["Plus",self.flowControl.getTargetFlow()])
		
	def btn_minus_click(self):
		if(self.flowControl.getTargetFlow() >= 10):
			self.flowControl.setTargetFlow(self.flowControl.getTargetFlow() - 10)
			self.gui.update(["Minus",self.flowControl.getTargetFlow()])
			
	
	def startCalibration(self):
		self.calibration = Calibration(self.FlowDetection, self.gate)
		self.calibration.start()

	def clearCSV(self):
		csvfile = open('flow.csv', "w+")
		csvfile.close()

def main():

	root = Tk()

	client = ThreadedClient(root)
	root.mainloop()

	x = 100
	while x > 0:
		client.FlowDetection.onWeightChanged([x, False])
		x = x - 1
	return 0

if __name__ == '__main__':
	main()




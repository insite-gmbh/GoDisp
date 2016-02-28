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
from tkinter import *
import time
import threading
import queue

from gate import Gate
from scales import Scales
from gui import GuiPart	
from dispensingrule import DispensingRule


class ThreadedClient:
	
	gate = None
	scales = None
	dispensingRule = None
	
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
		self.gui = GuiPart(master, self.queue, self.onEndApplication, self.onGUIEvent)

		self.gate = Gate(self.processOpeningChange)
		self.gate.start()
		self.gate.execute(["Z"])
		# self.gate.execute(["S", 100])
		# self.gate.execute(["S", -100])

		self.scales = Scales(self.processWeightChange)
		self.scales.start()
		self.scales.execute("T")
		self.scales.execute("Z")

		self.loadDispensingRule()


		# Start the periodic call in the GUI to check if the queue contains
		# anything
		self.periodicCall()

	def processOpeningChange(self, sender, openingData):
		self.gui.update(["OpeningPercentage", openingData[0]])
		self.gui.update(["OpeningSteps", openingData[1]])
		
	def processWeightChange(self, sender, weight):
		self.gui.update(["ActualWeight", weight])
		if self.dispensing_state == 1:
			self.gate.execute(["P", self.dispensingRule.getOpeningForWeight(weight)])
	

	def periodicCall(self):
		"""
		Check every 100 ms if there is something new in the queue.
		"""
		self.gui.processIncoming()
		if not self.running:
			# This is the brutal stop of the system. You may want to do
			# some cleanup before actually shutting it down.
			import sys
			sys.exit(1)
		self.master.after(100, self.periodicCall)


	def onEndApplication(self):
		self.gate.execute(["C"])
		self.gate.execute("X");
		self.scales.execute("X");
		print("before join")
		
		self.gate.join()
		self.scales.join()
		
		print("ready")
		
		self.running = 0

	def onGUIEvent(self, event):
		if isinstance(event.widget, Button):
			btn_text = event.widget.cget("text")
			if btn_text == "Down":
				self.btn_down_click()
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
			elif btn_text == "StartDispensing":
				self.btn_startdispensing_click()
			elif btn_text == "StopDispensing":
				self.btn_stopdispensing_click()
			elif btn_text == "LoadDispRule":
				self.btn_loaddispensingrule_click()
		else:	
			print("widgetType = ", typeof(event.widget), ", x= ", event.x, ", y = ", event.y, ", num = ", event.num)
			
	def btn_down_click(self):
		self.gate.execute(["S", 10])

	def btn_up_click(self):
		self.gate.execute(["S", -10])

	def btn_tickdown_click(self):
		self.gate.execute(["S", 1])

	def btn_tickup_click(self):
		self.gate.execute(["S", -1])

	def btn_zero_click(self):
		self.gate.execute(["Z"])

	def btn_open_click(self):
		self.gate.execute(["O"])

	def btn_close_click(self):
		self.gate.execute(["C"])

	def btn_startdispensing_click(self):
		self.dispensing_state = 1
		self.scales.execute(["T"])
		self.gate.execute(["O"])
		self.gui.update(["DispensingState", self.dispensing_state])

	def btn_stopdispensing_click(self):
		self.dispensing_state = 0
		self.gate.execute(["C"])
		self.gui.update(["DispensingState", self.dispensing_state])
		
	def btn_loaddispensingrule_click(self):
		self.loadDispensingRule()

	def loadDispensingRule(self):
		if self.dispensingRule is None:
			self.dispensingRule = DispensingRule()
		self.gui.update(["DispensingRule", self.dispensingRule.asString()])
		
def main():
	
	root = Tk()

	client = ThreadedClient(root)
	root.mainloop()
	
	return 0

if __name__ == '__main__':
	main()


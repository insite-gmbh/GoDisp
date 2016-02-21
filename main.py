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
import random
import queue

from gate import Gate
from scales import Scales
from gui import GuiPart	


class ThreadedClient:
	
	gate = Gate()
	scales = None
	rand = random.Random()

	
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

		# Create the queue
		self.queue = queue.Queue()

		# Set up the GUI part
		self.gui = GuiPart(master, self.queue, self.endApplication)

		# Set up the thread to do asynchronous I/O
		# More can be made if necessary
		self.running = 1
		self.thread1 = threading.Thread(target=self.workerThread1)
		self.thread1.start()

		self.gate.start()
		self.gate.execute(["S", 100])
		self.gate.execute(["S", -100])

		self.scales = Scales(self.processWeightChange)
		self.scales.start()
		self.scales.execute("T")
		self.scales.execute("Z")


		# Start the periodic call in the GUI to check if the queue contains
		# anything
		self.periodicCall()

	def processWeightChange(self, sender, weight):
		print(weight)
		if weight > 200:
			self.gate.execute(["C"])
		elif weight > 100:
			self.gate.execute([50])
		elif weight > 10:
			self.gate.execute([75])
		else:
			self.gate.execute(["O"])
		

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

	def workerThread1(self):
		"""
		This is where we handle the asynchronous I/O. For example, it may be
		a 'select()'.
		One important thing to remember is that the thread has to yield
		control.
		"""
		while self.running:
			# To simulate asynchronous I/O, we create a random number at
			# random intervals. Replace the following 2 lines with the real
			# thing.
			time.sleep(self.rand.random() * 0.3)
			msg = self.rand.random()
			self.queue.put(msg)

	def endApplication(self):
		self.gate.execute("X");
		self.scales.execute("X");
		print("before join")
		
		self.gate.join();
		self.scales.join();
		
		print("ready")
		
		self.running = 0



def main():
	
	root = Tk()

	client = ThreadedClient(root)
	root.mainloop()
	
	return 0

if __name__ == '__main__':
	main()


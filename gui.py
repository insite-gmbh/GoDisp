#!/usr/bin/python
# coding=utf-8
from tkinter import *
import tkinter.font as tkf
import signal

import queue
import threading
from time import sleep

class GuiPart:
	
	def __init__(self, master, queue, endCommand, handler):
		self.master = master
		self.queue = queue
		Button(self.master, text="Exit", command=endCommand, width=37).grid(column=0, row=10, sticky=W, columnspan=3)
		self.createAndBindButton("Down", handler, 2, 0)
		self.createAndBindButton("Up", handler, 0, 0)
		self.createAndBindButton("TickDn", handler, 2, 1)
		self.createAndBindButton("TickUp", handler, 0, 1)
		self.createAndBindButton("Zero", handler, 1, 1)
		self.createAndBindButton("Close", handler, 2, 2)
		self.createAndBindButton("Open", handler, 0, 2)

		self.actual_weight = IntVar()
		Label(self.master, text="Weight: ").grid(column=0, row=3)
		Label(self.master, textvariable=self.actual_weight).grid(column=1, row=3)

		self.actual_flow = IntVar()
		Label(self.master, text="Flow: ").grid(column=2, row=3)
		Label(self.master, textvariable=self.actual_flow).grid(column=4, row=3)

		self.opening_percentage = IntVar()
		Label(self.master, text="Opening: ").grid(column=0, row=4)
		Label(self.master, textvariable=self.opening_percentage).grid(column=1, row=4)

		self.opening_steps = IntVar()
		Label(self.master, textvariable=self.opening_steps).grid(column=2, row=4)

		self.start_stop_button = self.createAndBindButton("StartDispensing", handler, 0, 5)
		self.createAndBindButton("LoadDispRule", handler, 1, 5)
		
		self.dispensing_rule = StringVar()
		Label(self.master, textvariable=self.dispensing_rule).grid(column=0, row=6, columnspan=3, rowspan=4)

		master.protocol('WM_DELETE_WINDOW', endCommand)
		signal.signal(signal.SIGINT, endCommand)

	def createAndBindButton(self, text, handler, column, row):
		button = Button(self.master, text=text, width=10, height=1)
		button.grid(column=column, row=row, sticky=W)
		button.bind("<Button-1>", handler)
		return button
	
	def update(self, cmd):
		self.queue.put(cmd)
		
	def processIncoming(self):
		"""
		Handle all the messages currently in the queue (if any).
		"""
		while self.queue.qsize():
			try:
				msg = self.queue.get(0)
				if msg[0] == "ActualWeight":
					self.actual_weight.set(msg[1])
				elif msg[0] == "ActualFlow":
					self.actual_flow.set(msg[1])
				elif msg[0] == "OpeningPercentage":
					self.opening_percentage.set(msg[1])
				elif msg[0] == "OpeningSteps":
					self.opening_steps.set(msg[1])
				elif msg[0] == "DispensingRule":
					self.dispensing_rule.set(msg[1])
				elif msg[0] == "DispensingState":
					if msg[1] != 0:
						self.start_stop_button["text"] = "StopDispensing"
					else:
						self.start_stop_button["text"] = "StartDispensing"
					
			except:
				e = sys.exc_info()[0]
				print( "Error: ", e)
				


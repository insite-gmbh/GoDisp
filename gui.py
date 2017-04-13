#!/usr/bin/python
# coding=utf-8

# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0621
# pylint: disable=W0312


from tkinter import *
import tkinter.font as tkf
from tkinter import ttk
import signal
import queue
import threading
from time import sleep

class GuiPart():

	def __init__(self, master, queue, endCommand, mb_handler, btn_handler):
		self.master = master
		self.queue = queue
		Button(self.master, text="Exit", command=endCommand, width=37).grid(column=0, row=12, columnspan=3)
		self.createAndBindButton("Down", mb_handler, 2, 0)
		self.createAndBindButton("Up", mb_handler, 0, 0)
		self.createAndBindButton("Rumble", mb_handler, 1, 0)
		self.createAndBindButton("TickDn", mb_handler, 2, 1)
		self.createAndBindButton("TickUp", mb_handler, 0, 1)
		self.createAndBindButton("Zero", mb_handler, 1, 1)
		self.createAndBindButton("Tare", mb_handler, 1, 2)
		self.createAndBindButton("Close", mb_handler, 2, 2)
		self.createAndBindButton("Open", mb_handler, 0, 2)
		self.createAndBindButton("Load Rule", mb_handler, 1, 8)
		self.createAndBindButton("Recalibrate", mb_handler, 2, 8)
				
		Label(self.master, text="Opening: ").grid(column=0, row=4)
		
		self.targetFlow = IntVar()
		Label(self.master, textvariable=self.targetFlow).grid(column=2, row=6)
		Label(self.master, text="Target Flow").grid(column=2, row=5)
		Label(self.master, text="Target Weight").grid(column=2, row=3)
		
		self.targetWeight=StringVar()
		self.entry =  Entry(self.master, textvariable = self.targetWeight, width = 10)
		self.entry.grid(column=2, row=4, sticky=W)
		self.entry.delete(0, END)
		self.entry.insert(0, "0")
		
		setbtn = Button(self.master, text="set", height = 0, width=0)
		setbtn.grid(column=2, sticky=E, row=4)
		setbtn.bind("<Button-1>", mb_handler)
		setbtn.bind("<Shift-Button-1>", btn_handler)
		
			
		b1 = Button(self.master, text="+", height = 0, width=0)
		b1.grid(column=2, sticky=E, row=6)
		b1.bind("<Button-1>", mb_handler)
		b1.bind("<Shift-Button-1>", btn_handler)
		
		b2 = Button(self.master, text="-",height = 0, width=0)
		b2.grid(column=2, sticky=W, row=6)
		b2.bind("<Button-1>", mb_handler)
		b2.bind("<Shift-Button-1>", btn_handler)

		self.actual_weight = IntVar()
		Label(self.master, text="Weight: ").grid(column=0, row=3)
		Label(self.master, textvariable=self.actual_weight).grid(column=1, row=3)
		
		self.progressdiff = StringVar()
		Label(self.master, textvariable = self.progressdiff ).grid(column=1, row=10)

		self.actual_flow = IntVar()
		Label(self.master, text="Current Flow: ").grid(column=0, row=5)
		Label(self.master, textvariable=self.actual_flow).grid(column=1, row=5)
		
		self.average_flow = IntVar()
		Label(self.master, text="Average Flow: ").grid(column=0, row=6)
		Label(self.master, textvariable=self.average_flow).grid(column=1, row=6)

		self.opening_percentage = IntVar()
		Label(self.master, text="Opening: ").grid(column=0, row=4)
		Label(self.master, textvariable=self.opening_percentage).grid(column=1, row=4)
		
		self.dispensing_rule = StringVar()
		Label(self.master, textvariable=self.dispensing_rule).grid(column=4, row=0, columnspan=3, rowspan=10)

		self.progress = ttk.Progressbar(self.master, orient="horizontal",length=250, mode="determinate")
		self.progress.grid(column=0, row=9, columnspan = 3)
		self.progress["value"] = 0
		self.maxprogress = 100
		self.progress["maximum"] = 100
		
		#self.opening_steps = IntVar()
		#Label(self.master, textvariable=self.opening_steps).grid(column=2, row=4)

		self.start_stop_button = self.createAndBindButton("Start", mb_handler, 0, 8)
		#self.dispensing_rule = StringVar()
		#Label(self.master, textvariable=self.dispensing_rule).grid(column=0, row=6, columnspan=3, rowspan=4)

		master.protocol('WM_DELETE_WINDOW', endCommand)
		signal.signal(signal.SIGINT, endCommand)

	def closeGUI(self):
		self.master.destroy

	def createAndBindButton(self, text, handler, column, row):
		button = Button(self.master, text=text, width=10, height=1)
		button.grid(column=column, row=row, sticky=E)
		button.bind("<Button-1>", handler)
		return button

	def update(self, cmd):
		self.queue.put(cmd)
	
	def processIncoming(self):
		"""
		Handle all the messages currently in the queue (if any).
		"""
		while self.queue.qsize():
			msg = self.queue.get(0)
			if msg[0] == "ActualWeight":
				self.actual_weight.set(msg[1])
				self.progressdiff.set(str(msg[1])+"/"+str(self.targetWeight))
			elif msg[0] == "ActualFlow":
				self.actual_flow.set(msg[1])
			elif msg[0] == "Progress":
				self.progress["value"] = msg[1]
			elif msg[0] == "AverageFlow":
				self.average_flow.set(msg[1])
			elif msg[0] == "OpeningPercentage":
				self.opening_percentage.set(msg[1])
			elif msg[0] == "OpeningSteps":
				self.bytes.set(msg[1])
			elif msg[0] == "LoadRule":
				self.dispensing_rule.set(msg[1])
			elif msg[0] == "Plus":
				self.targetFlow.set(msg[1])
			elif msg[0] == "Minus":
				self.targetFlow.set(msg[1])
			elif msg[0] == "DispensingRule":
				self.dispensing_rule.set(msg[1])
			elif msg[0] == "DispensingState":
				if msg[1] != 0:
					self.start_stop_button["text"] = "Stop"
				else:
					self.start_stop_button["text"] = "Start"


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

from gate import Gate

def main():
	gate = Gate()
	gate.start()
	print("O")
	gate.execute("O")
	print("C")
	
	gate.execute("C")
	print("50")
	gate.execute("50")
	print("75")
	gate.execute("75")
	print("25")
	gate.execute("25")
	print("0")
	gate.execute("0");
	print("X")
	gate.execute("X");
	print("before join")
	
	gate.join();
	print("ready")
	
	return 0

if __name__ == '__main__':
	main()


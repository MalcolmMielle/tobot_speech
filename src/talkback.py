#!/usr/bin/env python

"""
    talkback.py - Version 0.1 2012-01-10
    
    Use the sound_play client to say back what is heard by the pocketsphinx recognizer.
    
    Created for the Pi Robot Project: http://www.pirobot.org
    Copyright (c) 2012 Patrick Goebel.  All rights reserved.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.5
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details at:
    
    http://www.gnu.org/licenses/gpl.htmlPoint
"""

import roslib; roslib.load_manifest('rbx1_speech')
import rospy
import datetime
import time

from std_msgs.msg import String
from sound_play.libsoundplay import SoundClient
import sys

class TalkBack:
	def __init__(self, script_path):
		rospy.init_node('talkback')

		rospy.on_shutdown(self.cleanup)

		# Set the default TTS voice to use
		self.voice = rospy.get_param("~voice", "voice_don_diphone")

		# Set the wave file path if used
		self.wavepath = rospy.get_param("~wavepath", script_path + "/../sounds")

		# Create the sound client object
		self.soundhandle = SoundClient()

		self.keywords_to_command = {'time': ['time','what time is it'],
						'face' : ['face', 'follow me', 'look at me'],
						'stoplook' : ['stop looking', 'who you looking at']
				     }

		# Wait a moment to let the client connect to the
		# sound_play server
		rospy.sleep(1)

		# Make sure any lingering sound_play processes are stopped.
		self.soundhandle.stopAll()

		# Announce that we are ready for input
		self.soundhandle.playWave(self.wavepath + "/R2D2a.wav")
		rospy.sleep(1)
		self.soundhandle.say("What do you want me to do, master", self.voice)

		rospy.loginfo("Say one of the navigation commands...")

		# Subscribe to the recognizer output and set the callback function
		rospy.Subscriber('/recognizer/output', String, self.talkback)
 
 
	def get_command(self, data):
	  # Attempt to match the recognized word or phrase to the 
	  # keywords_to_command dictionary and return the appropriate
	  # command
		for (command, keywords) in self.keywords_to_command.iteritems():
			for word in keywords:
		    		if data.find(word) > -1:
			  		return command
		return data
        
	def talkback(self, msg):
		# Print the recognized words on the screen
		rospy.loginfo(msg.data)
		command = self.get_command(msg.data)
		
		print(command)
		
		# Speak the recognized words in the selected voice
		if command == 'time':
			now = datetime.datetime.now()
			now_str=now.strftime(" the year is %Y the month is %m and we are the %d. The time is %H:%M:%S")
			rospy.loginfo(now_str)
			self.soundhandle.say(now_str, self.voice)
		if command=='face':
			self.soundhandle.say("I'm looking at you now", self.voice)
		if command=='stoplook':
			self.soundhandle.say("I'll stop looking at you", self.voice)
		else : 
			self.soundhandle.say(command, self.voice)

		# Uncomment to play one of the built-in sounds
		#rospy.sleep(2)
		#self.soundhandle.play(5)

		# Uncomment to play a wave file
		#rospy.sleep(2)
		#self.soundhandle.playWave(self.wavepath + "/R2D2a.wav")

	def cleanup(self):
		self.soundhandle.stopAll()
		rospy.loginfo("Shutting down talkback node...")

if __name__=="__main__":
	try:
		TalkBack(sys.path[0])
		rospy.spin()
	except rospy.ROSInterruptException:
		rospy.loginfo("Talkback node terminated.")

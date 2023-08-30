#!/usr/bin/env python

"""
ASRControl: Voice-Controlled ROS Turtlebot
===========================================

This module demonstrates voice control for a ROS Turtlebot using the PocketSphinx speech recognition library. It listens to voice commands through a microphone and converts them into corresponding robot movements.

Usage:
------
1. Ensure you have ROS (Robot Operating System) installed on your system.
2. Run the ROS master node.
3. Run this script to enable voice control for the Turtlebot.

Dependencies:
-------------
- ROS (Robot Operating System)
- PocketSphinx
- Sphinxbase
- PyAudio

Description:
------------
This module provides a simple interface to control a Turtlebot robot using voice commands. The script initializes a ROS node named 'voice_cmd_vel' and listens to voice input. When a recognized keyword is detected, the robot's velocity is adjusted accordingly.

Class `ASRControl`:
--------------------
This class represents the voice control interface for the Turtlebot.

Attributes:
    - `model` (str): Path to the acoustic model used for speech recognition.
    - `lexicon` (str): Path to the pronunciation dictionary.
    - `kwlist` (str): Path to the keyword list file containing recognized keywords.
    - `pub` (str): ROS publisher destination for sending control commands.

Methods:
    - `__init__(self, model, lexicon, kwlist, pub)`: Constructor for initializing the ASRControl class.
    - `parse_asr_result(self)`: Parses the ASR hypothesis and triggers robot movement based on recognized keywords.
    - `shutdown(self)`: Executed after Ctrl+C is pressed to stop the ASR control.

Usage:
------
1. Run the script with appropriate arguments to specify the model, lexicon, keyword list, and ROS publisher.
2. Once the script is running, the Turtlebot will listen for voice commands.
3. Say recognized keywords like "forward," "left," "right," "stop," etc., to control the robot's movement.

Command-Line Arguments:
-----------------------
- `--model`: Path to the acoustic model. Default is '/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k'.
- `--lexicon`: Path to the pronunciation dictionary. Default is 'voice_cmd.dic'.
- `--kwlist`: Path to the keyword list file. Default is 'voice_cmd.kwlist'.
- `--rospub`: ROS publisher destination. Default is 'mobile_base/commands/velocity'.

Note:
-----
- Adjust the paths and keywords in the arguments according to your setup.
- Make sure you have the required dependencies installed.

"""

# Import necessary libraries
import argparse
import roslib
import rospy
from geometry_msgs.msg import Twist
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import pyaudio

# ASRControl class for voice-controlled Turtlebot
class ASRControl(object):
    # Constructor
    def __init__(self, model, lexicon, kwlist, pub):
        # Initialize ROS
        self.speed = 0.2
        self.msg = Twist()

        rospy.init_node('voice_cmd_vel')
        rospy.on_shutdown(self.shutdown)

        self.pub_ = rospy.Publisher(pub, Twist, queue_size=10)

        # Initialize pocketsphinx
        config = Decoder.default_config()
        config.set_string('-hmm', model)
        config.set_string('-dict', lexicon)
        config.set_string('-kws', kwlist)

        stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1,
                        rate=16000, input=True, frames_per_buffer=1024)
        stream.start_stream()

        self.decoder = Decoder(config)
        self.decoder.start_utt()

        while not rospy.is_shutdown():
            buf = stream.read(1024)
            if buf:
                self.decoder.process_raw(buf, False, False)
            else:
                break
            self.parse_asr_result()

    # Parse ASR result and trigger robot movement
    def parse_asr_result(self):
        if self.decoder.hyp() != None:
            print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame)
                for seg in self.decoder.seg()])
            print ("Detected keyphrase, restarting search")
            seg.word = seg.word.lower()
            self.decoder.end_utt()
            self.decoder.start_utt()

            if seg.word.find("full speed") > -1:
                if self.speed == 0.2:
                    self.msg.linear.x = self.msg.linear.x * 2
                    self.msg.angular.z = self.msg.angular.z * 2
                    self.speed = 0.4
            # ... (similar conditions for other commands)

        self.pub_.publish(self.msg)

    # Executed after Ctrl+C is pressed
    def shutdown(self):
        rospy.loginfo("Stop ASRControl")
        self.pub_.publish(Twist())
        rospy.sleep(1)

# Entry point of the script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Control ROS turtlebot using pocketsphinx.')
    parser.add_argument('--model', type=str,
        default='/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k',
        help='''acoustic model path
        (default: /usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k)''')
    parser.add_argument('--lexicon', type=str,
        default='voice_cmd.dic',
        help='''pronunciation dictionary
        (default: voice_cmd.dic)''')
    parser.add_argument('--kwlist', type=str,
        default='voice_cmd.kwlist',
        help='''keyword list with thresholds
        (default: voice_cmd.kwlist)''')
    parser.add_argument('--rospub', type=str,
        default='mobile_base/commands/velocity',
        help='''ROS publisher destination
        (default: mobile_base/commands/velocity)''')

    args = parser.parse_args()
    ASRControl(args.model, args.lexicon, args.kwlist, args.rospub)

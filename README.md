# Voice control for ROS turtlebot with pocketsphinx

The script shows how to control ROS turtlebot 
with English keywords using pocketsphinx

This script:
- enables the keyword search mode, which should better filter not needed words
- uses pocketsphinx-python instead of Gstreamer
- is really simple (just a script to run)

It was currently tested only for linux and ROS Indigo turtlebot

## Installation

### Install pocketsphinx with dependencies

```
sudo apt-get install -y python python-dev python-pip build-essential swig libpulse-dev git
sudo pip install pyaudio
sudo pip install pocketsphinx
```

## Running an example 

Run turtlebot environment:

```
roslaunch turtlebot_gazebo turtlebot_world.launch
```

In a separate terminal run the script:

```
python ros_voice_control.py
```

Default commands ( forward / move / stop / left / right / back / full speed / half speed )



#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO
import time

R,G,B=15,18,14

# 按钮输出针脚连接的GPIO口
btnR, btnG, btnB=21,20,16

RPi.GPIO.setmode(RPi.GPIO.BCM)

RPi.GPIO.setup(R, RPi.GPIO.OUT)
RPi.GPIO.setup(G, RPi.GPIO.OUT)
RPi.GPIO.setup(B, RPi.GPIO.OUT)

# 按钮连接的GPIO针脚的模式设置为信号输入模式，同时默认拉高GPIO口电平，
# 当GND没有被接通时，GPIO口处于高电平状态，取的的值为1
# 注意到这是一个可选项，如果不在程序里面设置，通常的做法是通过一个上拉电阻连接到VCC上使之默认保持高电平
RPi.GPIO.setup(btnR, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(btnG, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(btnB, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

try:

	t = 0.4
	RPi.GPIO.output(R, True)
	RPi.GPIO.output(G, True)
	RPi.GPIO.output(B, True)
	while True:
		time.sleep(0.01)
		
		# 检测红色按钮是否被按下，如果被按下(低电平)，则亮红灯(输出低电平)，否则关红灯
		if (RPi.GPIO.input(btnR) == 0):
			RPi.GPIO.output(R, False)
		else:
			RPi.GPIO.output(R, True)
		
		# 检测绿色按钮是否被按下，如果被按下(低电平)，则亮红绿灯(输出低电平)，否则关绿灯
		if (RPi.GPIO.input(btnG) == 0):
			RPi.GPIO.output(G, False)
		else:
			RPi.GPIO.output(G, True)
		
		# 检测蓝色按钮是否被按下，如果被按下(低电平)，则亮蓝灯(输出低电平)，否则关蓝灯
		if (RPi.GPIO.input(btnB) == 0):
			RPi.GPIO.output(B, False)
		else:
			RPi.GPIO.output(B, True)

except KeyboardInterrupt:
	pass

RPi.GPIO.cleanup()

#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO
import time

# 串行数据输入
DIN = 13

# 时钟脉冲信号——上升沿有效
LOAD = 26

# 打入信号————上升沿有效
CLK = 19

RPi.GPIO.setmode(RPi.GPIO.BCM)

RPi.GPIO.setup(DIN, RPi.GPIO.OUT)
RPi.GPIO.setup(LOAD, RPi.GPIO.OUT)
RPi.GPIO.setup(CLK, RPi.GPIO.OUT)

# 传输一个8位数
def setByte(byteData):
	# print ""
	# print "S-----------setByte---------------:", hex(byteData)
	for bit in range(0,8):
		# 传入的数字从高位到低位依次判断是否为1，若为1则设置高电平，否则设置低电平
		# 判断的方法是先向左移位，把要判断的位移动到最高位然后跟0x80（1000 0000）相与，
		# 如果结果仍然是0x80（1000 0000）就表示最高位是1，否则最高位就是0
		if ((byteData<<bit) & 0x80 == 0x80):
			setBitData(True)
			# print "1",
		else:
			setBitData(False)
			# print "0",
	# print ""
	# print "E-----------setByte---------------"

# 译码模式设置
def setDecodeMode(mode = 4):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xX9
	# D15-D12:任意
	# D11,10,9,8: 1,0,0,1
	setByte(0x09)
	
	if (mode == 1) :
		# 所有数码管均不使用译码功能
		# 指令代码: 0x00
		setByte(0x00)
	elif (mode == 2) :
		# 只对DIG0号数码管进行译码，其他数码管不使用译码功能
		# 指令代码: 0x01
		setByte(0x01)
	elif (mode == 3) :
		# 对DIG0-3号数码管进行译码，其他数码管不使用译码功能
		# 指令代码: 0x0F
		setByte(0x0f)
	elif (mode == 4) :
		# 数码管7－0全部采用译码模式
		# 指令代码: 0xFF
		setByte(0xff)

	RPi.GPIO.output(LOAD, True)

# 亮度设置
def setIntensity(mode = 8):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXA
	# D15-D12:任意
	# D11,10,9,8: 1,0,1,0
	setByte(0x0A)
	
	# 亮度从0到15共16个等级，指令的D3－D0就是数字0－15的二进制编码
	# D7-D4:任意
	setByte(mode)

	RPi.GPIO.output(LOAD, True)

# 扫描显示位数设置(0-7)
def setScanLimit(mode = 7):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXB
	# D15-D12:任意
	# D11,10,9,8: 1,0,1,1
	setByte(0x0B)
	
	# 扫描位数可设置0－7共8种选择，指令的D2－D0就是数字0－7的二进制编码
	# D7-D3:任意
	# D2-D0:0-7的3位二进制编码
	setByte(mode)

	RPi.GPIO.output(LOAD, True)

# 关断模式设置
# mode: 1: 正常运行模式
# mode: 0: 关断模式
def setShutdownMode(mode = 1):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXC
	# D15-D12:任意
	# D11,10,9,8: 1,1,0,0
	setByte(0x0C)
	
	# 关断模式可设置0－1共2种选择，设置D0即可
	# D7-D1:任意
	# D0:1: 正常运行模式 0: 关断模式
	setByte(mode)

	RPi.GPIO.output(LOAD, True)

# 测试模式设置
# mode=0: 正常运行模式
# mode=1: 测试模式(全亮模式)
def setDisplayTestMode(mode = 0):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXF
	# D15-D12:任意
	# D11,10,9,8: 1,1,1,1
	setByte(0x0f)
	
	# 测试模式可设置0－1共2种选择，设置D0即可
	# D7-D1:任意
	# D0:0: 正常运行模式 1: 测试模式(全亮模式)
	setByte(mode)

	RPi.GPIO.output(LOAD, True)

# 指定no(1-8)号数码管显示数字num(0-9)，第三个参数是显示不显示小数点（true/false）
def showDigit(no, num, showDotPoint):

	RPi.GPIO.output(LOAD, False)

	# 设置指令寄存器地址：0xX1-0xX8
	# 格式：D15-D12:任意（我们这里设置0）
	#       D11-D8: 1-8的4位二进制编码：例：1（0,0,0,1）
	setByte(no)

	# 设置显示内容
	# 格式：D7:显示小数点（1点亮）
	#       D6-D4:任意（我们这里设置0）
	#       D3-D0:数字0-9的4位二进制编码：例：2（0,0,1,0）
	if (showDotPoint):
		# 如果显示小数点则需要将数字的最高位（D7）设置为1(最高位跟1相或)
		setByte(num | 0x80)
	else:
		setByte(num)

	RPi.GPIO.output(LOAD, True)

def setBitData(data):
	RPi.GPIO.output(CLK, False)
	RPi.GPIO.output(DIN, data)
	RPi.GPIO.output(CLK, True)

try:
	# 测试代码，亮度使用最低亮度，显示从0开始递增的数字。
	# print "=====================setShutdownMode====================="
	setShutdownMode()
	# print "=====================setDecodeMode====================="
	setDecodeMode()
	# print "=====================setIntensity====================="
	setIntensity(1)
	# print "=====================setScanLimit====================="
	setScanLimit()
	# print "=====================setDisplayTestMode====================="
	setDisplayTestMode()

	n=0
	while True:
		n=n+1
		showDigit(8, int(n)%10, False)
		showDigit(7, int(n/10)%10, False)
		showDigit(6, int(n/100)%10, False)
		showDigit(5, int(n/1000)%10, False)
		showDigit(4, int(n/10000)%10, False)
		showDigit(3, int(n/100000)%10, False)
		showDigit(2, int(n/1000000)%10, False)
		showDigit(1, int(n/10000000)%10, False)
		time.sleep(0.01)
except KeyboardInterrupt:
	pass

# 最后清理GPIO口（不做也可以，建议每次程序结束时清理一下，好习惯）
RPi.GPIO.cleanup()

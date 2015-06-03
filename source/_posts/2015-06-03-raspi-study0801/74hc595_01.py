#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO
import time

# 串行数据输入引脚连接的GPIO口
DS = 13

# 移位寄存器时钟控制引脚连接的GPIO口——上升沿有效
SHCP = 19

# 数据锁存器时钟控制引脚连接的GPIO口——上升沿有效
STCP = 26

RPi.GPIO.setmode(RPi.GPIO.BCM)

RPi.GPIO.setup(DS, RPi.GPIO.OUT)
RPi.GPIO.setup(STCP, RPi.GPIO.OUT)
RPi.GPIO.setup(SHCP, RPi.GPIO.OUT)

RPi.GPIO.output(STCP, False)
RPi.GPIO.output(SHCP, False)

# 通过串行数据引脚向74HC595的传送一位数据
def setBitData(data):
	# 准备好要传送的数据
	RPi.GPIO.output(DS, data)
	# 制造一次移位寄存器时钟引脚的上升沿（先拉低电平再拉高电平）
	# 74HC595会在这个上升沿将DS引脚上的数据存入移位寄存器D0
	# 同时D0原来的数据会顺移到D1，D1的数据位移到D2。。。D6的数据位移到D7
	# 而D7的数据已经没有地方储存了，这一位数据会被输出到引脚Q7S上
	# 如果Q7S引脚没有被使用，那么这一位的数据就被丢掉了。
	# 而如果将Q7S引脚连接到另一块74HC595上的DS引脚，
	# 那么这一位数据就会继续位移到第二块595芯片的位移寄存器里去。
	# 这就是多块595芯片级联的原理。
	RPi.GPIO.output(SHCP, False)
	RPi.GPIO.output(SHCP, True)

# 指定数码管显示数字num(0-9)，第2个参数是显示不显示小数点（true/false）
# 由于我使用的数码管是共阳数码管，所以设置为低电平的段才会被点亮
# 如果你用的是共阴数码管，那么要将下面的True和False全部颠倒过来，或者统一在前面加上not
def showDigit(num, showDotPoint):
	
	if (num == 0) :
		setBitData(not showDotPoint) # DP
		setBitData(True)  # G
		setBitData(False) # F
		setBitData(False) # E
		setBitData(False) # D
		setBitData(False) # C
		setBitData(False) # B
		setBitData(False) # A
	elif (num == 1) :
		setBitData(not showDotPoint)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
	elif (num == 2) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
	elif (num == 3) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (num == 4) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
	elif (num == 5) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
	elif (num == 6) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
	elif (num == 7) :
		setBitData(not showDotPoint)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (num == 8) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (num == 9) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)

	# 移位寄存器的8位数据全部传输完毕后，制造一次锁存器时钟引脚的上升沿（先拉低电平再拉高电平）
	# 74HC595会在这个上升沿将移位寄存器里的8位数据复制到8位的锁存器中（锁存器里原来的数据将被替换）
	# 到这里为止，这8位数据还只是被保存在锁存器里，并没有输出到数码管上。
	# 决定锁存器里的数据是否输出是由“输出使能端口”OE决定的。当OE设置为低电平时，锁存器里数据才会被输出到Q0-Q7这8个输出引脚上。
	# 在我的硬件连接里，OE直接连接在了GND上，总是保持低电平，所以移位寄存器的数据一旦通过时钟上升沿进入锁存器，也就相当于输出到LED上了。
	RPi.GPIO.output(STCP, True)
	RPi.GPIO.output(STCP, False)

try:
	# 测试代码
	# 从0显示到9，不显示小数点
	for x in range(0,10):
		showDigit(x, False)
		time.sleep(0.2)

	# 再从0显示到9，显示小数点
	for y in range(0,10):
		showDigit(y, True)
		time.sleep(0.2)
					
except KeyboardInterrupt:
	pass

# 最后清理GPIO口
# 清理了IO是将所有使用中的IO口释放，并全部设置为输入模式
# 你会发现最后设置的数据在清理了IO口以后还会继续正常显示
# 这是因为数据一旦存入锁存器，除非断电或重置数据（MR口设置为低电平），
# 否则最后设置的数据会一直保留在74HC595芯片中。也就是被“锁存”了。
RPi.GPIO.cleanup()

#!/usr/bin/env python
# encoding: utf-8
 
import RPi.GPIO as GPIO
import time
import numpy as np
import struct
import random

cs=23		# 片选
rs=17		# 数据 / 命令 切换
sda=13		# 数据
scl=19		# 时钟
reset=27	# 复位

# 传输byte
def setByteData(data):
	# print ""
	# print "S-----------setByte---------------:", hex(data)
	for bit in range(0,8):
		# 传入的数字从高位到低位依次判断是否为1，若为1则设置高电平，否则设置低电平
		# 判断的方法是先向左移位，把要判断的位移动到最高位然后跟0x80（1000 0000）相与，
		# 如果结果仍然是0x80（1000 0000）就表示最高位是1，否则最高位就是0
		if ((data<<bit) & 0x80 == 0x80):
			setBitData(True)
			# print "1",
		else:
			setBitData(False)
			# print "0",
	# print ""
	# print "E-----------setByte---------------"

def setBitData(data):
	GPIO.output(scl, False)
	GPIO.output(sda, data)
	GPIO.output(scl, True)

def write_command(cmd):
	GPIO.output(cs, False)
	GPIO.output(rs, False)
	setByteData(cmd)
	GPIO.output(cs, True)

def write_data(byteData):
	GPIO.output(cs, False)
	GPIO.output(rs, True)
	setByteData(byteData)
	GPIO.output(cs, True)

def write_data_8bitH_8bitL(bit8DataH, bit8DataL):
	write_data(bit8DataH)
	write_data(bit8DataL)

def write_data_16bitHL(bit16DataHL):
	write_data(bit16DataHL>>8)
	write_data(bit16DataHL&0xff)

def lcd_reset():
    GPIO.output(reset, False)
    time.sleep(0.1)
    GPIO.output(reset, True)
    time.sleep(0.1)

def lcd_init():
	lcd_reset()

	#------------------------------------------------------------------#   
	#-------------------Software Reset-------------------------------# 
	write_command(0x11) # Exit Sleep
	time.sleep(0.02)
	write_command(0x26) # Set Default Gamma
	write_data(0x04)
	write_command(0xB1)# Set Frame Rate
	write_data(0x0e)
	write_data(0x10)
	write_command(0xC0) # Set VRH1[4:0] & VC[2:0] for VCI1 & GVDD
	write_data(0x08)
	write_data(0x00)
	write_command(0xC1) # Set BT[2:0] for AVDD & VCL & VGH & VGL
	write_data(0x05)
	write_command(0xC5) # Set VMH[6:0] & VML[6:0] for VOMH & VCOML
	write_data(0x38)
	write_data(0x40)

	write_command(0x3a) # Set Color Format
	write_data(0x05)
	write_command(0x36) # RGB
	write_data(0xc8)

	write_command(0x2A) # Set Column Address
	write_data(0x00)
	write_data(0x00)
	write_data(0x00)
	write_data(0x7F)
	write_command(0x2B) # Set Page Address
	write_data(0x00)
	write_data(0x00)
	write_data(0x00)
	write_data(0x7F)

	write_command(0xB4) 
	write_data(0x00)

	write_command(0xf2) # Enable Gamma bit
	write_data(0x01)
	write_command(0xE0) 
	write_data(0x3f)# p1
	write_data(0x22)# p2
	write_data(0x20)# p3
	write_data(0x30)# p4
	write_data(0x29)# p5
	write_data(0x0c)# p6
	write_data(0x4e)# p7
	write_data(0xb7)# p8
	write_data(0x3c)# p9
	write_data(0x19)# p10
	write_data(0x22)# p11
	write_data(0x1e)# p12
	write_data(0x02)# p13
	write_data(0x01)# p14
	write_data(0x00)# p15
	write_command(0xE1) 
	write_data(0x00)# p1
	write_data(0x1b)# p2
	write_data(0x1f)# p3
	write_data(0x0f)# p4
	write_data(0x16)# p5
	write_data(0x13)# p6
	write_data(0x31)# p7
	write_data(0x84)# p8
	write_data(0x43)# p9
	write_data(0x06)# p10
	write_data(0x1d)# p11
	write_data(0x21)# p12
	write_data(0x3d)# p13
	write_data(0x3e)# p14
	write_data(0x3f)# p15

	write_command(0x29) #  Display On
	write_command(0x2C)

def show_single_color(DH,DL):
	for i in xrange(0,128):
		for j in xrange(0,128):
			write_data_8bitH_8bitL(DH,DL)

def setDotColor(x, y, color):
	drawRect(x,y, x,y, color)

# startX, startY, endX, endY:0-127
def drawRect(startX, startY, endX, endY, color_16bit):
	if (startX > 127):
		startX = 127
	if (startY > 127):
		startY = 127
	if (endX > 127):
		endX = 127
	if (endY > 127):
		endY = 127
	if (endX < startX):
		endX = startX
	if (endY < startY):
		endY = startY
	
	write_command(0x2a)
	write_data_16bitHL(startX)
	write_data_16bitHL(endX)

	write_command(0x2b)
	write_data_16bitHL(startY)
	write_data_16bitHL(endY)

	write_command(0x2c)
	for i in xrange(startX, endX+1):
		for j in xrange(startY, endY+1):
			write_data_16bitHL(color_16bit)

# 从读取到内存里的字库中取得单个汉字的点阵信息，并保存在一个字节数组里
# 某个汉字的点阵信息在字库里的开始位置(字节偏移值)可以通过以下公式计算出来，这个是固定的
# 某汉字的字节偏移值 = ((汉字的区码 - 0xa1) * 94 + 汉字的位码 - 0xa1) * 32
# 而汉字的区码和位码其实就是该汉字以GB2312码编码时的第一和二个字节
# 我们使用的字库是16x16的点阵字库，所以每一个汉字的点阵信息可以
def getHZ_32Bytes(hz):
	retBytes32 = []
	
	# 先将汉字从utf-8方式解码成unicode形式，再以gb2312方式编码，得到该汉字gb2312的编码
	gb=hz.decode('utf-8').encode('gb2312')

	print '汉字:' + hz,
	
	# 区码
	codeQu = struct.unpack('B', gb[0])[0]
	print '区码:' + str(codeQu) + ', ',

	# 位码
	codeWei = struct.unpack('B', gb[1])[0]
	print '位码:' + str(codeWei) + ', ',

	# 字节偏移值（非位偏移值）
	offset = ((codeQu - 0xa1) * 94 + codeWei - 0xa1) * 32
	print '偏移值:' + str(offset)
	
	# 从偏移值位置开始，向后连续取32个字节数据，即该汉字的点阵数据。
	# 每个汉字的点阵数据共16行，每行由两个字节的数据组成（16位）
	# 比如汉字“三”的点阵数据应该是下面这个样子的，0表示空像素，1表示有效像素
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第1行，点阵数据字节1，字节2）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第2行，点阵数据字节3，字节4）
	# 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 0 （第3行，点阵数据字节5，字节6）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第4行，点阵数据字节7，字节8）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第5行，点阵数据字节9，字节10）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第16行，点阵数据字节31，字节32）
	# 我们取到了这个点阵数据后，0的对应的像素绘制背景色，1对应的像素绘制文字色就可以了。
	for i in range(offset, offset+32):
		retBytes32.append(zk[i])
	return retBytes32

class Point:
    def __init__(self):
        self.x = -1
        self.y = -1

# 显示单个汉字函数
# 为方便调用，第一个参数是一个简单的class，包含了x和y两个信息，用于返回下一个汉字的显示位置
def drawHz16x16(pStart, byteArray32Hz, bit16Backcolor, bit16Fontcolor):
	pNext = Point()
	
	# 检查显示位置是否有效，如果超出显示范围直接退出
	if (pStart.x<0 or pStart.y<0 or pStart.x>128-16 or pStart.y>128-16):
		return pNext

	# 命令：0X2A
	# 设置绘图区域左上角的x坐标和右下角的x坐标（注意都是x坐标）
	write_command(0x2a)
	write_data_16bitHL(pStart.x)
	write_data_16bitHL(pStart.x+15)

	# 命令：0X2B
	# 设置绘图区域左上角的y坐标和右下角的y坐标（注意都是y坐标）
	write_command(0x2b)
	write_data_16bitHL(pStart.y)
	write_data_16bitHL(pStart.y+15)

	# 命令：0X2C
	# 开始在绘图区域绘图，每次绘制一个像素点的颜色，指针会自动移动到下一个像素点
	# 指针的移动顺序是，从左到右，从上到下（指针的移动顺序可以通过发送另外一个命令进行修改，请自己翻datasheet）
	# 由于之前使用命令2a和2b限制了绘图区域，所以指针到达右侧边界时会自动回到最左边并向下移动一个像素（像素换行）
	# 我们把汉字的点阵数据进行逐位判断，0的时候像素点绘制背景色，1的时候像素点绘制字体色即可。
	write_command(0x2c)
	for i in range(0, 32):
		byteHz=byteArray32Hz[i]
		for j in range(0, 8):
			if ((byteHz << j) & 0x80):
				write_data_16bitHL(bit16Fontcolor)
			else:
				write_data_16bitHL(bit16Backcolor)

	# 如果右侧已经无法显示一个完整的文字则试图换行
	if (pStart.x + 16 > 128 - 16):
		# 换行前还要检查下方有无空位显示一行
		if (pStart.y + 16 > 128 - 16):
			# 若下方已不足一行的行高则显示结束
			return pNext
		else:
			# 若下方可以继续显示新行，则换行。x坐标移到最左边0，y坐标下移一个汉字的高度
			pNext.x = 0
			pNext.y = pStart.y + 16
	# 如果右侧还有空位则继续显示
	else:
		pNext.x = pStart.x + 16
		pNext.y = pStart.y

	return pNext

try:
	### 主程序开始 ###################################################
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(cs, GPIO.OUT)
	GPIO.setup(rs, GPIO.OUT)
	GPIO.setup(sda, GPIO.OUT)
	GPIO.setup(scl, GPIO.OUT)
	GPIO.setup(reset, GPIO.OUT)

	lcd_init()
	write_command(0x2c)

	show_single_color(0x00,0x00)

	p = Point()
	p.x = 30
	p.y = 5

	# 一次性将字库全部读入内存
	zk=np.fromfile('HZK16.dat', dtype='b')
	
	text = "你好，世界"
	# 取得文本的字数
	cnt=len(text.decode('utf-8'))
	for i in range(0, cnt):
		# 逐字调用绘制单个汉字的函数
		# 第一次调用时设置一个初始位置
		# 每次绘制完一个汉字，返回值里存放的是下一个汉字的绘制开始位置
		# 如此循环往复，直到所有汉字全部显示完毕或者显示到边界无法继续显示为止
		p = drawHz16x16(p, getHZ_32Bytes(text[i*3:i*3+3]), 0x0000, 0xf800)

	p.x = 0
	p.y = 30
	text = "使用树莓派的ＧＰＩＯ来驱动一块液晶显示屏的例子。Ｂｙ：芒果爱吃胡萝卜"
	# 取得文本的字数
	cnt=len(text.decode('utf-8'))
	for i in range(0, cnt):
		# 逐字调用绘制单个汉字的函数
		# 第一次调用时设置一个初始位置
		# 每次绘制完一个汉字，返回值里存放的是下一个汉字的绘制开始位置
		# 如此循环往复，直到所有汉字全部显示完毕或者显示到边界无法继续显示为止
		p = drawHz16x16(p, getHZ_32Bytes(text[i*3:i*3+3]), 0x0000, 0xff80)

except KeyboardInterrupt:
	pass

# 清理GPIO口
#GPIO.cleanup()

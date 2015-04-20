title: SSH暴力扫描的防范手段
date: 2015-03-27 19:47:37
categories:
- 技术
tags:
- SSH
- LINUX
- 树莓派
---
之前买了块树莓派在家里搭了一台服务器玩，为了在外面方便访问，在路由器给小pi设置成了DMZ主机，并开启了SSH服务。一直用的很开心。
前几天偶然打开系统日志发现每天都有大量的SSH登录失败的log。
<!-- more -->
#背景
之前买了一块树莓派在家里搭了一台服务器玩，为了在外面方便访问，在路由器给小pi设置成了DMZ主机，并开启了SSH服务。一直用的很开心。
前几天偶然打开系统日志发现每天都有大量的SSH登录失败的log。基本上长成下面这个样子：
```
Mar 26 09:30:39 raspberrypi sshd[1088]: Failed password for root from 115.230.126.148 port 34063 ssh2
Mar 26 09:30:42 raspberrypi sshd[1088]: Failed password for root from 115.230.126.148 port 34063 ssh2
Mar 26 09:30:57 raspberrypi sshd[1251]: Failed password for root from 115.230.126.148 port 40513 ssh2
Mar 26 09:30:58 raspberrypi sshd[1255]: Failed password for invalid user user from 111.73.46.22 port 4918 ssh2
Mar 26 09:30:59 raspberrypi sshd[1251]: Failed password for root from 115.230.126.148 port 40513 ssh2
Mar 26 09:31:01 raspberrypi sshd[1251]: Failed password for root from 115.230.126.148 port 40513 ssh2
Mar 26 09:31:10 raspberrypi sshd[1370]: Failed password for invalid user ubnt from 111.73.46.22 port 4432 ssh2
Mar 26 09:31:14 raspberrypi sshd[1370]: Failed password for invalid user ubnt from 111.73.46.22 port 4432 ssh2
Mar 26 09:31:19 raspberrypi sshd[1370]: Failed password for invalid user ubnt from 111.73.46.22 port 4432 ssh2
```
虽然对自己设置的密码强度有信心，但自己家里被人偷窥的感觉总是不爽。
解决方案有很多：
- 被动方式。监视系统日志，发现有连续登录失败的尝试就屏蔽来源ip的请求，也就是封IP。
- 弱主动方式。修改SSH端口，SSH默认端口是22，改个端口可以档掉一部分扫描，但挡不住连端口也一起扫描的家伙。
- 强主动方式。关掉SSH的密码登录验证，只允许使用公密钥方式登录。这种方式最安全，缺点是初始设置稍微麻烦点，且用一个新的客户端总要进行初始设置。

下面一个一个试着做。
#扫描系统日志，封IP
系统日志的位置：
/var/log/auth.log

这个日志文件专门记录登入登出以及调用sudo等敏感操作。我们需要的尝试登录失败的记录就在里面。
我写了一个简单的shell程序。每一步都做了注释，应该很好懂。

{% codeblock lang:bash %}
#!/bin/bash

# 日志文件
LOG_FILE="/var/log/auth.log"

# 上一次login失败的ip
last_ip=""

# 上一次列入黑名单的ip
last_blocked_ip=""

# 当前处理行数
lines=0

# 每次运行时都删掉之前生成的ip列表文件
rm -rf block_ip.log

# 获取错误日志总行数，以便输出处理进度
total="$(grep "Failed" ${LOG_FILE} | wc -l)"

# 检索错误日志，并逐行取得试图登录系统的ip
grep "Failed" $LOG_FILE | while read LINE; do
{
  # 从当前行取得ip
  # awk NF-3 的意思是以空格或tab为分隔符，从后往前数第3个项目
  ip="$(echo ${LINE} | awk '{print $(NF-3)}')"
  lines=$(($lines + 1))
  
  # 下面这条语句实现了显示进度的功能，注意最后是以\r结尾的，作用是不换行，把光标移动到行首
  printf "Progress Line: $lines"/"$total\r"
  #echo $lines"/"$total

  # 同一个IP连续两次登录错误的话就认为是恶意登录，将该ip记录到ip列表文件中
  if [ "$last_ip" == "$ip" ] && [ "$ip" != "$last_blocked_ip"   ]; then
    echo "$ip" >> block_ip.log
    last_blocked_ip=$ip
  fi
  last_ip=$ip
}
done

# 至此，所有日志里试图连续尝试登录失败的ip全部被记录在*block_ip.log*这个文件中了。
# 接着我们把这个列表里重复的ip删掉
sort block_ip.log | uniq > sorted_ip.log

# 这样我们就得到了一个不重复的，试图暴力破解我们密码的坏人的ip列表
# 屏蔽他们！
cat sorted_ip.log | while read LINE; do
{
  ip=${LINE}
  # 将ip加入黑名单
  iptables -A INPUT -s "$ip" -j DROP
}
done
{% endcodeblock %}

这样，封ip就成功了。
这个程序还可以改成使用 tail -f 不停监视最新的日志，随时封新发现的ip的模式。有兴趣的可以自己动手改一下。

#修改SSH端口
todo

#关掉SSH的密码登录验证
todo

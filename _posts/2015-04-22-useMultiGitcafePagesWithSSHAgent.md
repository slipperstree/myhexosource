title: "从同一台终端分别向Gitcafe不同帐号Push的方法"
date: 2015-04-22 04:21:55
categories: 技术
tags:
- hexo
- git
- ssh
---
#需求
拥有多个不同内容的个人静态站点（均使用Hexo），各自拥有独立域名，希望托管在gitcafe上操作：gitcafe的每一个帐号可以开设一个静态页面的站点（gitcafe pages服务）

#操作
申请了多个gitcafe的id，且每一个id都开设了gitcafe pages进行deploy的时候希望通过ssh密钥验证的方式，所以在每个id的gitcafe的设置里都需要设定ssh公钥。可能是出于安全的考虑，在gitcafe里即使是不同的id也不允许使用相同的公钥所以我为每一个id都生成了一对专用的公钥和私钥（文件名不同，均放置在~/.ssh/下面）

#问题
当我利用hexo进行deploy的时候，只有其中一个站点能成功deploy，其他几个均报错提示用户AAA没有push到BBB账户的权限！
> Error: PERMISSION DENIED: User AAA can't write to BBB/BBB.

#分析
虽然为每个账户都生成了独立的私钥密钥，但是ssh连接的时候，ssh客户端并不知道针对不同用户id应该使用哪个私钥。那么就需要在每一次deploy之前明确告诉接下来的ssh连接要使用的私钥。

#解决
ssh-agent可以在其生命周期内使用指定的密钥文件。在hexo deploy之前指定，deploy结束后退出ssh-agent即可。（退出以后再进入需要重新指定）
新建一个sh文件，代码如下。

``` bash
#! /bin/bash

# 启动ssh-agent
eval `ssh-agent`

# 指定接下来要使用的私钥
ssh-add ~/.ssh/id_rsa_for_BBB

# 做你想做的工作，我这里是使用hexo向gitcafe部署博客文件。（hexo的ssh连接信息已经实现配置好了，这部分不是本文重点，省略）
hexo d

# 做完你要做的工作以后记得退出ssh-agent
eval `ssh-agent -k`
```

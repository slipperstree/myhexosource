title: 利用webpy搭建一个简单的网页版hexo编辑器
date: 2014-08-20 18:52:35
categories: 技术
tags:
- webpy
- python
discription: 利用强大方便的webpy来搭建一个简单但完备的在线版hexo编辑器...
---
相信看到本文的读者都已经搭建了自己的hexo站点。hexo（或者任何其他静态html框架）有一个非常不方便的地方就是每次写博客，你都必须ssh到你的服务器上执行以下命令来创建一篇新文章：
```
hexo n 文章标题
```
<!-- more -->
然后再用nano或者是vim等文字编辑器来更新这个md文件。编辑完以后再执行下面两条命令生成文章并发布。
```
hexo g
hexo d 
```
这个过程很geek，可能也是最先吸引程序猿们使用这套东西的原因。但最终你会觉得厌烦，为什么我把精力集中在写文章上呢？
本文的目的就是利用强大方便的webpy来搭建一个简单但完备的在线版hexo编辑器，这个编辑器应该具有：
- 发布新文章
- 修改旧文章
- 删除旧文章
- 通过web页面指示后台执行hexo命令生成html并发布

我们开始吧

#安装

##安装hexo

##安装webpy

#验证

##验证hexo

##验证webpy

#造轮子

##设计

###首页
首页分成有两个部分。
1. 顶部的命令按钮区。
目前只有一个最基本的功能按钮，写新文章。
2. 文章列表区。
初期显示时取得hexo的_post目录下所有文件(文章)的列表显示。每一个文件都有一组对应的操作按钮。(目前只有最基本的修改和删除按钮)为了页面整洁，这些操作按钮默认不显示，当点到某文章时才动态显示出来。

###创建新文章页
这个页面接收一个新标题(其实是文件名)作为参数并显示在页面顶部。不可修改。主体只需要一个文本框和一个提交按钮。文本框用来编辑md源文件。点击提交按钮则将文章写入文件然后调用hexo命令生成html并发布。

###修改旧文章页
布局基本和创建新文章一样。一个编辑文本框，一个提交按钮。

###其他

####回收站功能

####登录功能

##关键代码

- 为了避免中文乱码，统一设置字符集为UTF-8
```
import sys
reload(sys)
sys.setdefaultencoding('utf8')
```

- 取得文章列表函数
```
# 这里替换成你自己的hexo根目录
hexoRoot = '/home/pi/hexo_root'
postDir = hexoRoot + '/source/_posts/'
def getWzList():
    # Make list for show
    wzList = []
    idx = 0;
    for lists in os.listdir(postDir): 
        path = os.path.join(postDir, lists) 
        if os.path.isfile(path):
            wzList.append([os.path.basename(path), 'wz_'+str(idx)])
            idx = idx + 1
    wzList.sort(reverse=True)
    return wzList
```

- 首页基本上什么都不做直接返回文章列表给模板
```
class index:
    def GET(self):
        return render.index(getWzList())
```

- 创建新文章时调用hexo命令
为了执行hexo命令需要更改工作目录到你的hexo根目录下。
记得要先备份一下当前工作目录，执行完hexo命令以后需要恢复原来的工作目录，否则读取模板文件时会出错。
```
        # 更改工作目录
        sWebpyDir = os.getcwd()
        os.chdir(hexoRoot)
        
        # 执行 Hexo n ... 这里的sNewTitle是从index页面传过来的参数
        os.system('hexo n ' + sNewTitle)
        
        # 恢复原来的webpy的工作目录
        os.chdir(sWebpyDir)
```

- 读取md文件
```
        now = datetime.datetime.now()
        filename = now.strftime('%Y-%m-%d-') + sNewTitle + '.md'
        fileHandle = open ( postDir + filename )
        fileContent = fileHandle.read()
        fileHandle.close()
```
##运行效果




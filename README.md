# TexasHoldem-0002
这是我的

本来是主要分为三个模块
 - 通信
 - 数据解析
 - 算法
 
后来改了点东西，还利用了一个开源的项目，用于计算牌型的排名等等
其实 Python 真的很好用啊

自认为处理半包和多包的问题我用的代码算是极少的：

```python
patt = r'((?P<TypeTag>[^/]+)/[\s\S]+?/(?P=TypeTag)|game-over)'
```

```python
                data = self.sock.recv(1024)
                if data:
                    reply = pm.msgHandler(tempData + data)
                    if reply == 'game-over':
                        self.sock.shutdown(socket.SHUT_RDWR)
                        self.sock.close()
                        break
                    elif reply == 'waiting':
                        tempData += data

```

还有一些，有空写吧~

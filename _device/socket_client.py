from _device import wlan_wait_connected
import socket
import time
class AbstractClient:
    '''客户端的基类，支持将给定句柄发送到指定端口，infos是一个元组列表
    发送数据的形式为元组列表的元组的关键字形式
    example:
    
    infos = [
    (name,handle),(name,handle)
    ]

    obj_addr = AbstractClient.getaddrInfo(addr)

    client = AbstractClient(ojb_address)#初始化

    client.setInfo(infos)#设置信息挂钩

    client.begin_sever()#如果更改要对默认地址之外的发送服务,可以传入地址

    client.close()#释放socket对象

    the other example:

    infos = [
    (name,handle),(name,handle)
    ]

    obj_addr = AbstractClient.getaddrInfo(addr)

    with AbstractClient(ojb_address) as client:
    
        client.setInfo(infos)

        client.begin_sever()

    '''
    SEND = 1
    RECV = 2
    SEND_RECV = 3
    def __init__(self,obj_address,address = None,send_code = 'utf-8',recv_code = 'utf-8') -> None:
        self.obj_address = obj_address
        self.address = address if address else None
        self.send_code = 'utf-8'
        self.recv_code = 'utf-8'

    def __enter__(self):
        return self
    
    def __exit__(self,exc_type,exc_val,_exc_tb):
        self.close()
    
    def setAddress(self,obj_addr,addr = None):
        '''在micropython中为socket.getaddrinfo('www.micropython.org', 80)[0][-1]，
        所以在此可以为具体类的getaddrinfo'''
        self.address = addr
        self.obj_address = obj_addr
    
    def setInfos(self,infos):
        '''infos是一个元组列表,[(name,handle),...]'''
        self.infos = infos
    

   
    def close(self):
        '''用于进行关闭的必要操作'''
        pass

  
    def getClient(self):
        '''获取socket对象'''
        pass

    def begin_sever(self,client_type = SEND,time_sleep = 1,times = None):
        '''开始收发数据的服务'''
        pass
    def sends(self,time_sleep = 1,times = None):
        pass

    @classmethod
    def getaddrinfo(host,port,family= 0,type =0,proto =0,flags =0):
        '''返回[(addr,other*4),...]'''
        return socket.getaddrinfo(host,port,family,type,proto,flags)
    

class UDPClient(AbstractClient):
    '''服务基类用于将获取的信息发送到指定端口
    example:
    #1初始化

    obj_addr = ('10.195.86.44',46545)

    udp_client = UDPClient(obj_addr)

    #2infos配置

    infos = [('I',handle1),('me',handle2)]

    udp_client.setInfos(infos)

    #3发送

    udp_client.sends(times=50)
    '''
    def __init__(self,ojb_address,address = None,send_code = 'utf-8',recv_code = 'utf-8'):
        super().__init__(ojb_address,address,send_code,recv_code)
        self.client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    
    def close(self):
        return self.client.close()
    
    def getClient(self):
        '''获取socket对象'''
        return self.client

    def begin_sever(self,sever_type,time_sleep = 1,times = None):
        '''双线程开始收发数据的服务,sever_type = SEND or RECV or SEND_RECV,当times 为 None或0时，一直服务 '''
        #发送部分
        pass

    def recvfrom(self,maxsize = 1024):
        pass

    def recvs(self,time_sleep = 1,times = None):
        pass

    def sends(self,time_sleep = 1,times = None):
        print('sends begin:',end='')
        #发送服务
        if not times:
            while True:
                self.sendto(self.obj_address)
                time.sleep(time_sleep)
        else:
            for i in range(times):
                self.sendto(self.obj_address)
                time.sleep(time_sleep)
    
    def sendto(self,obj_address):
        print('.',end='')
        data = ''
        for info in self.infos:
            data_item = info[0] + ':' + str(info[1](*info[2])) + '\n'
            data_item = data_item.encode(self.send_code)
            data = data + data_item
        self.client.sendto(data,obj_address)
    
class TCPClient(AbstractClient):
    '''服务基类用于将获取的信息发送到指定端口
    example:
    #1初始化

    obj_addr = ('10.195.86.44',46545)

    tcp_client = TCPClient(obj_addr)

    #2infos配置

    infos = [('I',handle1),('me',handle2)]

    tcp_client.setInfos(infos)

    #3发送
    tcp_client.connect()

    udp_client.sends(times=50)
    '''
    def __init__(self,ojb_address,address = None,send_code = 'utf-8',recv_code = 'utf-8'):
        super().__init__(ojb_address,address,send_code,recv_code)
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    def close(self):
        return self.client.close()
    
    def getClient(self):
        '''获取socket对象'''
        return self.client

    def begin_sever(self,sever_type,time_sleep = 1,times = None):
        '''双线程开始收发数据的服务,sever_type = SEND or RECV or SEND_RECV,当times 为 None或0时，一直服务 '''
        #发送部分
        pass

    def recvfrom(self,maxsize = 1024):
        pass

    def recvs(self,time_sleep = 1,times = None):
        pass

    def sends(self,time_sleep = 1,times = None):
        print('sends begin:',end='')
        #发送服务
        if not times:
            while True:
                self.send()
                time.sleep(time_sleep)
        else:
            for i in range(times):
                self.send()
                time.sleep(time_sleep)
    
    def send(self):
        print('.',end='')
        data = b''
        for info in self.infos:
            data_item = info[0] + ':' + str(info[1](*info[2])) + '\n'
            data_item = data_item.encode(self.send_code)
            data = data+data_item
        self.client.send(data)

    def connect(self,obj_address = None):
        obj_addr = obj_address if obj_address else self.obj_address
        print("TCP connecting...")
        return self.client.connect(obj_addr)


    def bind(self,address):
        self.address = address
        self.client.bind(address)




if __name__ == '__main__':
    #网络连接
    ssid='wawu'
    password='long13044'
    wlan_wait_connected(ssid,password)
    #发送服务配置
    #1初始化
    obj_addr = ('10.199.157.43',46545)
    tcp_client = TCPClient(obj_addr)
    #2infos配置
    def handle1():
        return 1
    def handle2():
        return 2
    infos = [('I',handle1),('me',handle2)]
    tcp_client.setInfos(infos)
    #3发送
    tcp_client.connect()
    tcp_client.sends(times=50)





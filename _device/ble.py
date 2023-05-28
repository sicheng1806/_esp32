'''此模块实现了蓝牙的基础配置，包含了一些常量IRQ，特性值FLAG和一个BLESever类用于配置控制传感器的类'''
import bluetooth
from machine import Pin,Timer


class IRQ:
    IRQ_CENTRAL_CONNECT = 1
    IRQ_CENTRAL_DISCONNECT = 2
    IRQ_GATTS_WRITE = 3
    IRQ_GATTS_READ_REQUEST = 4
    IRQ_SCAN_RESULT = 5
    IRQ_SCAN_DONE = 6
    IRQ_PERIPHERAL_CONNECT = 7
    IRQ_PERIPHERAL_DISCONNECT = 8
    IRQ_GATTC_SERVICE_RESULT = 9
    IRQ_GATTC_SERVICE_DONE = 10
    IRQ_GATTC_CHARACTERISTIC_RESULT = 11
    IRQ_GATTC_CHARACTERISTIC_DONE = 12
    IRQ_GATTC_DESCRIPTOR_RESULT = 13
    IRQ_GATTC_DESCRIPTOR_DONE = 14
    IRQ_GATTC_READ_RESULT = 15
    IRQ_GATTC_READ_DONE = 16
    IRQ_GATTC_WRITE_DONE = 17
    IRQ_GATTC_NOTIFY = 18
    IRQ_GATTC_INDICATE = 19
    IRQ_GATTS_INDICATE_DONE = 20
    IRQ_MTU_EXCHANGED = 21
    IRQ_L2CAP_ACCEPT = 22
    IRQ_L2CAP_CONNECT = 23
    IRQ_L2CAP_DISCONNECT = 24
    IRQ_L2CAP_RECV = 25
    IRQ_L2CAP_SEND_READY = 26
    IRQ_CONNECTION_UPDATE = 27
    IRQ_ENCRYPTION_UPDATE = 28
    IRQ_GET_SECRET = 29
    IRQ_SET_SECRET = 30
    
    
class FLAG:
    FLAG_BROADCAST = 0x000
    FLAG_READ = 0x0002
    FLAG_WRITE_NO_RESPONSE = 0x0004
    FLAG_WRITE = 0x0008
    FLAG_NOTIFY = 0x0010
    FLAG_INDICATE = 0x0020
    FLAG_AUTHENTICATED_SIGNED_WRITE = 0x0040
    FLAG_AUX_WRITE = 0x0100
    FLAG_READ_ENCRYPTED = 0x0200
    FLAG_READ_AUTHENTICATED = 0x0400
    FLAG_READ_AUTHORIZED = 0x0800
    FLAG_WRITE_ENCRYPTED = 0x1000
    FLAG_WRITE_AUTHENTICATED = 0x2000
    FLAG_WRITE_AUTHORIZED = 0x4000

class BaseBLESever:
    '''BleSever的基类,BaseBleSever(name,servicer,ble_irq)
    '''

    def __init__(self,name,servicer = None,ble_irq = None,led_pin = 2):
        self.name = bytes(name,'utf-8')
        self.servicer = servicer
        #
        self.ble = bluetooth.BLE()
        self.timer = Timer(0)
        self.led = Pin(led_pin,Pin.OUT)
        #
        self.ble.active(True)
        self.ble.config(gap_name = name)
        self.register(self.servicer)
        #
        self.irq = ble_irq
        self.ble.irq(self.irq)#蓝牙中断函数挂载
           
        self.advertise()# 开始广播
        

    def advertise(self,interval_us=100,resp_data=None):
        '''转换状态为广播员，开始广播，注意不连接就是广播态，通过led和print显示状态'''
        adv_data = bytearray(b'\x02\x01\x06')+bytearray([len(self.name)+1,0x09])+self.name
        self.ble.gap_advertise(interval_us = interval_us,adv_data = adv_data,resp_data = resp_data)
        self.disconnected()#状态显示

    def disconnected(self):
        '''未连接态状态显示'''
        self.timer.init(mode = Timer.PERIODIC,period=100,callback= lambda blink:self.led.value(not self.led.value()))
        print("ble disconnected...")
    
    def connected(self):
        '''连接态状态显示'''
        self.led.on()
        self.timer.deinit()
        print("ble connected...")
    
    def register(self,servicer):
        '''充当gatts注册服务'''
        self.handles = self.ble.gatts_register_services(servicer)
        
    @property
    def servicer_shap(self):
        servicer_generator = (len(i) for i in self.servicer)
        return [i for i in servicer_generator]

    
class BLESever(BaseBLESever):
    '''一个蓝牙代理设备BLESever(name,getBuffer,servicer = None)，默认的servicer针对于XGZP类,
    其中通过getBuffers = List<func> 的挂载，实现了设备向蓝牙设备提供数据接口的挂载

    example:

    from xgzp import XGZP

    from machine import SoftI2C,Pin

    #配置一下XZGP传感器设备

    i2c = SoftI2C(scl = Pin(18),sda = Pin(19),freq = 400000)

    xgzp = XGZP(i2c)

    xgzp.setMode(XGZP.CMD_DORMANT_MOD[2])

    #配置一下蓝牙设备

    servicer = None #默认的servicer

    getBuffers = [
                    [getPress,getTemp,],
                    ]

    ble = BLESever('XGZP',getBuffers=getBuffers,servicers=servicer)#集中配置
    '''
    #默认服务配置
    dft_character_pres = (bluetooth.UUID(0x2A6D),bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)#读通知
    dft_character_temp = (bluetooth.UUID(0x2A6E),bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)#读通知
    dft_servicer = (
            (bluetooth.UUID(0x181A),(dft_character_pres,dft_character_temp)),
        )
    
    def __init__(self,name,getBuffers,servicer = None,led_pin = 2):
        self.ble = bluetooth.BLE()
        self.timer = Timer(0)
        self.led = Pin(led_pin,Pin.OUT)

        self.name = bytes(name,'utf-8')
        self.ble.config(gap_name=name)
        self.getBuffers = getBuffers
        self.servicer = servicer if servicer else BLESever.dft_servicer
        #
        self.ble.active(True)
        self.register(self.servicer)#蓝牙注册
        #
        self.ble.irq(self._dft_iqr)#蓝牙中断函数挂载
           
        self.advertise()# 开始广播

    def _dft_iqr(self,event,data):
        if event == IRQ.IRQ_CENTRAL_CONNECT:
            self.connected()
        elif event == IRQ.IRQ_CENTRAL_DISCONNECT:
            self.advertise()
        elif event == IRQ.IRQ_GATTS_READ_REQUEST:
            for i in range(len(self.handles)):
                for j in range(len(self.handles[i])):
                    if data[1] == self.handles[i][j]:
                        buf = getBuffers[i][j]()
                        buf = bytes(str(round(buf,3)),'uft-8')
                        print(f'buf is {buf},handle is handles[{i}][{j}]')
                        self.ble.gatts_write(self.handles[i][j],buf)
                        
    
if __name__ == '__main__':
    from _device import XGZP
    from machine import SoftI2C,Pin
    #配置一下XZGP传感器设备
    i2c = SoftI2C(scl = Pin(18),sda = Pin(19),freq = 400000)
    xgzp = XGZP(i2c)
    xgzp.setMode(XGZP.CMD_DORMANT_MOD[2])
    #配置一下蓝牙设备
    servicer = None #默认的servicer
    getBuffers = [
                    [xgzp.getPress,xgzp.getTemp,],
                    ]
    ble = BLESever('XGZP',getBuffers=getBuffers,servicer=servicer)#集中配置
    



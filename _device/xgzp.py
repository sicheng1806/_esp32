from machine import SoftI2C,Pin
import time

class XGZP:
    '''集成了xgzp的模式设置，数据读取功能
    
    example:

    import time

    from machine import Pin,SoftI2C

    from _device import XGZP
            
    if __name__ == '__main__':
    
        #step1:初始化i2c

        i2c = SoftI2C(scl = Pin(18),sda = Pin(19),freq=400000)

        xgzp = XGZP(i2c)

        #step2:设置工作模式_休眠模式

        xgzp.setMode(xgzp.cmd_dormant_model[2])

        #不断返回数据

        while True:
        
            xgzp.getData()

            time.sleep(1)

            print('-------------\n')
    修改日志:
    1.发现getTemp,getData,getPress方法会出现偶尔不成功的情况，由于一次采集失败无很大影响，
    而且猜测应该是SoftI2C的读取数据的问题,采用try.
    2.经过大量测试去掉前面的修改，类运转很正常，问题可以由其他方面引起
    3.发现问题是由于i2c通信时设备不存在所导致，由于这种错误无法避免因而需要加以处理，采用错误丢弃的方法，如果一直错误，则堵塞
    '''
    #指令集
    ADDR = 0x6D
    ADDR_P = 0x06,0x07,0x08
    ADDR_T = 0x09,0x0A
    ADDR_PT = 0x06,0x07,0x08,0x09,0x0A
    ADDR_CMD = 0x30
    ADDR_SYS_CONF = 0xA5
    ADDR_P_CONF = 0xA6
    CMD_COMBINE_MOD = 0x0A
    CMD_SINGLE_T_MOD = 0x08
    CMD_SINGLE_P_MOD = 0x09
    CMD_DORMANT_MOD = (0x1B,0x2B,0xFB)#对应 63.5ms, 125ms, 1s
    K = [4096, 256]

    def __init__(self,i2c):
        self.i2c = i2c

    def __get_pressure(self,buf,_round):
        p_ADC = 0
        for i in range(3):
            p_ADC = p_ADC << 4
            p_ADC += buf[i]
        #print(p_ADC,buf[0])
        pressure = p_ADC/XGZP.K[0] if not buf[0]>>7 else (p_ADC-2^24)/XGZP.K[0]
        if _round is not None:
            pressure = round(pressure,_round)
        print(f"Data: pressure is {pressure}")
        return pressure
    
    def __get_temperature(self,buf,_round = None):
        N = buf[0]*256+buf[1]
        temperature = N /XGZP.K[1] if N<2^15 else (N-2^16)/XGZP.K[1]
        if _round is not None:
            temperature = round(temperature,_round)
        print(f"Data: temperature is {temperature}")
        return temperature
    
    def setI2c(self,i2c):
        self.i2c = i2c

    def setMode(self,cmd_mode):
        '''设置采集模式:
        
        i2c为machine.SoftI2c实例
        mode = 命令的参数如self.cmd_combine_model
        '''
        buf = bytearray([cmd_mode])
        try:
            self.i2c.writeto_mem(XGZP.ADDR,XGZP.ADDR_CMD,buf)
            print(f"cmd_mode: success to set {cmd_mode}")
        except:
            print(f"cmd_mode: fail to set {cmd_mode}")
            raise
    
    def getData(self,_round = None):
        buf = bytearray(5)
        for i in range(5):
            Flag = True
            while Flag:
                try:
                    buf[i] = ord(self.i2c.readfrom_mem(XGZP.ADDR,XGZP.ADDR_PT[i],1))#此处可能会os错误，可能是设备断触导致的
                    Flag = False
                except:
                    Flag = True
            #print(f"Collection: XGZP.ADDR_PT[{i}] collection success!:{buf[i]}")
        pressure = self.__get_pressure(buf[0:3],_round)
        temperature = self.__get_temperature(buf[3:5],_round)
        return pressure,temperature

    def getPress(self,_round = None):
        buf = bytearray(3)
        for i in range(3):
            Flag = True
            while Flag:
                try:
                    buf[i] = ord(self.i2c.readfrom_mem(XGZP.ADDR,XGZP.ADDR_P[i],1))
                    Flag = False
                except:
                    Flag = True
            #print(f"Collection: XGZP.ADDR_P[{i}] collection success!:{buf[i]}")
        pressure = self.__get_pressure(buf,_round)
        return pressure

    def getTemp(self,_round = None):
        buf = bytearray(2)
        for i in range(2):
            Flag = True
            while Flag:
                try:
                    buf[i] = ord(self.i2c.readfrom_mem(XGZP.ADDR,XGZP.ADDR_T[i],1))
                    Flag = False
                except:
                    Flag = True
                #print(f"{XGZP.ADDR_T[i]} collection success!:{buf[i]}")
        temperature = self.__get_temperature(buf,_round)
        return temperature
    


if __name__ == '__main__':
    i2c = SoftI2C(scl = Pin(18),sda = Pin(19),freq = 400000)
    xgzp = XGZP(i2c)
    xgzp.setMode(XGZP.CMD_DORMANT_MOD[2])
    #i2c.readfrom_mem(0x01,XGZP.ADDR_T[0],1) #由于0x01地址对应的设备不存在所以会引发错误
    #i2c.readfrom_mem(XGZP.ADDR,0xBB,1)#不会引发错误，但是会不可控
    for i in range(100):
        xgzp.getData()
        time.sleep(0.1)


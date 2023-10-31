from machine import SoftI2C,Pin
import time

class VEML7700:
    '''集成了AEML7700的模式设置，数据读取功能
    
    example:

    >>> import time
    >>> from machine import Pin,SoftI2C
    >>> from _device import VEML7700
    >>> #创建i2c连接
    >>> i2c = SoftI2C(scl = Pin(18),sda = Pin(19),freq=400000)
    >>> als = VEML7700(i2c)#als = VEML7700(i2c,config = {},wh = {},wl = {},psm = {})
    >>> # 设置参数
    >>> als.set_

    1.参数设置，所有可以设置的参数共有11个,包括config寄存器的设置,psm寄存器的设置,wh和wl寄存器的设置。参数可以在创建对象时,设置寄存器时,或者之后独立设置。未设置参数保持默认。
    '''
    # 设备地址和读写模式设置命令
    Device_ADDR = 0x10
    # 设置用寄存器地址
    ALS_CONFIG_0 = 0x00
    ALS_WH = 0x01
    ALS_WL = 0x02
    ALS_PSM = 0x03 #省电模式
    # 读取用寄存器地址
    ALS = 0x04
    WHITE = 0x05
    ALS_INT = 0x06
    # config参数
    config_ALS_GAIN = {'1x':0b00,'2x':0b01,'1/8x':0b10,'1/4x':0b11}
    config_ALS_IT = {'25ms':0b1100,'50ms':0b1000,'100ms':0b0000,'200ms':0b0001,'400ms':0b0010,'800ms':0b11}
    config_ALS_PERS = {'protect_1':0b00,'protect_2':0b01,'protect_4':0b10,'protect_8':0b11}
    config_ALS_INT_EN = {'int_enable':1,'int_disable':0}
    config_ALS_SD = {"als_on":0,'als_down':1}
    CONF_ARGS = config_ALS_GAIN|config_ALS_IT|config_ALS_INT_EN|config_ALS_SD|config_ALS_PERS
    # psm 参数
    psm_PSM_EN = {'psm_enable':1,'psm_disable':0}
    psm_PSM = {'psm_1':0b00,'psm_2':0b01,'psm_3':0b10,'psm_4':0b11}
    PSM_ARGS = psm_PSM|psm_PSM_EN

    ARGS = CONF_ARGS|PSM_ARGS
    # psm_PSM和config_ALS_IT 共同决定了 设备的刷新时间、工作电流和分辨率，因而支持通过刷新时间，分辨率来控制设备的省电模式，前提是psm_PSM_EN打开。
    # config_ALS_IT与分辨率对应，刷新时间受两者调控
    config_resolution = {"0.0288lx":0b0000,"0.0144lx":0b0001,"0.0072lx":0b0010,"0.0036lx":0b0011}
    psm_refresh_time = {"600ms":6,"1100ms":11,"2100ms":21,"4100ms":41,"700ms":7,"1200ms":12,
                        "2200ms":22,"4200ms":42,'900ms': 9, '1400ms': 14, '2400ms': 24,
                          '4400ms': 44, '1300ms': 13, '1800ms': 18, '2800ms': 28, 
                          '4800ms': 48}


    def __init__(self,i2c):
        self.i2c = i2c
    def communicate_with_register(self,register_addr,*args):
        args = list(args)
        if register_addr == 0x00: # 配置寄存器
            
            '''bit对应12:11,9:6,5:4,1,0'''
            for i,f in zip(range(0,len(args)),[2,4,2,1,0]):
                if isinstance(args[i],str):
                    pass
                if isinstance(args[i],int):
                    args[i] = f"{args[i]:b}"[-f:]
            ALS_GAIN,ALS_IT,ALS_PERS,ALS_INT_EN,ALS_SD = args
            bytenumber = '000'+ALS_GAIN+'0'+ALS_IT+ALS_PERS+'00'+ALS_INT_EN+ALS_SD
            buf = bytearray([int(bytenumber,2)])
            return self.i2c.writeto_mem(VEML7700.Device_ADDR,register_addr,buf)
        elif register_addr == 0x01:#15:8 MSB高阈值窗口设置 7:0 LSB高阈值窗口设置
            for i,f in zip(range(0,len(args)),[8,8]):
                if isinstance(args[i],str):
                    pass
                elif isinstance(args[i],int):
                    args[i] = f"{args[i]:b}"[-f:]
                else:
                    raise TypeError("not implement")
            MSB_HIGH_WINDOW,LSB_HIGH_WINDOW = args
            bytenumber = MSB_HIGH_WINDOW+LSB_HIGH_WINDOW
            buf = bytearray([int(bytenumber,2)])
            return self.i2c.writeto_mem(VEML7700.Device_ADDR,register_addr,buf)
        elif register_addr == 0x02:
            for i,f in zip(range(0,len(args)),[8,8]):
                if isinstance(args[i],str):
                    pass
                elif isinstance(args[i],int):
                    args[i] = f"{args[i]:b}"[-f:]
                else:
                    raise TypeError("not implement")
            MSB_LOW_WINDOW,LSB_LOW_WINDOW = args
            bytenumber = MSB_LOW_WINDOW+LSB_LOW_WINDOW
            buf = bytearray([int(bytenumber,2)])
            return self.i2c.writeto_mem(VEML7700.Device_ADDR,register_addr,buf)
        elif register_addr == 0x03:#15:3 保留 2:1 模式设置 0 开启或关闭
            for i,f in zip(range(0,len(args)),[2,1]):
                if isinstance(args[i],str):
                    pass
                elif isinstance(args[i],int):
                    args[i] = f"{args[i]:b}"[-f:]
                else:
                    raise TypeError("not implement")
            PSM,PSM_EN = args
            bytenumber = '0'*13+PSM+PSM_EN
            buf = bytearray([int(bytenumber,2)])
            return self.i2c.writeto_mem(VEML7700.Device_ADDR,register_addr,buf)
        #读数据
        elif register_addr == 0x04:
            buf = self.i2c.readfrom_mem(VEML7700.Device_ADDR,register_addr,2).hex()
            ALS_OUT_MSB,ALS_OUT_LSB = int(buf[0:2],16),int(buf[-2:],16)
            return ALS_OUT_MSB,ALS_OUT_LSB
        elif register_addr == 0x05:
            buf = self.i2c.readfrom_mem(VEML7700.Device_ADDR,register_addr,2).hex()
            WHITE_OUT_MSB,WHITE_OUT_LSB = int(buf[0:2],16),int(buf[-2:],16)
            return WHITE_OUT_MSB,WHITE_OUT_LSB
        elif register_addr == 0x06:# 15 低阈值溢出，14高阈值溢出，13:0 保留
            buf = f'{int(self.i2c.readfrom_mem(VEML7700.Device_ADDR,register_addr,2).hex(),16):b}'[:2]
            int_th_low ,int_th_high = int(buf[0],2),int(buf[1],2)
            return int_th_low,int_th_high
        else:
            raise Exception(f"no register address is {register_addr}")

    def set_config(self,ALS_GAIN=None,ALS_IT=None,ALS_PERS=None,ALS_INT_EN=None,ALS_SD=None):
        return self.communicate_with_register(VEML7700.ALS_CONFIG_0,ALS_GAIN,ALS_IT,ALS_PERS,ALS_INT_EN,ALS_SD)
    def set_wh(self,msb_wh,lsb_wh):
        return self.communicate_with_register(VEML7700.ALS_WH,msb_wh,lsb_wh)
    def set_wl(self,msb_wl,lsb_wl):
        return self.communicate_with_register(VEML7700.ALS_WH,msb_wl,lsb_wl)
    def set_psm(self,psm,psm_en):
        return self.communicate_with_register(VEML7700.ALS_PSM,psm,psm_en)
    def read_als_out(self):
        return self.communicate_with_register(register_addr=VEML7700.ALS)
    def read_white_out(self):
        return self.communicate_with_register(register_addr=VEML7700.WHITE)
    def read_ALS_INT(self):
        return self.communicate_with_register(register_addr=VEML7700.ALS_INT)
    '''def setArgs(self,**kwargs):
        config_flag,wh_flag,wl_flag,psm_flag = False,False,False,False
        for key in kwargs.keys():
            if key in self.config.keys():
                self.config[key] = kwargs.keys[key]
                config_flag = True
            elif key in self.wh.keys():
                self.wh[key] = kwargs.keys[key]
                wh_flag = True
            elif key in self.wl.keys():
                self.wl[key] = kwargs.keys[key]
                wl_flag = True
            elif key in self.psm.keys():
                self.psm[key] = kwargs.keys[key]
                psm_flag = True
        if config_flag: self.set_config(**self.config)
        if wh_flag: self.set_wh(**self.config)
        if wl_flag: self.set_wl(**self.config)
        if psm_flag: self.set_psm(**self.config)
        return True'''
    '''def set_refresh_time(self,refresh_time):
        # 若未处于省电状态，报错
        #2**config_ALS_IT+5*2**PSM = refresh_time
        t = [(0, 0, 6), (1, 0, 7), (2, 0, 9), (3, 0, 13), (0, 1, 11), (1, 1, 12), (2, 1, 14), (3, 1, 18), (0, 2, 21), (1, 2, 22), (2, 2, 24), (3, 2, 28), (0, 3, 41), (1, 3, 42), (2, 3, 44), (3, 3, 48)]
        for i in t:
            if refresh_time == i[2]:
                return self.setArgs(psm_PSM = i[0],config_ALS_IT = i[1])
        raise Exception(f"no refresh_time like {refresh_time}")'''

if __name__ == '__main__':
    #参数设置
    config =  [VEML7700.CONF_ARGS[key] for key in ['1x','25ms','protect_1','int_disable','als_on']]
    psm = [VEML7700.PSM_ARGS[key] for key in ['psm_1','psm_disable']]
    wh = 0xFF,0xFF
    wl = 0x00,0x00
    i2c = SoftI2C(scl = Pin(18),sda = Pin(19),freq = 400000)
    als = VEML7700(i2c)

    als.set_config(*config)
    als.set_psm(*psm)
    als.set_wh(*wh)
    als.set_wl(*wl)
    for i in range(0,10):
        print(als.read_als_out(),als.read_white_out())
        time.sleep(1)
    

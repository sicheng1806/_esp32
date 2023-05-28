from machine import SoftI2C,Pin
from _device import XGZP,wlan_wait_connected,TCPClient
#import time

if __name__ == '__main__':
    #xgzp
    i2c = SoftI2C(scl=Pin(18),sda=Pin(19),freq=400000)
    xgzp = XGZP(i2c)
    xgzp.setMode(xgzp.CMD_DORMANT_MOD[2])
    #
    wlan,bol = wlan_wait_connected(ssid='wawu',password='long13044')

    obj_addr = ('10.195.86.44',46545)
    tcp_client = TCPClient(obj_addr)
    infos = [("pressure",xgzp.getPress),("temperature",xgzp.getTemp)]
    tcp_client.setInfos(infos)
    tcp_client.connect()
    tcp_client.sends(times = 50)


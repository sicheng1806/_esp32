import network
import time

def wlan_do_connected(ssid,password):
    '''
    example:

    ssid='wawu'

    password='long13044'

    wlan,bl = wlan_do_connected(ssid,password)
    修改日志：

    1.对于wifi无法连接的操作，有两种处理方法，一种是直接抛出错误，另一种是采取堵塞的方式，直到wifi正常连接，不然不会处理，
    分别对应派生出的wlan_must_connected(ssid,password)和wlan_wait_connected(ssid,password)
    '''
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print(f'{ssid} has connected')
        return wlan,True
    if not wlan_is_exit(wlan,ssid):
        print("wlan is not exit")
        return wlan,False
    else:                   #尝试连接十次
        for i in range(10):
            if wlan.isconnected():
                print('wifi connected')
                return wlan,True
            wlan.connect(ssid,password)
            time.sleep(1)
        return wlan,False
    
def wlan_must_connected(ssid,password):
    '''如果wifi无法连接，则报错'''
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print(f'{ssid} is connected')
        return wlan,True
    if not wlan_is_exit(wlan,ssid):
        raise ConnectError("wifi connected failed")
    else:                   #尝试连接十次
        for i in range(10):
            if wlan.isconnected():
                print('wifi connected')
                return wlan,True
            wlan.connect(ssid,password)
            time.sleep(1)
        raise ConnectError("wifi connected failed")

def wlan_wait_connected(ssid,password):
    '''阻塞，直到wifi连接'''
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print(f'{ssid} has connected')
        return wlan,True
    print("WIFI connecting...")
    while not wlan.isconnected():
        try:
            wlan.connect(ssid,password)
            time.sleep(1)
            print('.',end = '')
        except:
            pass
    return wlan,True


def wlan_is_exit(wlan:network.WLAN,ssid):
    flag = False
    for info in wlan.scan():
        if ssid == info[0].decode('utf-8'):
            print(f"Found {ssid}")
            flag = True
            return True
        print('.',end='')
    if not flag:
        print(f"Not Found {ssid}")
        return False

def wlan_AP_open(essid,password = None):
    '''配置wifi热点，放回热点的ifconfig'''
    ap = network.WLAN(network.AP_IF) 
    if password:
        ap.config(essid=essid,password=password)
    else:
        ap.config(essid=essid)
    ap.active(True)
    print("ap open")
    return ap.ifconfig()
def wlan_AP_wait(essid,password = None):
    ap = network.WLAN(network.AP_IF) 
    if password:
        ap.config(essid=essid,password=password)
    else:
        ap.config(essid=essid)
    ap.active(True)
    print(f"{essid} ap open, waiting for connected",end = '')
    while not ap.isconnected():
        print('.',end = '')
        time.sleep(0.5)
    print('')
    return ap.ifconfig()
class ConnectError(Exception):
    pass


if __name__ == '__main__':
    from _device import wlan_AP_open,UDPClient
    essid = "esp32"
    ip,subnet,gateway,dns = wlan_AP_wait(essid = essid)
    obj_address = ('192.168.4.2',46545)
    udp_client = UDPClient(ojb_address=obj_address)
    def handle():
        return "hello"
    infos = [("1",handle),]
    udp_client.setInfos(infos)
    udp_client.sends()
        


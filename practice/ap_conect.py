from _device import wlan_AP_open,UDPClient

if __name__ == '__main__':
    essid = "esp32"
    ip,subnet,gateway,dns = wlan_AP_open(essid = essid)
    obj_address = (ip,46545)
    udp_client = UDPClient(ojb_address=obj_address)
    def handle():
        return "hello"
    infos = [("1",handle),]
    udp_client.setInfos(infos)
    udp_client.sends()
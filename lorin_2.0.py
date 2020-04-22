
from scapy.all import sniff, Dot11
import time
from db import Lorin

data_base = Lorin()


def handle_packet(pkt):
    try:
        if not pkt.haslayer(Dot11):
            if pkt.type == 0 and pkt.subtype == 4:
                mac = pkt.addr2.upper()
                ssid = pkt.info
                data_base.insert_update_log(mac)
                print('\033[95m' + f'Device MAC:  {mac}  with SSID: {ssid}' + '\033[0m')
    except Exception as e:
        print(print('\033[91m An errror occured :>> ' + e))




def main():
    print('\n' + '\033[93m' + 'Wifi Scanner Initialized' + '\033[0m' + '\n')
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default='wlx00e04c3ae8c6', # Change mon0 to your monitor-mode enabled wifi interface
				help='monitor mode enabled interface')
    args = parser.parse_args()
    sniff(iface=args.interface, prn=handle_packet)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

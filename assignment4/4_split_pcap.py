import glob
import numpy as np
from matplotlib import pyplot as plt
from scapy.all import *
from os import walk
from tqdm import tqdm

def check_packet(packet):
    # Assuming we have a standard UDP packet ,
    # which is encapsulated in IP packet , which
    # is itself encapsulated in an Ethernet frame
    ip_packet = packet.payload
    try:
        assert isinstance(ip_packet, IP)
    except AssertionError:
        return False

    udp_packet = ip_packet.payload
    try:      
        assert isinstance(udp_packet, UDP)
    except AssertionError:
        return False

    if udp_packet.dport == 1194:
        if ip_packet.dst == "141.13.99.168":
            return True

    if udp_packet.sport == 1194:
        if ip_packet.src == "141.13.99.168":
            return True
    
    return False


# Setup i/o
output_dir = "./split_pcaps/"
input_file = "./inputs/fingerprinting-traffic.pcap"
f = input_file

# Iterating over all pcap files
log = open("error_log.txt","w")

# Reading in pcap
print("Reading in {}".format(f))
try:
    packet_list = rdpcap(f)
except:
    print("PCAP file {} is broken".format(f))
    log.write("PCAP file {} is broken".format(f))

# time window of 5 seconds
# Access all packets
count = 0
last_cut = 0
pcap_number = 0
split_pcaps = []
for i in tqdm(range(len(packet_list))):

    current_packet = packet_list[i]
    current_time = current_packet.time
    if not check_packet(current_packet):
        continue
    
    count = 0
    for j in range(len(packet_list[i:])):
        if not check_packet(packet_list):
            continue

        if packet_list[j].time - current_time > 5.0:
            #print("5 second window end")
            break
        else:
            count += 1

    if count < 100:
        print("Found a splitting point")
        #split_pcaps.append(packet_list[last_cut:i])
        wrpcap("{}_theirs.pcap".format(pcap_number), packet_list[last_cut:i])
        pcap_number += 1

log.close()

import glob
import numpy as np
from matplotlib import pyplot as plt
from scapy.all import *
from os import walk
from tqdm import tqdm

output = np.zeros((80,2,1300))
i = 0
log = open("error_log.txt","w")
for f in glob("./pcaps/*.pcap"):
    # Reading in pcap
    print("Reading in {}".format(f))
    try:
        packet_list = rdpcap(f)
    except:
        print("PCAP file {} is broken".format(f))
        log.write("PCAP file {} is broken".format(f))
        continue
    # Setup vectors
    received = np.zeros(1300)
    sent = np.zeros(1300)

    # Access all packets
    for packet in tqdm(packet_list):
        try:
            packet_length = packet.len
        except:
            print("Packet broken")
            continue
        timestamp = packet.time

        # Assuming we have a standard UDP packet ,
        # which is encapsulated in IP packet , which
        # is itself encapsulated in an Ethernet frame
        ip_packet = packet.payload
        try:
            assert isinstance(ip_packet, IP)
        except AssertionError:
            continue

        udp_packet = ip_packet.payload
        try:      
            assert isinstance(udp_packet, UDP)
        except AssertionError:
            continue

        if udp_packet.dport == 1194:
            if ip_packet.dst == "141.13.99.168":
                received[int(packet_length)] += 1

        if udp_packet.sport == 1194:
            if ip_packet.src == "141.13.99.168":
                sent[int(packet_length)] += 1
    
    output[i,0,:] = received
    output[i,1,:] = sent

    i += 1
    # Plotting
    #packet_lengths = [packet.len for packet in packet_list]
    #plt.hist(received, log=True)
    #plt.show()

np.save("fingerprints.npy", output, allow_pickle=False)
log.close()

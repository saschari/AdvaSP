import glob
import numpy as np
from matplotlib import pyplot as plt
from scapy.all import *
from os import walk
from tqdm import tqdm

# Setup i/o
output_file = "fingerprints_theirs.npy"
input_dir = "./split_pcaps/*.pcap"

# Initializing output matrix (80 sites, 2 vecors, 1300 packet sizes)
output = np.zeros((17,2,1300))

# Iterating over all pcap files
i = 0
log = open("error_log.txt","w")
for f in glob(input_dir):
    
    #file_number = f[f.rfind("/")+1:f.find(".pcap")]
    file_number = f[f.rfind("/")+1:f.rfind("_theirs")]
    print(file_number)

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
            #print(packet_length)
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
    
    # Save vectors into output matrix
    output[int(file_number),0,:] = received
    output[int(file_number),1,:] = sent

    i += 1
    # Plotting
    #packet_lengths = [packet.len for packet in packet_list]
    #plt.hist(received, log=True)
    #plt.show()

np.save(output_file, output, allow_pickle=False)
log.close()

import os
from matplotlib import pyplot as plt
from scapy.all import *

# Reading in pcap
packet_list = rdpcap('pcaps/2.pcap')
print(packet_list.summary())

# Access first packet
first_packet = packet_list[0]
print(first_packet.summary())

# Access all packets
'''
for packet in packer_list:
    print(packet.summary())
    packet.display()
    packet_length = packet.len
    timestamp = packet.time

    # Assuming we have a standard UDP packet ,
    # which is encapsulated in IP packet , which
    # is itself encapsulated in an Ethernet frame
    ip_packet = packet.payload
    assert isinstance(ip_packet, IP)
    udp_packet = ip_packet.payload
    assert isinstance(udp_packet, UDP)

    destination_port = udp_packet.dport
    source_port = udp_packet.sport
'''
# Plotting
packet_lengths = [packet.len for packet in packet_list]
plt.hist(packet_lengths)
plt.show()

#!/usr/bin/env python3
"""
Extensive example script for using pychrome.

In order to use this script, you have to start Google Chrome/Chromium
with remote debugging as follows:
    google-chrome --remote-debugging-port=9222 --enable-automation

You can also run in headless mode, which doesn't require a graphical
user interface by supplying --headless.
"""

import pprint
import pychrome
import json
import re
import os
import subprocess

current_page = ''
last_page = ''
ga_count = 0
aip_set = False

class Crawler:
    def __init__(self, debugger_url='http://127.0.0.1:9222'):
        # Create a browser instance which controls Google Chrome/Chromium
        self.browser = pychrome.Browser(url=debugger_url)

    def open_page(self, url, wait_time = 10):
        # Create a tab
        self.tab = self.browser.new_tab()

        # Start our tab after callbacks have been registered
        self.tab.start()

        # Enable network notifications for all request/response so our
        # callbacks actually receive some data.
        #self.tab.Network.enable()

        # Enable page domain notifications so our load_event_fired
        # callback is called when the page is loaded.
        #self.tab.Page.enable()

        # Navigate to a specific page
        self.tab.Page.navigate(url=url, _timeout=5)

        # Wait some time for events. This will wait until tab.stop()
        # is called or the timeout of 10 seconds is reached.
        # In this case we wait for our load event to be fired (see
        # `cb_load_event_fired`)
        self.tab.wait(wait_time)

        # Close tab
        self.browser.close_tab(self.tab)


def main():

    # Remove previous file
    os.remove("results/results.txt")

    # Initialize chrome and wait until startup finished
    p_chrome = subprocess.Popen(['google-chrome', '--remote-debugging-port=9222', '--enable-automation', '--headless'],stdout=subprocess.PIPE)
    c = Crawler()
    c.Network.setCacheDisabled(True)
    sys.wait(10)
    
    links = open("fingerprinting-sites.txt", "r")
    for line in links:
        if len(line) > 1:
            s = line.rstrip()           
            
            # Name for pcap file
            pcap_out = re.search("^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)", s)
            if pcap_out:
                pcap_out = pcap_out(1)
            
            # Start tcpdump as subprocess
            p = subprocess.Popen(['tcpdump', '-i', 'enp0s3', '-w', pcap_out + '.pcap'], stdout=subprocess.PIPE)
            
            # Open the current page
            global current_page, ga_count, aip_set
            current_page = s
            c.open_page(line, wait_time = 30)

            # Stop tcpdump
            p.send_signal(subprocess.signal.SIGTERM)
    
    p_chrome.send_signal(subprocess.signal.SIGTERM)

if __name__ == '__main__':
    main()

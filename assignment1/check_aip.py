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

class Crawler:
    def __init__(self, debugger_url='http://127.0.0.1:9222'):
        # Create a browser instance which controls Google Chrome/Chromium
        self.browser = pychrome.Browser(url=debugger_url)

    def crawl_page(self, url):
        # Create a tab
        self.tab = self.browser.new_tab()

        # Set callbacks for request in response logging
        self.tab.Network.requestWillBeSent = self.cb_request_will_be_sent
        self.tab.Network.responseReceived = self.cb_response_received
        self.tab.Page.loadEventFired = self.cb_load_event_fired
        
        # Start our tab after callbacks have been registered
        self.tab.start()
        
        # Enable network notifications for all request/response so our
        # callbacks actually receive some data.
        self.tab.Network.enable()

        # Enable page domain notifications so our load_event_fired
        # callback is called when the page is loaded.
        self.tab.Page.enable()
        
        # Navigate to a specific page
        self.tab.Page.navigate(url=url, _timeout=5)
        
        # Wait some time for events. This will wait until tab.stop()
        # is called or the timeout of 10 seconds is reached.
        # In this case we wait for our load event to be fired (see
        # `cb_load_event_fired`)
        self.tab.wait(10)

        # Close tab
        self.browser.close_tab(self.tab)

    def cb_request_will_be_sent(self, request, **kwargs):
        """Will be called when a request is about to be sent.

        Those requests can still be blocked or intercepted and modified.
        This example script does not use any blocking or intercepting.

        Note: It does not say anything about the request being sucessful,
        there can still be connection issues.
        """
        request_string = json.dumps(request)
        output = open("results.txt", "a")
        for m in re.finditer('aip', request_string):
            aipString = request_string[m.start():m.start()+10]
            if "aip=1" in aipString or "aip = 1" in aipString:
                print("++++ Request +++++")
                print("GA is used correctly: %s" %aipString)
                output.write("++++ Request +++++")
                output.write("GA is used correctly: %s" %aipString)
            else:
                print("++++ Request +++++")
                print("GA is not used correctly: %s" %aipString)
                output.write("++++ Request +++++")
                output.write("GA is not used correctly: %s" %aipString)
                
        output.close()
        #pprint.pprint(request)

    def cb_response_received(self, response, **kwargs):
        """Will be called when a response is received.

        This includes the originating request which resulted in the
        response being received.
        """
        response_string = json.dumps(response)
        output = open("results.txt", "a")
        for m in re.finditer('aip', response_string):
            aipString = response_string[m.start():m.start()+10]
            if "aip=1" in aipString or "aip = 1" in aipString:
                print("++++ Request +++++")
                print("GA is used correctly: %s" %aipString)
                output.write("++++ Request +++++")
                output.write("GA is used correctly: %s" %aipString)
            else:
                print("++++ Request +++++")
                print("GA is not used correctly: %s" %aipString)
                output.write("++++ Request +++++")
                output.write("GA is not used correctly: %s" %aipString)
        output.close()
        
        #pprint.pprint(response)

    def cb_load_event_fired(self, timestamp, **kwargs):
        """Will be called when the page sends an load event.

        Note that this only means that all resources are loaded, the
        page may still processes some JavaScript.
        """
        # Give the page one second for further processing
        self.tab.wait(1)

        # Run a JavaScript expression on the page.
        # If Google Analytics is included in the page, this expression will tell you
        # whether the site owner's wanted to enable anonymize IP. The expression will
        # fail with a JavaScript exception if Google Analytics is not in use.
        result = self.tab.Runtime.evaluate(expression="ga.getAll()[0].get('anonymizeIp')")
        
        # Check the result if it contains "ga not found" --> if no, GA is used on the page
        result_string = json.dumps(result)
        if result_string.find("ga is not") <= 0:
            #pprint.pprint(result)
            pprint.pprint("Website uses GA")        
        #output = open("results.txt", "a")
        #output.write(json.dumps(result) + "\n")
        #output.close()

        # Stop the tab
        self.tab.stop()


def main():

    # Remove previous file
    if os.path.isfile("results.txt"):
        os.remove("results.txt")
    
    c = Crawler()
    links = open("versicherungs-websites.txt", "r")
    for line in links:
        if len(line) > 1: 
            line.rstrip()
            print("----------%s----------" %line)
            c.crawl_page(line)


if __name__ == '__main__':
    main()

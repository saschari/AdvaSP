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
import pandas as pd
import matplotlib.pyplot as plt

requests = pd.DataFrame(columns=['CrawledSite', 'URL', 'Site', 'Method', 'Origin'])
responses = pd.DataFrame(columns=['CrawledSite', 'URL', 'Site', 'Content-type', 'IP', 'Status'])
current_page = ''

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
        #pprint.pprint(request)
        print("--- REQUEST ---\n")
        crawled_page = ''
        if kwargs is not None:
            crawled_page = kwargs['initiator']
        url = request['url']
        wwwPos = request['url'].find("://") + 3
        domainPos = request['url'].find("/", wwwPos)
        site = request['url'][wwwPos:domainPos]
        method = request['method']
        origin = ''
        if "headers" in request:
            if "Origin" in request['headers']:
                origin = request['headers']['Origin']

        print("URL: " + url)
        print("Site: " + site)
        print("HTTP method: " + method)
        print("Origin: " + origin)

        requests.loc[len(requests)] = [current_page, url, site, method, origin]


    def cb_response_received(self, response, **kwargs):
        """Will be called when a response is received.

        This includes the originating request which resulted in the
        response being received.
        """

        print("--- RESPONSE ---")
        crawled_page = ''
        url = response['url']
        wwwPos = response['url'].find("://") + 3
        domainPos = response['url'].find("/", wwwPos)
        site = response['url'][wwwPos:domainPos]
        content_type = ''
        if "headers" in response:
            if "content-type" in response['headers']:
                content_type = response['headers']['content-type']
        ip = response['remoteIPAddress']
        status = str(response['status'])

        print("URL: " + url)
        print("Site: " + site)
        print("Content type: " + content_type)
        print("IP: " + ip)
        print("Status: " + status)

        responses.loc[len(responses)] = [current_page, url, site, content_type, ip, status]

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

        # Stop the tab
        self.tab.stop()


def main():

    # Read sites to crawl
    sites = []
    links = open("versicherungs-websites.txt", "r")
    for line in links:
        if len(line) > 1:
            line = line.rstrip()
            sites.append(line)
    links.close()

    # Remove previous file
    if not (os.path.isfile("requests.csv") and os.path.isfile("responses.csv")):
        # Crawl all links from text file
        c = Crawler()
        for s in sites:
            print("----------%s----------" %s)
            global current_page
            current_page = s
            c.crawl_page(s)

        # Save findings as csv
        requests.to_csv("requests.csv", sep=';', encoding='utf-8')
        responses.to_csv("responses.csv", sep=';', encoding='utf-8')
    else:
        requests_load = pd.read_csv("requests.csv", sep=";")
        responses_load = pd.read_csv("responses.csv", sep=";")

        # Remove query URLs
        for s in sites:
            start = s.find(".")+1
            end = s.find(".", start)
            s = s[start:end]
            requests_load = requests_load[requests_load.Site.str.contains(s) == False]
            responses_load = responses_load[responses_load.Site.str.contains(s) == False]

        # Plots for requests
        dist = requests_load.groupby(['Site'])['Site'].count().reset_index(name='distribution')
        dist_groups = requests_load.groupby(['CrawledSite','Site'])['Site'].count().reset_index(name='distribution')

        dist_groups.groupby(['CrawledSite'])['distribution'].sum().reset_index(name='sum').plot.bar(x='CrawledSite', y='sum', title='Responses from third parties by start URL', rot=65)
        plt.tight_layout()
        plt.savefig('plots\\third_parties_per_url.png')
        #dist['distribution'] = dist['distribution'] / dist['distribution'].sum()

        for index, group in dist_groups.groupby('CrawledSite'):
            group.plot.bar(x='Site', y='distribution', title=index, rot=25)
            start = index.find(".")+1
            end = index.find(".", start)
            plt.tight_layout()
            plt.savefig('plots\\' + index[start:end] + '_third_parties.png')

        # Plots for responses
        resp_status_dist = responses_load.groupby(['Status'])['Status'].count().reset_index(name='distribution')
        resp_status_dist.plot.bar(x='Status', y='distribution', title='Number of status codes for all responses',rot=45)
        plt.savefig('plots\\responses_status_codes.png')


if __name__ == '__main__':
    main()

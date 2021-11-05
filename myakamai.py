from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

import requests
import datetime
import os


class MyAkamai():
    ''' Akamai class that creates an EdgeGridAuth API connection using 'default' section from .edgerc file from $HOME '''

    def __init__(self, section='default', switchkey=""):
        self.edgerc = EdgeRc('{}/.edgerc'.format(os.environ.get('HOME')))
        self.section = section
        self.baseurl = 'https://%s' % self.edgerc.get(self.section, 'host')

        # our account switchkey so we can check any account, GSS only!
        self.ask = switchkey

        # set start and end date
        # let's use an interval of 7 days
        interval = 7
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(interval)

        # define our start end end date and they should be at least two chars long.
        self.start = f"{start_date.year}-{start_date.month:02}-{start_date.day:02}"
        self.end = f"{end_date.year}-{end_date.month:02}-{end_date.day:02}"

        self.s = requests.Session()
        self.s.auth = EdgeGridAuth.from_edgerc(self.edgerc, self.section)

    def get_hits_by_cpcode(self, cpcodes: list) -> list:
        ''' return offload percentages per cpcode. Argument should be a list with zero or more cpcodes'''

        # our request body. A dict which will be transferred to json by requests module
        # cpcodes should be an array but can be empty to get all cpcodes.
        body = {"objectType": "cpcode", "objectIds": cpcodes}

        # create our url to lookup the bytes-by-cpcode statistics
        # https://developer.akamai.com/api/core_features/reporting/bytes-by-cpcode.html
        url = urljoin(
            self.baseurl, 'reporting-api/v1/reports/bytes-by-cpcode/versions/1/report-data?start={}T00%3A00%3A00Z&end={}T00%3A00%3A00Z&interval=HOUR&accountSwitchKey={}'.format(self.start, self.end, self.ask))

        # let's get our results. requests module will convert to json.
        r = self.s.post(url, json=body)

        # if we have some resuls, only return data part from results
        if r.status_code == requests.codes.ok:
            results = r.json()
            return(results["data"])

        # just return empty list if anthing went wrong.
        return([])

    def get_urls_by_cpcode(self, cpcodes: list) -> list:
        ''' return list of urls. Argument should be a list with zero or more cpcodes'''

        # our request body. A dict which will be transferred to json by requests module
        # cpcodes should be an array but can be empty to get all cpcodes and we can include a filter
        body = {"objectType": "cpcode", "objectIds": cpcodes}

        # we can add a filters to the POST body including a regex via url_match
        # in this example we're just filtering some extensions we know that can be cached
        # this will match .woff and .woff2 but only .js files, json is ignored.
        # you can extend this to any object you know is capable of being cached
        body["filters"] = {"url_match": ["\\.woff|\\.js$"]}

        # create our url to lookup the bytes-by-cpcode statistics
        # https://developer.akamai.com/api/core_features/reporting/urlbytes-by-url.html
        url = urljoin(
            self.baseurl, 'reporting-api/v1/reports/urlbytes-by-url/versions/1/report-data?start={}T00%3A00%3A00Z&end={}T00%3A00%3A00Z&interval=DAY&accountSwitchKey={}'.format(self.start, self.end, self.ask))

        print(url)
        # let's get our results. requests module will convert to json.
        r = self.s.post(url, json=body)

        # if we have some resuls, only return data part from results
        if r.status_code == requests.codes.ok:
            results = r.json()
            return(results["data"])

        # just return empty list if anthing went wrong.
        return([])


if __name__ == '__main__':
    # accountSwitchKey (Akamai internal)
    accountSwitchKey = ""

    # user cpcodes list to filter on specific cpcodes
    cpcodes = []
    section = 'gss'

    reporting = MyAkamai(section, accountSwitchKey)
    # print(reporting.get_hits_by_cpcode(cpcodes))

    # now let's load our list as a panda's dataframe
    print(reporting.get_urls_by_cpcode(cpcodes))

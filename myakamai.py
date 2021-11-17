from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

import requests
import datetime
import os

from requests import status_codes


class MyAkamai():
    ''' Akamai class that creates an EdgeGridAuth API connection using 'default' section from .edgerc file from $HOME '''

    def __init__(self, section='default'):
        self.edgerc = EdgeRc('{}/.edgerc'.format(os.environ.get('HOME')))
        self.section = section
        self.baseurl = 'https://%s' % self.edgerc.get(self.section, 'host')

        # our account switchkey so we can check any account, GSS only!
        # set environment var to get it, none if not set.
        self.ask = os.getenv('ASK')
        print(f"using accountSwitchKey: {self.ask}")

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
        # convert json to dict and only return data part
        if r.status_code == requests.codes.ok:
            results = r.json()
            return(results["data"])

        # just return empty list if anthing went wrong.
        return([])

    def get_urls_by_cpcode(self, cpcodes: list) -> list:
        ''' return list of urls. Argument should be a list with zero or more cpcodes'''

        # our request body. A dict which will be transferred to json by requests module
        # cpcodes should be an array but can be empty to get all cpcodes and we can include a filter
        body = {"objectType": "cpcode", "objectIds": cpcodes, "limit": 10000}

        # we can add a filters to the POST body including a regex via url_match
        # in this example we're just filtering some extensions we know that can be cached
        # this will match .woff and .woff2 but only .js files, json is ignored etc.
        # you can extend this to any object/path you know is capable of being cached
        body["filters"] = {"url_match": ["\\.woff|\\.js$|\\.png$|\\.svg"]}

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

    def get_all_cpcodes(self):
        ''' return a dict with all cpcodeId:cpcodeName '''

        # create an empty dict
        cpcodes = {}

        # create our url to get all the cpcodes
        # https://techdocs.akamai.com/cp-codes/reference/cpcodes
        url = urljoin(
            self.baseurl, '/cprg/v1/cpcodes?accountSwitchKey={}'.format(self.ask))

        # get al cpcodes from our cpcodes endpoint
        r = self.s.get(url)

        # if everthing is ok, let create a dict with our cpcode info
        if r.status_code == requests.codes.ok:
            results = r.json()

            # using dictionary comprehension we're creating a dict with cpcodeId:cpcodeName
            cpcodes = {cpcode['cpcodeId']: cpcode['cpcodeName']
                       for cpcode in results['cpcodes']}

        # just return the empty dict if anything went wrong
        return(cpcodes)


if __name__ == '__main__':
    # user cpcodes list to filter on specific cpcodes
    cpcodes = []
    section = 'gss'

    reporting = MyAkamai(section)
    # print(reporting.get_hits_by_cpcode(cpcodes))

    # now let's get our cpcode dictionary
    cpcodes = reporting.get_all_cpcodes()
    print(cpcodes)

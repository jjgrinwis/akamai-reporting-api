from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

import requests
import datetime


class MyClass(object):
    def __init__(self, switchkey):
        self.edgerc = EdgeRc('/Users/jgrinwis/.edgerc')
        self.section = 'gss'
        self.baseurl = 'https://%s' % self.edgerc.get(self.section, 'host')

        # our account switchkey so we can check any account, GSS only!
        self.ask = switchkey

        self.s = requests.Session()
        self.s.auth = EdgeGridAuth.from_edgerc(self.edgerc, self.section)

    def get_hits_by_cpcode(self, cpcodes: list) -> list:
        ''' return offload percentages per cpcode. Argument should be a list with zero or more cpcodes'''

        # our request body. A dict which will be transferred to json by requests module
        # cpcodes should be an array but can be empty to get all cpcodes.
        body = {"objectType": "cpcode", "objectIds": cpcodes}

        # let's use an interval of 7 days
        interval = 7
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(interval)

        # define our start end end date and they should be at least two chars long.
        start = f"{start_date.year}-{start_date.month:02}-{start_date.day:02}"
        end = f"{end_date.year}-{end_date.month:02}-{end_date.day:02}"

        # create our url to lookup the bytes-by-cpcode statistics
        # https://developer.akamai.com/api/core_features/reporting/bytes-by-cpcode.html
        url = urljoin(
            self.baseurl, 'reporting-api/v1/reports/bytes-by-cpcode/versions/1/report-data?start={}T10%3A00%3A00Z&end={}T12%3A00%3A00Z&interval=HOUR&accountSwitchKey={}'.format(start, end, self.ask))

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

    reporting = MyClass(accountSwitchKey)
    print(reporting.get_hits_by_cpcode(cpcodes))

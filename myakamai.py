# pylint: disable=E1101
from urllib.parse import urljoin

import datetime
import os
import requests

from akamai.edgegrid import EdgeGridAuth, EdgeRc


class MyAkamai:
    """Akamai class that creates an EdgeGridAuth API connection.
    using 'default' section from .edgerc file from $HOME"""

    def __init__(self, section="default"):
        self.section = section
        self.edgerc = EdgeRc(f"{os.environ.get('HOME')}/.edgerc")
        self.baseurl = f"https://{self.edgerc.get(self.section, 'host')}"

        # our account switchkey so we can check any account, GSS only!
        # set environment var to get it, none if not set.
        self.ask = os.getenv("ASK")
        print(f"using accountSwitchKey: {self.ask}")

        # set start and end date
        # let's use an interval of 7 days
        interval = 7
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(interval)

        # define our start end end date and they should be at least two chars long.
        self.start = f"{start_date.year}-{start_date.month:02}-{start_date.day:02}"
        self.end = f"{end_date.year}-{end_date.month:02}-{end_date.day:02}"

        self.ses = requests.Session()
        self.ses.auth = EdgeGridAuth.from_edgerc(self.edgerc, self.section)

    def get_hits_by_cpcode(self, cpcodes: list) -> list:
        """return offload percentages per cpcode.
        Argument should be a list with zero or more cpcodes"""

        # our request body. A dict which will be transferred to json by requests module
        # cpcodes should be an array but can be empty to get all cpcodes.
        body = {"objectType": "cpcode", "objectIds": cpcodes}

        # create our url to lookup the bytes-by-cpcode statistics
        # https://developer.akamai.com/api/core_features/reporting/bytes-by-cpcode.html
        url = urljoin(
            self.baseurl,
            f"reporting-api/v1/reports/bytes-by-cpcode/versions/1/report-data?start={self.start}"
            f"T00%3A00%3A00Z&end={self.end}T00%3A00%3A00Z&interval=HOUR&"
            f"accountSwitchKey={self.ask}",
        )

        # let's get our results. requests module will convert to json.
        req = self.ses.post(url, json=body)

        # if we have some resuls, only return data part from results
        # convert json to dict and only return data part
        if req.status_code == requests.codes.ok:
            results = req.json()
            return results["data"]

        # just return empty list if anthing went wrong.
        return []

    def get_urls_by_cpcode(self, cpcodes: list) -> list:
        """return list of urls. Argument should be a list with zero or more cpcodes"""

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
            self.baseurl,
            f"reporting-api/v1/reports/urlbytes-by-url/versions/1/report-data?start={self.start}"
            f"T00%3A00%3A00Z&end={self.end}T00%3A00%3A00Z&interval=DAY&accountSwitchKey={self.ask}",
        )

        # print(url)
        # let's get our results. requests module will convert body dict to json.
        req = self.ses.post(url, json=body)

        # if we have some resuls, only return data part from results
        if req.status_code == requests.codes.ok:
            results = req.json()
            return results["data"]

        # just return empty list if anthing went wrong.
        return []

    def get_all_cpcodes(self):
        """return a dict with all cpcodeId:cpcodeName"""

        cpcodes = {}

        # create our url to get all the cpcodes
        # https://techdocs.akamai.com/cp-codes/reference/cpcodes
        url = urljoin(self.baseurl, f"/cprg/v1/cpcodes?accountSwitchKey={self.ask}")

        # get al cpcodes from our cpcodes endpoint
        request = self.ses.get(url)

        # if everthing is ok, let's create a dict with our cpcode info
        if request.status_code == requests.codes.ok:
            results = request.json()

            # using dictionary comprehension we're creating a dict with cpcodeId:cpcodeName
            cpcodes = {
                cpcode["cpcodeId"]: cpcode["cpcodeName"]
                for cpcode in results["cpcodes"]
            }

        # just return the empty dict if anything went wrong
        return cpcodes


if __name__ == "__main__":
    # user cpcodes list to filter on specific cpcodes
    cpcode_list = []
    SECTION = "gss"

    reporting = MyAkamai(SECTION)
    # print(reporting.get_hits_by_cpcode(cpcodes))

    # now let's get our cpcode dictionary
    cpcode_list = reporting.get_all_cpcodes()
    print(cpcode_list)

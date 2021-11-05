from numpy import int16, int64
from numpy.core.numeric import outer
from myakamai import MyAkamai
import pandas as pd


if __name__ == '__main__':
    # accountSwitchKey (Akamai internal)
    accountSwitchKey = ""
    section = ''

    # user cpcodes list to filter on specific cpcodes
    cpcodes = []

    reporting = MyAkamai(section, accountSwitchKey)
    # print(reporting.get_hits_by_cpcode(cpcodes))

    # now let's load our list as a panda's dataframe and set correct type and numer of decimals
    # the from_dict is setting everything column to an object(df.info())
    df = pd.DataFrame.from_dict(reporting.get_urls_by_cpcode(cpcodes))
    df = df.astype({"allEdgeBytes": int})
    df = df.astype({"allOriginBytes": int})
    df = df.astype({"allBytesOffload": float})
    df['allBytesOffload'] = df['allBytesOffload'].round(decimals=2)

    # let's sort our results on offload and edgebytes
    output = (df.sort_values(
        ['allBytesOffload', 'allEdgeBytes'], ascending=[True, False]))

    print(output.head(100))

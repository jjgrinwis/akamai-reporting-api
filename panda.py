from numpy import int16, int64
from numpy.core.numeric import outer
from myakamai import MyAkamai
import pandas as pd


if __name__ == '__main__':
    # accountSwitchKey (Akamai internal)
    accountSwitchKey = ""
    section = 'gss'

    # cpcodes list to filter on specific cpcodes
    cpcodes = []

    reporting = MyAkamai(section, accountSwitchKey)
    # print(reporting.get_hits_by_cpcode(cpcodes))

    # now let's load our list as a panda's dataframe and set correct type and numer of decimals
    # the from_dict is setting every column to an object(df.info()) so we need to fix that.
    df = pd.DataFrame.from_dict(reporting.get_urls_by_cpcode(cpcodes))
    df = df.astype({"allEdgeBytes": int})
    df = df.astype({"allOriginBytes": int})
    df = df.astype({"allBytesOffload": float})
    df['allBytesOffload'] = df['allBytesOffload'].round(decimals=2)

    print(f"{len(df.index)} items found based on used regex\n")

    # let's get everything with <50% offload
    bad_offload = df[df['allBytesOffload'] < 50]

    # let's sort our results on offload and edgebytes
    output = (bad_offload.sort_values(
        ['allBytesOffload', 'allEdgeBytes'], ascending=[True, False]))

    print(f"we have {len(output.index)} objects with a low offload %\n")

    # let's creat a .csv with all objects with a low offload and let's ignore the index
    output.to_csv(f"results/{reporting.end}.csv", index=False)

    print(
        f"top 5 files with low offload. The complete list can be found here: results/{reporting.end}.csv\n")
    print(output.head(5))

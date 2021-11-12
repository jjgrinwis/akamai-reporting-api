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

    # offload minimum
    offload = 70

    # create connection to Akamai reporting API endpoint.
    reporting = MyAkamai(section, accountSwitchKey)

    # now let's load our list as a panda's dataframe and set correct type and numer of decimals
    # the from_dict is setting every column to an object(df.info()) so we need to fix that.
    # we should be able to use "pd.DataFrame.from_dict(d, orient='columns').astype({'a':int,'b':int})""
    df = pd.DataFrame.from_dict(reporting.get_hits_by_cpcode(cpcodes))
    df = df.astype({"edgeBytes": int})
    df = df.astype({"cpcode": int})
    df = df.astype({"originBytes": int})
    df = df.astype({"midgressBytes": int})
    df = df.astype({"bytesOffload": float})
    df['bytesOffload'] = df['bytesOffload'].round(decimals=2)

    # now lets sort on low offload with high edgebytes
    bad_offload = df[df['bytesOffload'] < offload]

    print(
        f"found {len(bad_offload.index)} cpcodes with a offload lower than {offload}%\n")

    # let's sort our results on delivered edgebytes
    output = (bad_offload.sort_values(
        ['edgeBytes'], ascending=[False]))

    # let's get our dict of cpcodeId:cpcodeName
    # this is going to be used to map a cpcode to cpcodeName
    cpcodes = reporting.get_all_cpcodes()

    # now create a new column with the cpcodename mapping in this dataframe
    # it will now be end of the list, we might want to resort it.
    output["cpcodeName"] = output["cpcode"].map(cpcodes)
    print(output.head(10))

    # dump results to csv
    output.to_csv(f"results/cpcodes-{reporting.end}.csv", index=False)

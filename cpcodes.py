import pandas as pd
from myakamai import MyAkamai


if __name__ == "__main__":
    # our section from .edgerc file
    SECTION = "gss"

    # cpcodes list to filter on specific cpcodes
    cpcodes = []

    # offload minimum percentage
    OFFLOAD = 70

    # create connection to Akamai reporting API endpoint.
    reporting = MyAkamai(SECTION)

    # now let's load our list as a panda's dataframe and set correct type and numer of decimals
    # the from_dict is setting every column to an object(df.info()) so we need to fix that.
    df = pd.DataFrame.from_dict(reporting.get_hits_by_cpcode(cpcodes)).astype(
        {
            "edgeBytes": int,
            "cpcode": int,
            "originBytes": int,
            "midgressBytes": int,
            "bytesOffload": float,
        }
    )
    df["bytesOffload"] = df["bytesOffload"].round(decimals=2)

    # now lets sort on low offload with high edgebytes
    bad_offload = df[df["bytesOffload"] < OFFLOAD]

    print(
        f"found {len(bad_offload.index)} cpcodes with a offload lower than {OFFLOAD}%\n"
    )

    # let's sort our results on delivered edgebytes
    output = bad_offload.sort_values(["edgeBytes"], ascending=[False])

    # get our dict of cpcodeId:cpcodeName to map a cpcode to cpcodeName in dataframe
    cpcodes = reporting.get_all_cpcodes()

    # now create a new column with the cpcodename mapping in this dataframe
    # it will now be end of the list, we might want to resort it.
    output["cpcodeName"] = output["cpcode"].map(cpcodes)
    print(output.head(10))

    # dump results to csv
    output.to_csv(f"results/cpcodes-{reporting.end}.csv", index=False)

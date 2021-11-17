import pandas as pd
from myakamai import MyAkamai


if __name__ == "__main__":
    # section part from the .edgerc file
    SECTION = "gss"

    # cpcodes list to filter on specific cpcodes
    cpcodes = []

    # offload percentage
    OFFLOAD = 50

    # create connection to Akamai reporting API endpoint.
    reporting = MyAkamai(SECTION)

    # now let's load our list as a panda's dataframe and set the correc decimals.
    # the from_dict is setting every column to an object(df.info()) so we need to fix that.
    # there should be a better way of setting the types per column.
    df = pd.DataFrame.from_dict(reporting.get_urls_by_cpcode(cpcodes))
    df = df.astype({"allEdgeBytes": int})
    df = df.astype({"allOriginBytes": int})
    df = df.astype({"allBytesOffload": float})
    df["allBytesOffload"] = df["allBytesOffload"].round(decimals=2)

    print(f"{len(df.index)} items found based on used regex\n")

    # let's get everything with <50% offload
    bad_offload = df[df["allBytesOffload"] < OFFLOAD]

    # let's sort our results on offload and edgebytes
    output = bad_offload.sort_values(
        ["allBytesOffload", "allOriginBytes"], ascending=[True, False]
    )

    print(f"we have {len(output.index)} objects with a offload of {OFFLOAD}%\n")

    # let's creat a .csv with all objects with a low offload and let's ignore the index
    output.to_csv(f"results/urls-{reporting.end}.csv", index=False)

    print(
        f"Below a list with the top 5 files with a low offload.\n"
        f"The complete list can be found here: results/{reporting.end}.csv\n"
    )

    print(output.head(5))

    # next up we can do a request for a couple of file to check the cache-control header
    # to be continued....

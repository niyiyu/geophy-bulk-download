import os
import re
import xml.etree.ElementTree as ET

import pandas as pd
import requests
from tqdm import tqdm


def remove_invalid_xml_chars(s):
    return re.sub(r"[^\x09\x0A\x0D\x20-\x7F]", "", s)


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

url = "https://oaipmh.arxiv.org/oai"

if __name__ == "__main__":
    if os.path.exists("../metadata/arxiv.csv"):
        preprints = pd.read_csv("../metadata/arxiv.csv")
    else:
        ############# get identifier
        response = requests.get(
            url
            + "?verb=ListIdentifiers&metadataPrefix=oai_dc&set=physics:physics:geo-ph"
        )
        root = ET.fromstring(response.content.decode("utf-8"))

        preprints = []
        for i in root[2]:
            if "geo-ph" in i[2].text:
                preprints.append(
                    {"identifier": i[0].text, "date": i[1].text, "set": i[2].text}
                )

        preprints = pd.DataFrame(preprints)

    for idx, r in preprints.iterrows():
        if "download" in r:
            continue
        preprints.loc[idx, "download"] = (
            "https://arxiv.org/pdf/" + r["identifier"].split(":")[-1]
        )

    preprints.to_csv("../metadata/arxiv.csv", index=False)

    ############# download file
    for idp, p in tqdm(preprints.iterrows(), total=len(preprints)):
        if pd.isna(p["download"]):
            continue
        filename = (
            "../PDF/arxiv/"
            + p["identifier"].replace(":", "_").replace("/", "-")
            + ".pdf"
        )
        if os.path.exists(filename):
            continue
        response = requests.get(p["download"], headers=headers)
        with open(filename, "wb") as f:
            f.write(response.content)

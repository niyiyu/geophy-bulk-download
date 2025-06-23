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

url = "https://seismica.library.mcgill.ca/oai"

if __name__ == "__main__":
    if os.path.exists("../metadata/seismica.csv"):
        preprints = pd.read_csv("../metadata/seismica.csv")
    else:
        ############# get identifier
        response = requests.get(
            url + "?verb=ListIdentifiers&from=2015-01-01&metadataPrefix=oai_dc"
        )
        root = ET.fromstring(response.content.decode("utf-8"))

        preprints = []
        for i in root[2]:
            if len(i) == 3:
                preprints.append(
                    {"identifier": i[0].text, "date": i[1].text, "set": i[2].text}
                )
            else:
                resumptionToken = i.text

        while resumptionToken:
            response = requests.get(
                url
                + "?verb=ListIdentifiers&metadataPrefix=oai_dc&from=1998-01-15&resumptionToken="
                + resumptionToken
            )
            root = ET.fromstring(response.content.decode("utf-8"))
            resumptionToken = None
            for i in root[2]:
                if len(i) == 3:
                    preprints.append(
                        {"identifier": i[0].text, "date": i[1].text, "set": i[2].text}
                    )
                else:
                    resumptionToken = i.text

        preprints = pd.DataFrame(preprints)

    ############# get record and download link
    for idx, r in tqdm(preprints.iterrows(), total=len(preprints)):
        if "download" in r:
            continue
        response = requests.get(
            url + "?verb=GetRecord&metadataPrefix=oai_dc&identifier=" + r["identifier"]
        )
        root = ET.fromstring(remove_invalid_xml_chars(response.content.decode("utf-8")))
        if len(root[2][0]) == 1:
            preprints.loc[idx, "download"] = ""
        else:
            for c in root[2][0][1][0]:

                if ("https://seismica.library.mcgill.ca/article/view" in c.text) and (
                    "relation" in c.tag
                ):
                    preprints.loc[idx, "download"] = c.text.replace("view", "download")
                    break

    preprints.to_csv("../metadata/seismica.csv", index=False)

    ############# download file
    for idp, p in tqdm(preprints.iterrows(), total=len(preprints)):
        if pd.isna(p["download"]):
            continue
        filename = (
            "../PDF/seismica/"
            + p["identifier"].replace(":", "_").replace("/", "-")
            + ".pdf"
        )
        if os.path.exists(filename):
            continue
        response = requests.get(p["download"], headers=headers)
        with open(filename, "wb") as f:
            f.write(response.content)

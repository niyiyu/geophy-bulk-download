import pandas as pd
from pybtex.database.input import bibtex

parser = bibtex.Parser()
f = open("./tsr.bibtex", "r")
bibtexFile= parser.parse_string(f.read())   

pubs = []

for ie, en in bibtexFile.entries.items():
    pubs.append({"identifier": ie,
                 "download": en.fields["eprint"],
                 "doi": en.fields["url"],
                #  "abstract": en.fields["abstract"],
                 "title": en.fields["title"]})
pd.DataFrame.from_records(pubs).to_csv("tsr.csv", index=False)
import pandas as pd

from tqdm import tqdm

df = pd.read_csv("./Publication_list - GJI.csv")

selected = []
key_words = ["catalog", "seismicity", "picking", "association"]

for i, r in tqdm(df.iterrows()):
    try:
        if any([k in r["Article Title"].lower() for k in key_words]):
            selected.append(r)
    except:
        pass

pd.DataFrame(selected).to_csv("../metadata/selected.csv")
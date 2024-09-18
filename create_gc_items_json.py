#https://raw.githubusercontent.com/xivapi/ffxiv-datamining/master/csv/Item.csv
#https://github.com/xivapi/ffxiv-datamining/blob/master/csv/GCScripShopItem.csv

import pandas as pd

item_df = pd.read_csv("Item.csv",skiprows=[0,2])
gc_item_df = pd.read_csv("GCScripShopItem.csv", skiprows=[0,2,3])

def maplink(df1,df2,keys):
    for key in keys:
        df1[key] = gcs["Item"].map(df.set_index("#")[key])

maplink(gc_item_df,item_df, ["Name", 'StackSize', 'IsUnique', 'IsUntradable'])

gc_item_df=gc_item_df.rename(columns={gc_item_df.columns[2]:"RequiredGCRank","Cost{GCSeals}":"GCSealsCost"})

gc_item_df["IsTradeable"] = gc_item_df["IsUntradable"] ^ True 
gc_item_df = gc_item_df[["Item","Name","RequiredGCRank","GCSealsCost","StackSize","IsUnique","IsTradeable"]].dropna()
gc_item_df = gc_item_df.drop_duplicates()
gc_item_df=gc_item_df.set_index("Item")
gc_item_df.to_csv("gc_items.csv")
gc_item_df.to_json("gc_items.json", orient='index')
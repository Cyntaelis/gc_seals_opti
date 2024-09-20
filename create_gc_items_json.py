#https://raw.githubusercontent.com/xivapi/ffxiv-datamining/master/csv/Item.csv
#https://github.com/xivapi/ffxiv-datamining/blob/master/csv/GCScripShopItem.csv

import pandas as pd

import pandas as pd

item_df = pd.read_csv("Item.csv",skiprows=[0,2])
gc_item_df = pd.read_csv("GCScripShopItem.csv", skiprows=[0,2,3])
gc_cat_df = pd.read_csv("GCScripShopCategory.csv", skiprows=[0,2])
gc_item_df["#"] = gc_item_df["#"].astype(int)
def maplink(df1,df2,keys,key1="Item"):
    for key in keys:
        df1[key] = df1[key1].map(df2.set_index("#")[key])

maplink(gc_item_df, item_df, ["Name", 'StackSize', 'IsUnique', 'IsUntradable'])
print(gc_item_df.columns)
maplink(gc_item_df,gc_cat_df, ["GrandCompany"],key1="#")
#TODO: its the dupe entries for each GC thats causing problems
# gc_item_df["GrandCompany"] = gc_item_df["#"].astype(int).map(gc_cat_df.set_index("#")["GrandCompany"])
# print(gc_item_df.columns)
gc_item_df=gc_item_df.rename(columns={gc_item_df.columns[2]:"RequiredGCRank","Cost{GCSeals}":"GCSealsCost"})
print(len(gc_item_df))
print(gc_item_df["GrandCompany"].value_counts())
gc_item_df.loc[gc_item_df["Item"].duplicated(keep = False),"GrandCompany"] = 0
print(len(gc_item_df))
print(gc_item_df["GrandCompany"].value_counts())
gc_item_df["IsTradeable"] = gc_item_df["IsUntradable"] ^ True 

# print(gc_item_df["Item"].value_counts())
gc_item_df = gc_item_df.drop_duplicates(subset=["Name","Item"])
print(len(gc_item_df))
gc_item_df = gc_item_df[["Item","Name","RequiredGCRank","GCSealsCost","StackSize","IsUnique","IsTradeable","GrandCompany"]]
gc_item_df = gc_item_df.dropna()

print(gc_item_df["Item"].value_counts())
gc_item_df = gc_item_df.set_index("Item")
gc_item_df.to_csv("gc_items.csv")
print(gc_item_df.columns)
gc_item_df.to_json("gc_items.json", orient='index')
print("Done")
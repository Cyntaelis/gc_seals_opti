import streamlit as st
from univ_tools import univ_client
from processing import process_listings, process_sales
# from univ_tools import univ_client
from xivjson import gc_ranks, servers_lookup, reverse_servers_lookup, gc_items

st.set_page_config(
    layout="wide", 
    page_title="GC Seals Optimizer",
    menu_items = {}
    )

hide_streamlit_style = """
<style>
.css-hi6a2p {padding-top: 0rem;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@st.cache_resource
def get_univ_client():
    return univ_client()
univ_client = get_univ_client()

@st.cache_resource
def cache_tradeables():
    import pandas as pd
    # df = pd.read_json(gc_items)
    # return df[df["IsTradeable"]]
    df = pd.DataFrame.from_dict(gc_items, orient='index')
    return df[df["IsTradeable"]]
tradeable_gc_items = cache_tradeables()
# @st.cache_resource
# def cache_options_list():
#     return make_options_list()
# options_list = cache_options_list() 
print("Page Load")
# lcol, rcol = st.columns([2,2])
submit = None

with st.form("key"):
    home = st.selectbox("Home Server", ["North-America"]+list(reverse_servers_lookup.keys()), 0)
    gc = st.selectbox("Grand Company", ["Maelstrom","Twin Adders"," Immortal Flames"], None)
    rank = st.selectbox("GC Rank", [x for x in range(11)][::-1], 0, format_func=lambda x:gc_ranks[x])
    sales_window = st.number_input("Sales History WIndow, in days", 0, 14, value=7, step=1)
    listings_window = st.number_input("Listings History Window, in days", 0, 14, value=7, step=1)
    # num_seals = st.number_input("Number of seals", 0, 40000, value=40000, step=1)
    submit = st.form_submit_button("Calculate", "key")


# #TODO: default prio: what will make the most gil in the shortest amount of time
# stuff = ["Item", "Seals Cost", "Stack size", "Current Estimated local cost", "Lowest Price on DC" #per_item_constants
#          #windows: last 24 hours, default window, default window assuming uniques, next 24 but a week ago
#         "Avg price per", "Listings sold", "Items Sold", "Unique Buyers", "Updated Listings", "num_retainers" #window data
# ]

out=None
if submit is not None and submit:
    params = {
            'listings': 10,
            'entries': 30,
            'statsWithin': 1,
            }
    items = "".join([x+", " for x in tradeable_gc_items.index.to_list()])[:-2]

    out = univ_client.raw_cached_query(items, region=home, params=params)
    if out is None:
        st.write("exec failed")
    else:
        tradeable_gc_items["Item"] = tradeable_gc_items.index

        #TODO move this to a better spot
        #ytf are ventures marked tradeable? 
        tradeable_gc_items=tradeable_gc_items[tradeable_gc_items["Item"]!="21072"]
        tradeable_gc_items=tradeable_gc_items[tradeable_gc_items["RequiredGCRank"]<=rank+1]

        disp_df = tradeable_gc_items[["Item","Name",#"Required Rank",
                                    "GCSealsCost", "StackSize",#"IsUnique" #theyre all unique
                                    ]]

        disp_df = disp_df.rename(columns = {"Item":"Item ID",
                                "GCSealsCost":"GC Seals Cost",
                                "StackSize":"Stack Size",
                                # "IsUnique":"Unique"
                                })

        disp_df["Avg Gil per Seal"] = disp_df["GC Seals Cost"]

        disp_df[["Avg Sale Price","Listings Sold", "Items Sold", "Unique Buyers"]] = \
            [process_sales(out["items"][x]["recentHistory"], window=sales_window) 
                           if (x in out["items"]) else [None,None,None,None]
                           for x in disp_df["Item ID"].to_list()
                           ]

        disp_df[["Current Price", "Recent Listings", "Active Retainers"]] = \
            [process_listings(out["items"][x]["listings"], window=listings_window) 
                    if x in out["items"] else [None,None,None]
                    for x in disp_df["Item ID"].to_list()
                    ]
            
        disp_df["Avg Gil per Seal"] = disp_df["Avg Sale Price"] / disp_df["GC Seals Cost"]

        disp_df["Total Gil Moved"] = disp_df["Avg Sale Price"] * disp_df["Items Sold"]

        disp_df["Gil Moved per Day"] = disp_df["Avg Sale Price"] * disp_df["Items Sold"] / sales_window
        # print(l,out)
        # st.write(out.keys())
        # user_agent = "GCSealsOptimizer/0.1"
        disp_df = disp_df.sort_values(by="Gil Moved per Day", ascending=False, na_position="last")
        st.dataframe(disp_df)
        # if submit is not None:
        #     st.dataframe(tradeable_gc_items)
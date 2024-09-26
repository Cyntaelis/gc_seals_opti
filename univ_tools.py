import requests
import asyncio
import xivjson
import time
from xivjson import *

region_lookup = servers_lookup

REGION_NA = "North-America"
URL = "https://universalis.app/api/v2/"
LIMIT_PER_WORLD = 2
LIMIT_PER_DC = 3
LISTINGS_PER_ITEM = 5
keylist = [
           'listingID',
           'lastReviewTime', 
           'pricePerUnit', 
           'quantity', 
           'worldName', 
           'worldID', 
           'hq',
           'total',
           'retainerName']

class univ_client:

    def __init__(self):
        self.cache = {}
        self.recent = 0
        self.last_reset = time.time()
    #     self.queue = asyncio.Queue()
    #     self.mutex = False

    # async def enqueue(self, query):
    #     self.queue.put(query)
    #     self.queue_consumer()

    # async def queue_consumer(self):
    #     if self.mutex:
    #         return
    #     self.mutex = True
    #     try:
    #         while not self.queue.empty():
    #             pass
                
    #     except Exception as e:
    #         self.mutex = False
    #         raise e
        
    def raw_price_query(self, item_id, region = REGION_NA, params=None):
        region = region
        # def_params = {
        # 'listings': 100,
        # 'entries': 0,
        # 'statsWithin': 99999,
        # # 'entriesWithin': 77777
        # }
        # params = def_params if params is None else params
        self.recent += 1
        if self.recent > 15 and (time.time()-self.last_reset) <= 1:
            time.sleep(3)
            self.recent = 0
            self.last_reset = time.time()
            
        print("query sent", item_id, params)    
        response = requests.get(URL+f"{region}/{item_id}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            #maybe reenque?



    def _raw_cached_query(self, item_id, region, params=None):
        print(item_id)
        if False and (item_id,region) in self.cache :
            print("found in cache")
            results,timestamp = self.cache[(item_id,region)]
            if results is not None and time.time()-timestamp <= 1*60:
                return results

        # print("query sent ",item_id)
        results = self.raw_price_query(item_id, region, params)
        if results is not None:
            self.cache[(item_id,region)] = [results, time.time()] 
        print(results.keys())
        if "unresolvedItems" in results:
            print(results["unresolvedItems"])
        return results

    def raw_cached_query(self, item_id, region, params=None):
        splits = 2
        split_size=len(item_id)//splits
        retval = {}
        try:
            for x in range(splits):
                split_read = self._raw_cached_query(item_id[split_size*x:split_size*(x+1)], region, params)
                if split_read is not None:
                    retval = retval|split_read
                else:
                    return None
                time.sleep(3)
        except Exception as e:
            print(e)
            return None
        return retval

    def price_query(self, item_id, region = REGION_NA, params=None, **filter_args):
        
        region = REGION_NA
        if "region" in filter_args:
            region = filter_args["region"]
        if item_id in self.cache:
            results = self.cache[item_id]
        else:
            print("query sent ",item_id)
            results = self.raw_price_query(item_id, region, params)
            if results is not None:
                self.cache[item_id] = results    
        filtered_results = self._filter_price_query(results, **filter_args)
        return self._reduce_results(filtered_results)

    @staticmethod
    def _filter_price_query(results, **filter_args): 
        # print(results)
        listings = sorted(results["listings"], key=(lambda x:int(x["pricePerUnit"])) ) 
        retval = []
        worlds_seen = {}
        datacenters_seen = {}
        for listing in listings:

            if listing["onMannequin"]:
                continue
            
            skip=False
            for key, (cond, value) in filter_args.items():
                if key in listing:
                    # print(key,cond,value, listing[key], cond(listing[key], value))
                    if not cond(listing[key],value):
                        skip=True
                        break
            if skip:
                continue

            if listing["worldID"] in worlds_seen:
                worlds_seen["worldID"] += 1
                if worlds_seen["worldID"] > LIMIT_PER_WORLD:
                    continue
            else:
                worlds_seen["worldID"] = 1

            
            dc_id = reverse_servers_lookup[listing["worldName"]]
            if dc_id in datacenters_seen:
                datacenters_seen[dc_id] += 1
                if datacenters_seen[dc_id] > LIMIT_PER_DC:
                    continue
            else:
                datacenters_seen[dc_id] = 1

            if len(retval) <= LISTINGS_PER_ITEM:
                retval.append(listing)
            else:
                break
        return retval

    @staticmethod
    def _reduce_results(results):
        return [{k:x[k] for k in keylist} for x in results]

class filter:
    def __init__(self):
        self.conditions = {"hq":("accept", True)} #{property/accessor:(operator,value)}
        self.filter_functions = []

    def apply(self, iterable):
        return self.__call__(iterable)
    
    def __call__(self, iterable):
        
        pass

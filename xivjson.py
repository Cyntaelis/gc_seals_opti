import json

def load_resources():
    with open('items.json', 'r') as file:
        item_lookup = json.load(file)

    reverse_item_lookup = {item_lookup[x]["en"]:x for x in item_lookup.keys()}

    with open('recipes-ingredient-lookup.json', 'r') as file:
        recipe_lookup = json.load(file)

    reverse_recipe_lookup = {recipe_lookup["recipes"][x]["itemId"]:
                         recipe_lookup["recipes"][x]
                         for x in recipe_lookup["recipes"].keys()}
    
    return item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup

item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup = load_resources()

def server_mappings():
    with open('datacenters.json', 'r') as file:
        servers_lookup = json.load(file)

    reverse_servers_lookup = {x:a for a,b in servers_lookup.items() for x in b}
    return servers_lookup, reverse_servers_lookup

servers_lookup, reverse_servers_lookup = server_mappings()

def gc_ranks():
    with open('ranks.json', 'r') as file:
        gc_ranks = json.load(file)
    return gc_ranks["ranks"]#[::-1]

gc_ranks = gc_ranks()

def gc_items():
    with open('gc_items.json', 'r') as file:
        gc_items = json.load(file)
    return gc_items

gc_items = gc_items()

# def unique_gc_items():
#     import pandas as pd
#     df = pd.read_csv()
#     with open('GCScripShopItem.csv', 'r') as file:
#         gc_items = json.load(file)

# unique_gc_items = unique_gc_items()

def recipe_dict(itemID):
    retval = {"id":itemID, "text":item_lookup[str(itemID)]["en"]}
    if not int(itemID) in reverse_recipe_lookup:
        return None
    recipe = reverse_recipe_lookup [int(itemID)]
    if "yields" in recipe:
        retval["yields"] = recipe["yields"]
    ingredients = []
    for x in recipe["ingredients"]:
        ingredient = {}
        ingredient["id"] = x["id"]
        ingredient["text"] = item_lookup[str(x["id"])]["en"]
        ingredient["amount"] = x["amount"]
        recurs = recipe_dict(x["id"])
        if recurs is not None:
            if "yields" in recurs:
                ingredient["yields"] = recurs["yields"]
            ingredient["ingredients"] = recurs["ingredients"]
        ingredients.append(ingredient)
    retval["ingredients"] = ingredients
    return retval
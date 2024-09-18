import time

def process_listings(listings, window=7):
    window *= 24*60*60
    lowest_price = None
    listings_updated = 0
    unique_retainers = {}
    t = int(time.time())
    # print(listings)
    for x in listings:
        # if item is None:
        #     continue
        # for x in item:
        if x is None:
            continue
        if x["onMannequin"]:
            continue
        if t-x["lastReviewTime"] > window:
            continue
        if lowest_price is None or x["pricePerUnit"] < lowest_price:
            lowest_price = x["pricePerUnit"]
        listings_updated += 1
        unique_retainers[x["retainerID"]]=True

    return lowest_price, listings_updated, len(unique_retainers.keys())

def process_sales(sales, window=7):
    window *= 24*60*60
    t = time.time()
    # print(sales)
    listings_sold = 0
    items_sold = 0
    avg_price = [] #per listing, not per item in stack
    unique_buyers = {}
    for x in sales:
        # if item is None:
        #     continue
        # for x in item:

        if x["onMannequin"]:
            continue
        if int(t)-x["timestamp"] > window:
            continue
        unique_buyers[x['buyerName']] = True
        avg_price.append(int(x['pricePerUnit']))

        items_sold += int(x["quantity"])
        listings_sold += 1

    avg = sum(avg_price)/len(avg_price) if len(avg_price)!= 0 else None

    return avg, listings_sold, items_sold,  len(unique_buyers.keys())
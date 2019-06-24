# import required libraries
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re

# specify the url
cbre_toronto_url= "https://www.commerciallistings.cbre.ca/en-CA/listings/office/results?Common.HomeSite=ca-comm&CurrencyCode=CAD&Interval=Monthly&RadiusType=Kilometers&Site=ca-comm&Unit=sqft&aspects=isLetting&isParent=true&lat=43.653226&location=Toronto%2C+ON%2C+Canada&lon=-79.38318429999998&placeId=ChIJpTvG15DL1IkRd8S0KlBVNTI&polygons=%5B%5B%2243.8554579%2C-79.11689710000002%22%2C%2243.5810245%2C-79.11689710000002%22%2C%2243.5810245%2C-79.63921900000003%22%2C%2243.8554579%2C-79.63921900000003%22%5D%5D&radius=0&searchMode=bounding&sort=asc%28_distance%29&usageType=Office"
building_urls = []
unit_addresses = []
unit_urls = {}
unit_details = {}
driver = webdriver.Chrome('C:/Users/koush/Desktop/chromedriver')

""" 
********************************************
Top Level Function
********************************************
"""
def get_toronto_office_building_listings():
    """ The below section gets URLs for all buildings"""
    driver.get(cbre_toronto_url)
    print("going to sleep for 20s")
    time.sleep(20)
    print("my 20s wait is over")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_results = soup.find_all('a')
    for elem in search_results:
        try:
            if "en-CA/listings/office/details/CA-Plus" in elem["href"]:
                building_urls.append(elem["href"])
        except:
            #Sometimes 'a' tags don't have 'href' inside them
            pass
    return building_urls


""" 
********************************************
Helper Functions
********************************************
"""
def get_unit_address(url):
    my_string = url.split('CA-Plus-')[1]
    result = re.search('/(.*)', my_string).group(1).split("?")[0]
    return result

# get info about each unit
def get_sqft(soup, prefixes):
    headers = soup.find_all("div", {"class": "cbre_subh2 header-size"})
    sq_ft_size = headers[0].contents[0].contents[0].contents  # this is a list
    sq_ft_size = [x for x in sq_ft_size if not str(x).startswith(prefixes)]
    result = ''.join(sq_ft_size)
    return result

def get_price(soup, prefixes):
    headers = soup.find_all("div", {"class": "cbre_h1 header-price"})
    price = headers[0].contents[0].contents  # this is a list
    try:
        price = price[0].contents
    except:
        price = price
    price = [x for x in price if not str(x).startswith(prefixes)]
    result = ''.join(price)
    return result

def get_unit_number(soup, prefixes):
    main_header = soup.find_all("div", {"class": "header-title"})
    unit_number = main_header[0].contents[0].contents  # this is a list
    try:
        unit_number = unit_number[0].contents[1]
    except:
        unit_number = unit_number
    try:
        result = unit_number.split(',')[0]
    except:
        result = unit_number.split(',')[0][0]
    return result


""" 
****************************************************
Two Major Functions using above Helper Functions
****************************************************
"""
def get_unit_urls(building_urls):
    count = 1
    for building in building_urls:
        building = 'https://www.commerciallistings.cbre.ca' + building
        driver.get(building)
        title = get_unit_address(building)
        if title not in unit_urls.keys():
            unit_urls[count] = {}
            unit_urls[count][title] = []
            unit_details[count] = {}

        time.sleep(8)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        units = soup.find_all('a', {'class':'card_content'})
        for unit in units:
            if 'mississauga' not in str(unit["href"]).lower() \
                    and 'vaughan' not in str(unit["href"]).lower()\
                    and 'thornhill' not in str(unit["href"].lower()):
                unit_urls[count][title].append(unit["href"])
        count += 1
    return unit_urls, unit_details

"""!!!CORRECT THIS DURING PRODUCTION!!!"""
def get_individual_unit_details(final_unit_urls, base_unit_details_dict):
    count = 1
    unit_count = 1
    for each_unit in final_unit_urls:
        unit_count = 1
        for key,values in final_unit_urls[each_unit].items():
            base_unit_details_dict[count] = {}
            if key not in base_unit_details_dict[count]:
                base_unit_details_dict[count][key] = {}
            for value in values:
                value = 'https://www.commerciallistings.cbre.ca' + value
                driver.get(value)
                time.sleep(8)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                prefixes = ('react', ' react', ' /react')
                base_unit_details_dict[count][key][unit_count] = {}
                base_unit_details_dict[count][key][unit_count]['Unit Number'] = get_unit_number(soup, prefixes)
                base_unit_details_dict[count][key][unit_count]['Unit Size'] = get_sqft(soup, prefixes)
                base_unit_details_dict[count][key][unit_count]['Unit Price'] = get_price(soup, prefixes)
                unit_count += 1
        count +=1
    # print(base_unit_details_dict)
    return base_unit_details_dict


"""!!!UNCOMMENT THIS DURING PRODUCTION!!!"""
building_urls = get_toronto_office_building_listings()

"""!!!UNCOMMENT THIS DURING PRODUCTION!!!"""
# final_unit_urls is a dictionary
building_urls = ['/en-CA/listings/office/details/CA-Plus-915/477-mount-pleasant-road-toronto-m4s-2m4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-915/477-mount-pleasant-road-toronto-m4s-2m4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-613/yonge-eglinton-centre-2300-yonge-street-toronto-m4p-1e4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-613/yonge-eglinton-centre-2300-yonge-street-toronto-m4p-1e4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-563/yonge-eglinton-centre-20-eglinton-avenue-w-toronto-m4r-1k8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-563/yonge-eglinton-centre-20-eglinton-avenue-w-toronto-m4r-1k8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-769/3080-yonge-street-toronto-m4n-3n1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-769/3080-yonge-street-toronto-m4n-3n1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-655/labourers-pension-fund-building-1835-yonge-street-toronto-m4s-1x8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-655/labourers-pension-fund-building-1835-yonge-street-toronto-m4s-1x8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1326/morneau-sobeco-ii-895b-don-mills-road-north-york-m3c-1w3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1326/morneau-sobeco-ii-895b-don-mills-road-north-york-m3c-1w3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1134/don-mills-office-centre-1090-don-mills-road-north-york-m3c-3r6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1134/don-mills-office-centre-1090-don-mills-road-north-york-m3c-3r6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-609/21-st-clair-avenue-e-toronto-m4t-1l9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-609/21-st-clair-avenue-e-toronto-m4t-1l9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-611/1-st-clair-avenue-e-toronto-m4t-2v7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-611/1-st-clair-avenue-e-toronto-m4t-2v7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1140/yonge-corporate-centre-i-4100-yonge-street-north-york-m2p-2b5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1140/yonge-corporate-centre-i-4100-yonge-street-north-york-m2p-2b5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1033/alpha-corporate-centre-1262-don-mills-road-north-york-m3b-2w6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1033/alpha-corporate-centre-1262-don-mills-road-north-york-m3b-2w6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1085/bond-business-centre-1370-don-mills-road-north-york-m3b-3n7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1085/bond-business-centre-1370-don-mills-road-north-york-m3b-3n7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1129/concorde-corporate-centre-ii-3-concorde-gate-north-york-m3c-3n7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1129/concorde-corporate-centre-ii-3-concorde-gate-north-york-m3c-3n7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1128/concorde-corporate-centre-i-1-concorde-gate-north-york-m3c-3n6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1128/concorde-corporate-centre-i-1-concorde-gate-north-york-m3c-3n6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1130/celestica-12-concorde-place-north-york-m3c-3r8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1130/celestica-12-concorde-place-north-york-m3c-3r8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1047/cbre-2005-sheppard-avenue-e-north-york-m2j-5b4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1047/cbre-2005-sheppard-avenue-e-north-york-m2j-5b4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1049/gm-financial-2001-sheppard-avenue-e-north-york-m2j-4z8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1049/gm-financial-2001-sheppard-avenue-e-north-york-m2j-4z8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-882/163-queen-street-e-toronto-m5a-1s1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-882/163-queen-street-e-toronto-m5a-1s1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1196/atria-iii-2225-sheppard-avenue-e-north-york-m2j-5c2?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1196/atria-iii-2225-sheppard-avenue-e-north-york-m2j-5c2?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1195/atria-ii-2235-sheppard-avenue-e-north-york-m2j-5b5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1195/atria-ii-2235-sheppard-avenue-e-north-york-m2j-5b5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1194/atria-north-i-2255-sheppard-avenue-e-north-york-m2j-4y1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1194/atria-north-i-2255-sheppard-avenue-e-north-york-m2j-4y1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1399/245-fairview-mall-drive-north-york-m2j-4t1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1399/245-fairview-mall-drive-north-york-m2j-4t1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-661/30-st-patrick-street-toronto-m5t-3a3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-661/30-st-patrick-street-toronto-m5t-3a3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-626/10-king-street-e-toronto-m5c-1c3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-626/10-king-street-e-toronto-m5c-1c3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-210461/65-king-street-east-toronto-m5c-1g3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-210461/65-king-street-east-toronto-m5c-1g3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-875/8-king-street-e-toronto-m5c-1b5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-875/8-king-street-e-toronto-m5c-1b5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1932/the-robertson-building-215-spadina-avenue-toronto-m5t-2c7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1932/the-robertson-building-215-spadina-avenue-toronto-m5t-2c7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-622/scotia-plaza-40-king-street-w-toronto-m5h-3y2?view=isLetting', '/en-CA/listings/office/details/CA-Plus-622/scotia-plaza-40-king-street-w-toronto-m5h-3y2?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1151/westford-centre-2131-lawrence-avenue-e-scarborough-m1r-5g4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1151/westford-centre-2131-lawrence-avenue-e-scarborough-m1r-5g4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1183/5775-yonge-street-north-york-m2m-4j1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1183/5775-yonge-street-north-york-m2m-4j1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-9215/20-de-boers-drive-north-york-m3j-3e5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-9215/20-de-boers-drive-north-york-m3j-3e5?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1201/2202-eglinton-avenue-e-scarborough-m1l-2n3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1201/2202-eglinton-avenue-e-scarborough-m1l-2n3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-221658/2200-eglinton-avenue-e-toronto-m1l-2n3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-221658/2200-eglinton-avenue-e-toronto-m1l-2n3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-212175/1266-queen-street-w-toronto-m6k-1l3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-212175/1266-queen-street-w-toronto-m6k-1l3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1035/105-gordon-baker-road-north-york-m2h-3p8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1035/105-gordon-baker-road-north-york-m2h-3p8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-2074/511-mcnicoll-avenue-north-york-m2h-2c9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-2074/511-mcnicoll-avenue-north-york-m2h-2c9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1152/2075-kennedy-road-scarborough-m1t-3v3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1152/2075-kennedy-road-scarborough-m1t-3v3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-10321/2330-kennedy-road-toronto-m1t-3h1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-10321/2330-kennedy-road-toronto-m1t-3h1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1287/1-sparks-avenue-north-york-m2h-2w1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1287/1-sparks-avenue-north-york-m2h-2w1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-245187/160-springhurst-avenue-toronto-m6k-1c2?view=isLetting', '/en-CA/listings/office/details/CA-Plus-245187/160-springhurst-avenue-toronto-m6k-1c2?view=isLetting', '/en-CA/listings/office/details/CA-Plus-11168/12-morgan-avenue-markham-l3t-2b3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-11168/12-morgan-avenue-markham-l3t-2b3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1138/3650-victoria-park-avenue-north-york-m2h-3p7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1138/3650-victoria-park-avenue-north-york-m2h-3p7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-206611/4651-sheppard-avenue-e-toronto-m1s-3v4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-206611/4651-sheppard-avenue-e-toronto-m1s-3v4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-11110/150-jardin-drive-vaughan-l4k-3p9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-11110/150-jardin-drive-vaughan-l4k-3p9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-236272/270-the-kingsway-toronto-m9a-3t7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-236272/270-the-kingsway-toronto-m9a-3t7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-251257/7625-keele-street-vaughan-l4k-1y4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-251257/7625-keele-street-vaughan-l4k-1y4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1359/south-creek-corporate-centre-125-commerce-valley-drive-w-thornhill-l3t-7w4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1359/south-creek-corporate-centre-125-commerce-valley-drive-w-thornhill-l3t-7w4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-5770/150-commerce-valley-drive-w-thornhill-l3t-7z3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-5770/150-commerce-valley-drive-w-thornhill-l3t-7z3?view=isLetting', '/en-CA/listings/office/details/CA-Plus-188873/150-rivermede-road-vaughan-l4k-3m8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-188873/150-rivermede-road-vaughan-l4k-3m8?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1122/600-alden-road-markham-l3r-0e7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1122/600-alden-road-markham-l3r-0e7?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1761/east-tower-bloor-islington-centre-3250-bloor-street-w-etobicoke-m8x-2x9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-1761/east-tower-bloor-islington-centre-3250-bloor-street-w-etobicoke-m8x-2x9?view=isLetting', '/en-CA/listings/office/details/CA-Plus-6628/5535-eglinton-avenue-w-mississauga-m9w-5n1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-6628/5535-eglinton-avenue-w-mississauga-m9w-5n1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-213226/2305-stanfield-road-mississauga-l4y-1r6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-213226/2305-stanfield-road-mississauga-l4y-1r6?view=isLetting', '/en-CA/listings/office/details/CA-Plus-239810/1000-middlegate-mississauga-l4y-1m4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-239810/1000-middlegate-mississauga-l4y-1m4?view=isLetting', '/en-CA/listings/office/details/CA-Plus-8434/680-silver-creek-boulevard-mississauga-l5a-3z1?view=isLetting', '/en-CA/listings/office/details/CA-Plus-8434/680-silver-creek-boulevard-mississauga-l5a-3z1?view=isLetting']
building_urls = list(set(building_urls))
final_unit_urls, base_unit_details_dict = get_unit_urls(building_urls[0:10])

"""!!!UNCOMMENT THIS DURING PRODUCTION!!!"""
# final_unit_urls is a dictionary
# delete this line
final_dict = get_individual_unit_details(final_unit_urls, base_unit_details_dict)
driver.close()

addresses =[]
df = pd.DataFrame()
for key, minor_values in final_dict.items():
    for k, v in minor_values.items():
        addresses.append(k)
        if df.empty:
            df = pd.DataFrame(v).T
            df['Address'] = k
        else:
            temp_df = pd.DataFrame(v).T
            temp_df['Address'] = k
            df = pd.concat([df, temp_df], sort=True)

df['Address'] = df['Address'].replace('-', ' ', regex=True)
df['Address'] = df['Address'].str.title()
df1 = df[~df['Address'].isin(["ississauga", "aughan", "hornhill"])]
df1.to_csv('C:/Users/koush/Desktop/cbre_toronto_office_listings.csv')

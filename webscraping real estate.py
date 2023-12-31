from bs4 import BeautifulSoup
# import requests 
import pandas as pd 
#import urllib.parse
import json 
import time

from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options



driver = webdriver.Chrome()

website = "https://www.trulia.com/IL/Naperville/" #
website2 = "https://www.trulia.com/IL/Naperville_p/" #
website3 = "https://www.trulia.com/IL/Naperville/2_p/" 
web = "https://www.trulia.com/for_sale/Hinsdale,IL/SINGLE-FAMILY_HOME_type/11_zm/"
website4 = "https://www.trulia.com/for_sale/Evanston,IL/SINGLE-FAMILY_HOME_type/12_zm/"
website5 = "https://www.trulia.com/for_sale/Northbrook,IL/APARTMENT,CONDO,COOP,SINGLE-FAMILY_HOME,TOWNHOUSE_type/price;d_sort/11_zm/"
website6 = "https://www.trulia.com/for_sale/Schaumburg,IL/1p_beds/12_zm/"
website7 = "https://www.trulia.com/for_sale/Palatine,IL/1p_beds/1p_sqft/SINGLE-FAMILY_HOME_type/12_zm/"
websiteTest = "https://www.trulia.com/for_sale/Vernon_Hills,IL/1p_beds/1p_sqft/SINGLE-FAMILY_HOME_type/10_zm/"

demoweb = "https://www.trulia.com/IA/Iowa_City/"

# Use Selenium to navigate the webpage
driver.get("https://www.trulia.com/IA/Cedar_Rapids/")

# Wait for the page to load 
time.sleep(25)

# Extract the page source after it's fully loaded
page_source = driver.page_source

driver.quit()

# # # !!!
soup = BeautifulSoup(page_source, 'html.parser')



#############
# headers = ''
# response = requests.get(website, headers=headers)
# print(response)
#soup = BeautifulSoup(response.text, 'html.parser')
#############


result = soup.find_all('li', {'class': "Grid__CellBox-sc-a8dff4e9-0 sc-84372ace-0 kloaJl kTTMdB"})
len(result)

result_update = [i for i in result if i.has_attr('data-testid')]
len(result_update)

address = []
MLS_ID = []
sqft =[]
style = [] 
beds = []
bathrooms =[]
price = []
sqft = []
lot = []

data_list = []
    
links = soup.find_all('a',{})
all_links = []

####

for i,l in enumerate(links):
    if links[i]['href'][0:6] in ('/home/','/build') and "https://www.trulia.com" +  links[i]['href'] not in all_links:
        all_links.append("https://www.trulia.com" + links[i]['href'])

stories  = []
year_built = []
history = []

#### GET STORIES AND YEAR BUILT
time.sleep(25)
import random ### STOP AT 39
for url in all_links[0:40]: ## 
    #home = 'https://www.trulia.com/home/2012-springside-dr-naperville-il-60565-4551229'
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(random.uniform(20, 25))
    src = driver.page_source
    driver.quit()
    soup2 = BeautifulSoup(src, 'html.parser')
    details = soup2.find_all('span', {'class': "sc-9be18632-0 dcisBF"})
    
    year = None
    story = None
    for d in details:
        if d.get_text()[0:6] == 'Year B':
            year = (d.get_text()).split()[-1]
            history.append(url + " " + year)
        if 'Stories:' in d.get_text().split():
            story = (d.get_text()).split()[-1]
            history.append(url + " " + story)

    if year is None:
        year_built.append(0)
    else:
        year_built.append(year)
        
    if story is None:  
        stories.append(0)
    else:
        stories.append(story)

    #print("done")
    #time.sleep(random.uniform(40, 50))

####
################# update lists ##############################3

for result in result_update:
        # try:
        #     address.append(result.find('div', {'data-testid':'property-address'}).get_text())
        # except:
        #     address.append('n/a')
            
        try:
            beds.append(result.find('div', {'data-testid':'property-beds'}).get_text())
        except:
            beds.append('n/a')
    
        try:
            bathrooms.append(result.find('div', {'data-testid':'property-baths'}).get_text())
        except:
            bathrooms.append('n/a')    
        
        try:
            price.append(result.find('div', {'data-testid':'property-price'}).get_text())
        except:
            price.append('n/a')      
        try:
            sqft.append(result.find('div', {'data-testid':'property-floorSpace'}).get_text())
        except:
            sqft.append('n/a')

price = ["".join(p.strip('+$').split(',')) for p in price]

temp = []
for s in sqft:
    try:
        temp.append(s[:s.index(" ")].replace(",",""))
    except:
        temp.append('0')
sqft = temp


### JSON

for i, item in enumerate(result_update):
    script_tag = item.find('script', {'data-testid': 'srp-seo-breadcrumbs-list'})
    if script_tag:
        # Extract the JSON content from the script tag
        json_data = json.loads(script_tag.contents[0])

        # Extract address details
        address_info = json_data.get('address', {})
        street_address = address_info.get('streetAddress', 'N/A')
        address_locality = address_info.get('addressLocality', 'N/A')
        address_region = address_info.get('addressRegion', 'N/A')
        postal_code = address_info.get('postalCode', 'N/A')

        proptype = json_data.get('@type', 'N/A')
        
        data = {
            'address': street_address,
            'city': address_locality,
            'State': address_region,
            'zip': postal_code,
            'type': proptype,
            'bedrooms': beds[i].strip('bd'),
            'bathrooms': bathrooms[i].strip('ba'),
            'price': "".join(price[i].strip('+$').split(',')),
            'sqft': sqft[i],
            'year built': year_built[i],
            'stories': stories[i],
            'link':all_links[i]
        }

        data_list.append(data)
    else:
        print("Script tag not found for item.")
        
real_estate = pd.DataFrame(data_list)

real_estate.to_csv("train_properties.csv", index=False)


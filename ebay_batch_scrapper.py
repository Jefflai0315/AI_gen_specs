from unittest import result
from attr import attr
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import math
import os

# open new soup with a new url
def get_page(url):
    response =  requests.get(url)
    if not response.ok:
        print('server responded: ', response.status_code)
    else:
        data=response.text
        soup=BeautifulSoup(data,"html.parser")
        return soup

# use in the individual product page to find details
def get_detail_data(soup):
    try:
        title = soup.find('h1', attrs = {'class':"x-item-title__mainTitle"}).find('span').text
    except:
        title =' '

    try:
        price = soup.find('div', attrs = {'class':"mainPrice"}).find('span')
        price = price.get('content')
    except:
        price =' '

    try: 
        sold = soup.find('div', attrs = {'id':"why2buy"}).find('span').text #.split(' ')[0]
    except:
        sold =' '

    try: 
        review = soup.find('div', attrs = {'class':"overlay-top"}).find('a') #.split(' ')[0]
        reviewURL = review.get("href") + '&pgn='
        review_num = int(re.search(r'\d+', review.text).group())
        page = int(math.ceil(review_num/10))
        print(reviewURL,page)
    
        reviews = get_review(reviewURL, page)
        
    except:
        reviews =' '

    try:
        descs = soup.find('div', attrs ={'data-testid':"ux-layout-section__item",'class':"ux-layout-section__item ux-layout-section__item--table-view"}).find_all('span', attrs={'class':"ux-textspans"})
    except:
        descs = [' ']
    finally:
        try:
            specs = []
            for i in range(len(descs)):
                descs = [i for i in descs if i.contents[1] !='Read more'] #remove read more expandable tag
                print(descs)
            for i in range(len(descs)-1):
                if i % 2 ==0: 
                    specs.append([descs[i].contents[1],descs[i+1].contents[1]])
            if specs[0][1][:10] == specs[1][0][:10]:
                specs[0][1] = specs[1][0]
                del specs[1]
            
            
            specs_dict = {}
            for i in specs:
                specs_dict[i[0][:-1]] = i[1]
            print(specs_dict)
        except:
            specs_dict ={}

   
    return [title, price,sold,reviews] , specs_dict

# to see the specs of an individual product
def get_single_df(specs):
    df = pd.DataFrame(specs, columns = ['Specs title','Specs value'])
    return df

def get_review(url,page):
    print(url,page)
    reviews = []
    # url = url.split('urw')
    # url1 = 'urw/Samsung-TU7000-43-4K-LED-Smart-TV-Titan-Gray'.join(url)
    # print(url1)
    print("in get_review")
    for i in range(1):
        print(f'in loop{i}')
        
        url = url + str(0+i)
        soup = get_page(url)
        

        try: 
            review= soup.find_all('p',attrs= {'class':"review-item-content rvw-wrap-spaces", 'itemprop':"reviewBody"})
        except:
            review = ''
        finally:
            if review !="":
                reviews.extend(review)
    
    for i in range(len(reviews)):
        reviews[i] = str(reviews[i]).replace('<p class="review-item-content rvw-wrap-spaces" itemprop="reviewBody">','')
        reviews[i] = str(reviews[i]).replace('<span class="show-full-review">','')
        reviews[i] = str(reviews[i]).replace('</span>','')
        reviews[i] = str(reviews[i]).replace('</br>','')
        reviews[i] = str(reviews[i]).replace('<br/>','')
        reviews[i] = str(reviews[i]).replace('</p>','')
        reviews[i] = str(reviews[i]).replace('<a class="show-full-review-link" href="javascript:;">Read full review...</a>','')

    return reviews

base_value = 200

large_items=[]
for j in range(5):
    for i in range(10):
        ebayUrl = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw=heater&_sacat=0&_udhi={(j+1)*5+base_value}&rt=nc&_udlo={j*5+base_value}&_pgn="+str(i+1)
        r= requests.get(ebayUrl)
        data=r.text
        soup=BeautifulSoup(data,"html.parser")

        # get all listings 
        listings = soup.find_all('li', attrs={'class': 's-item'})
        links = soup.find_all('a', class_ ='s-item__link')
        items = [item.get('href') for item in links] # store the link to each product 
        large_items.extend(items)

print(len(large_items))
print(large_items)
    
array = []
dict_keys = []
dict_specs = []
for i in range(len(large_items)-1):
    soup =  get_page(large_items[i+1])   #open each product's url
    results, specs_dict = get_detail_data(soup) 
    dict_specs.append(specs_dict)
    for k in specs_dict.keys():
        if k not in dict_keys: # get all possible specs found
            dict_keys.append(k)
    # print(results)
    array.append(results)  #store all the details of a product

    
df_test = pd.DataFrame([[None]*len(dict_keys)]*len(dict_specs),columns=dict_keys)
i = 0
for dict in dict_specs:
    for k,v in dict.items():
        df_test.loc[i][k]= v
    i += 1
print(df_test)
df_review = pd.DataFrame(array, columns = ['Title','Price','Sold','Reviews'])
df = pd.concat([df_review, df_test], axis=1)
print(df)

#export into a json file for cleaning

if not os.path.exists("./outputs/ebay"):
    os.makedirs("./outputs/ebay")

df.to_csv(f"./outputs/ebay/heater{base_value}-{base_value + 5*5}.csv", index=False)




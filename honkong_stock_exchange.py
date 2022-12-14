# -*- coding: utf-8 -*-
"""honkong_stock_exchange.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OyF9Azq0sZR5TuixRLdEpuuD3vK629PL
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import os

# function to create soup
def create_soup(url):
    response = requests.get(url)
    soup     = BeautifulSoup(response.content, 'html.parser')
    return soup

url = 'https://www.hkex.com.hk/eng/stat/smstat/dayquot/d220608e.htm#dealings_suspstocks'

# creating soup
soup = create_soup(url)

# required texts are inside 'font' tags
# getting all texts
all_texts = soup.find_all('font', attrs = {'size' : '1'})

# let's check type of it
type(all_texts)

# let's check length of it
len(all_texts)

# slicing QUOTATIONS from all_texts
quotations = all_texts[:112]

# try len(quotations)
# try quotations[0]
# try quotations[-1]

# first item and last item of the quotations list contain extra information
# we will need to process these items
quotations[0].text.split('QUOTATIONS')[-1]

# something unusual
quotations[2].text.split('\r\n')[-1]

# desired headings
headings = quotations[0].text.split('QUOTATIONS')[-1].split('\r\n\r\n')[1]
headings

# create a list for all quotation
quotations_lists = []

# processing of first item
quotation_first_item = quotations[0].text.split('QUOTATIONS')[-1].split('\r\n\r\n')[2]

# adding first item in quotations_lists
quotations_lists += quotation_first_item.split('\r\n')[:-1]

# adding remaining items in quotations_lists except last one
for item in quotations[1:111]:
    quotations_lists += item.text.split('\r\n')[:-1]

# processing of last item
quotation_last_item = quotations[111].text.split('\r\n-------------------------------------------------------------------------------')[0]

# adding last item in quotations_lists
quotations_lists += quotation_last_item.split('\r\n')

len(quotations_lists)

quotations_lists[0:10]

def splited_list(item):

    ### different types of item

    # '50090#UB#MTUANRP2303N  HKD TRADING SUSPENDED'
    # '40808 SHINSUN N2308    USD TRADING SUSPENDED'
    # '709#GIORDANO INT'L   HKD TRADING HALTED'
    # '50234#UB#JDCOMRP2302B  HKD    0.04     0.015    0.027           1,312,500'
    # '50076 CS#MTUANRC2302M  HKD    0.155    0.175    0.176             175,000'
    # '50062#BP#HSI  RP2210H  HKD    0.053    0.02     0.024          44,340,000'
    # '40101 KM RT B2412      USD     N/A      -        -                      -'  
    # '122 CROCODILE        HKD    0.34     0.39     0.405          12,245,000'
    # '*  388 HKEX             HKD  352.20   361.40   362.80            8,347,757' 

    elements = item.split()
    li = []
    for elem in elements:
        if '#' in elem:
            li += elem.split('#')
        else:
            li.append(elem)
    return li


def suspended(li):
    # sample list
    # li = ['50105', 'UB', 'HSI', 'RP2211R', 'HKD', 'TRADING', 'SUSPENDED']

    code = int(li[0])
    nos  = ' '.join(li[1:-3])      # nos = Name of Stock
    cur  = li[-3]

    return code, nos, cur


def check(x):
    try:
        elem = float(x)
    except:
        elem = x
    return elem

def check_lsit_last_item(x):
    try:
        elem = int(''.join(x.split(',')))
    except:
        elem = x
    return elem

def not_suspended(li_1, li_2):
    # sample list
    # li = ['50234', 'UB', 'JDCOMRP2302B', 'HKD', '0.04', '0.015', '0.027', '1,312,500']
    # li = ['85987', 'CCB', 'B2304-R', 'CNY', 'N/A', '-', '-', '-']
    
    code = int(li_1[0])

    nos  = ' '.join(li_1[1:-5])                   # nos = NAME OF STOCK
    cur  = li_1[-5]

    cpc  = check(li_1[-4])                   # cpc = CUR PRV.CLO. 
    cls = check(li_2[0])                # cls = CLOSING

    ask  = check(li_1[-3])  
    bid = check(li_2[-3])

    high = check(li_1[-2]) 
    low = check(li_2[-2])

    st = check_lsit_last_item(li_1[-1])     # st = SHARES TRADED
    tnvr = check_lsit_last_item(li_2[-1])       # tnvr = TURNOVER


    

    return code, nos, cur, cpc, cls, ask, bid, high, low, st, tnvr

# total item in quotations_lists
total_item = len(quotations_lists)

final_list = []
i = 0
while (i< total_item):

    item_1= quotations_lists[i]
    list_1 = splited_list(item_1)

    if '*' in list_1:
        list_1.remove('*')
        
    if 'SUSPENDED' in list_1:
        dic = {}
        code, nos, cur = suspended(list_1)
        dic['CODE'] = code
        dic['NAME OF STOCK'] = nos
        dic['CUR'] = cur

        final_list.append(dic)
        i+=1

    if 'HALTED' in list_1:
        dic = {}
        code, nos, cur = suspended(list_1)
        dic['CODE'] = code
        dic['NAME OF STOCK'] = nos
        dic['CUR'] = cur

        final_list.append(dic)
        i+=1


    if 'SUSPENDED' not in list_1:
        item_2 = quotations_lists[i+1]
        list_2 = splited_list(item_2)
        
        dic = {}
        
        code, nos, cur, cpc, cls, ask, bid, high, low, st, tnvr = not_suspended(list_1, list_2)

        dic['CODE'] = code
        dic['NAME OF STOCK'] = nos
        dic['CUR'] = cur
        dic['CUR PRV.CLO.'] = cpc
        dic['CLOSING'] = cls
        dic['ASK'] = ask
        dic['BID'] = bid
        dic['HIGH'] = high
        dic['LOW'] = low
        dic['SHARES TRADED'] = st
        dic['TURNOVER'] = tnvr

        final_list.append(dic)
        i +=2

final_list[-1]

len(final_list)

# Creating Data Frame using pandas
df = pd.DataFrame(final_list)

df

# exporting data frame to CSV file
df.to_csv('all_data.csv',index=False)
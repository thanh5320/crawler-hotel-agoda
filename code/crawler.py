import cv2
import numpy as np
import sys,os
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import json
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from helium import *
from webdriver_manager.chrome import ChromeDriverManager
import array as arr
import json
import hashlib

driver = webdriver.Chrome(ChromeDriverManager().install())

def getInfor(link):
    dict = {"id": "", "link":"", "name":"", "imgs": "", "city":"", "address":"", "description":"","review_score":"", "rooms": [], "nears": [], "services":[]}
    review_score = {"score":0, "count": 0, "clean":0, "convenient":0, "location":0, "service": 0, "worth_the_money":0}
    room= {"name": "", "imgs":"", "utils":"", "benefit":"","adults":0, "children": 0, "cost": 0}
    driver.get(link)
    sleep(5)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load the page
        sleep(3)
        # Calculate new scroll height and compare with last height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        sleep(3)
    sleep(10)
    htmltext = driver.page_source
    soup = BeautifulSoup(htmltext, "html.parser", from_encoding="utf-8")

    name = soup.find("h1", class_="HeaderCerebrum__Name")
    if len(name) > 0:
        for i in name:
            dict["name"] = i.text
    #else:return None

    imgs = soup.findAll("img", class_="SquareImage")
    if len(imgs) > 0:
        arrImg = []
        for img in imgs:
            arrImg.append(img['src'].lstrip("/"))
        dict["imgs"] = arrImg
    #else:return None


    description=soup.findAll("div", {"data-element-name":"abouthotel-description"})
    if len(description) > 0:
        description = description[0].find_all("p")
        if len(description) > 0:
            dict["description"] = description[0].text
    #else:return None



    city = soup.findAll("div", class_="breadcrumb-regionName")
    if len(city) == 3:
        dict["city"] = city[2].text[10:-1]+city[2].text[-1]
    #else:return None
    
    address = soup.findAll("span", class_="Typographystyled__TypographyStyled-sc-j18mtu-0 dkxzVC kite-js-Typography")
    if len(address) > 0:
        dict["address"] = address[0].text
    #else:return None

    reviewScore1 = soup.findAll("span", class_="Review__ReviewFormattedScore")
    reviewScore2 = soup.findAll("span", class_="ReviewScore-Number")
    if len(reviewScore1) > 0:
        review_score["score"] = reviewScore1[0].text
    elif len(reviewScore2) > 0:
        review_score["score"] = reviewScore2[0].text

    reviewScoreCountP = soup.findAll("div", class_="CombinedReview__ReviewBaseOn")
    if len(reviewScoreCountP) > 0:
        numeric_filter = filter(str.isdigit, reviewScoreCountP[0].find_all("span")[0].text)
        numeric_string = "".join(numeric_filter)
        review_score["count"] = numeric_string 
    
    #soup.select('span[class*="Review-travelerGradeScore Review-travelerGradeScore--"]')
    reviewScoreAttr = soup.select('span[class*="Review-travelerGradeScore Review-travelerGradeScore--"]') #= soup.findAll("span", class_="Review-travelerGradeScore Review-travelerGradeScore--")
    if len(reviewScoreAttr) >= 1:
        review_score["clean"] = reviewScoreAttr[0].text
    if len(reviewScoreAttr) >= 2:
        review_score["convenient"] = reviewScoreAttr[1].text
    if len(reviewScoreAttr) >= 3:
        review_score["location"] = reviewScoreAttr[2].text
    if len(reviewScoreAttr) >= 4:
        review_score["service"] = reviewScoreAttr[3].text
    if len(reviewScoreAttr) == 5:
        review_score["worth_the_money"] = reviewScoreAttr[4].text

    dict["review_score"] = review_score


    roomTags = soup.findAll("div", class_="MasterRoom")
    if len(roomTags)>0:
        rooms=[]
        i=0
        for roomTag in roomTags:
            i+=1
            room= {"id":"", "name": "", "imgs":[], "utils":[], "benefit":"","adults":0, "children": 0, "cost": 0}
            roomNameTag = roomTag.find_all("span", class_="MasterRoom__HotelName")
            if len(roomNameTag) >0:
                room["name"] = roomNameTag[0].text
                str_id = roomNameTag[0].text + str(i)
                hash_id = hashlib.md5(str_id.encode())
                room["id"]=hash_id.hexdigest()

            imgTag= roomTag.find_all("img")
            if len(imgTag)>0:
                imgs=[]
                for img in imgTag:
                    imgs.append(img['src'].lstrip("/"))
                room["imgs"] = imgs

            utilsTags = roomTag.find_all("div", class_="MasterRoom-amenitiesTitle")
            if len(utilsTags) > 0:
                utils = []
                for utilsTag in utilsTags:
                    util = utilsTag.find_all("div")
                    if len(util)>0:
                        utils.append(util[0].text)
                room["utils"] = utils

            
            childRoomTag = roomTag.find_all("div", class_="ChildRoomsList-room-contents")
            if len(childRoomTag) >0:
                childRoomTag=childRoomTag[0]
                benefits=[]
                benefitTags=childRoomTag.find_all("span", class_="ChildRoomsList-roomFeature-TitleWrapper")
                if len(benefitTags) >0:
                    for benefifTag in benefitTags:
                        benefits.append( benefifTag.text)
                room["benefit"]=benefits

                costTag = childRoomTag.find_all("span", class_="pd-price")
                if len(costTag)>0:
                    room["cost"]=costTag[0].find_all("strong")[0].text
        
            rooms.append(room)
        dict["rooms"] = rooms

    nearTags = soup.findAll("div", {"data-element-name" : "about-hotel-whats-nearby-section"})
    if len(nearTags)>0:
        nears = []
        childNearTags=nearTags[0].findAll("div", {"data-element-value":"available"})
        if len(childNearTags) >0:
            for childTag in childNearTags:
                nameNearTags = childTag.find_all("span", class_="Spanstyled__SpanStyled-sc-16tp9kb-0 gwICfd")
                disNearTags = childTag.find_all("span", class_="Spanstyled__SpanStyled-sc-16tp9kb-0 ciawxZ")
                near={"name":"", "distance":""}
                if len(nameNearTags)>0:
                    near["name"]=nameNearTags[0].text
                    if len(disNearTags) >0:
                        s1= disNearTags[0].text
                        s2=disNearTags[0].text
                        numeric_filter = filter(str.isdigit, s2)
                        numeric_string = "".join(numeric_filter)
                        if s1.find("km") != -1:
                            if s1.find(",") != -1:
                                numeric_string= numeric_string+'00'
                            else:
                                numeric_string =numeric_string+'000'
                        near["distance"]=numeric_string
                nears.append(near)
        dict["nears"]=nears   

    serviceTags = soup.findAll("div", {"data-element-name" :"abouthotel-amenities-facilities"})
    if len(serviceTags)>0:
        services=[]
        childServiceTags = serviceTags[0].findAll("ul", class_="Liststyled__ListStyled-sc-ksl08h-0 iTjiYt")
        nameServiceTags = serviceTags[0].findAll("p", class_="Paragraphstyled__ParagraphStyled-sc-180znkb-0 dZrFOf Box-sc-kv6pi1-0 kainWI")

        if len(nameServiceTags)>0 and len(childServiceTags)==len(nameServiceTags):
            for i in range(0, len(childServiceTags)):
                service={"name": "", "service":[]}
                service["name"] = nameServiceTags[i].text
                childs = childServiceTags[i].findAll("span", class_="Spanstyled__SpanStyled-sc-16tp9kb-0 gwICfd")
                if len(childs)>0:
                    childService = []
                    for child in childs:
                        childService.append(child.text)
                    service["service"]=childService
                services.append(service)
        dict["services"]=services


    dict["link"] = link
    hash_id = hashlib.md5(link.encode())
    dict["id"]=hash_id.hexdigest()
    print(dict)
    return dict

links = pd.read_csv("/home/thanhnv/Desktop/python-crawler-hotel/data/input/linkHotel.csv")
links = links["link"]
toppic_es = {"index": {"_index": "hotel"}}
toppic_es_json = json.dumps(toppic_es)
for link in links:
    data=getInfor(link)
    if data == None:
        print(data) 
        continue

    json_object = json.dumps(data,ensure_ascii=False).encode('utf8') # view dữ liệu thì thêm cái này indent = 4
    
    with open("/home/thanhnv/Desktop/python-crawler-hotel/data/output/output.jl", "a+", encoding='utf8',newline='\n') as outfile:
        outfile.write(toppic_es_json)
        outfile.write('\n')
        outfile.write(json_object.decode())
        outfile.write('\n')


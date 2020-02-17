from flask import Flask, render_template, send_from_directory, jsonify, request, redirect
import sqlite3
from yelp.client import Client
import requests
from yelpapi import YelpAPI
from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather
from math import sin, cos, sqrt, atan2, radians
from geopy.geocoders import Nominatim
import math
from random import randint
from datetime import timedelta, date
import secretkeys

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])    
def home():
    error = request.args.get('error')
    if error == "true":
        message1 = "Try Another Origin"
        message2 = "Try Another Destination"
    else:
        message1 = "Origin"
        message2 = "Destination"
    return render_template("index.html", message1=message1,message2=message2)

@app.errorhandler(500)
def pageNotFound(error):
    return redirect("https://travel.aru.wtf?error=true")

@app.route('/middleman', methods=['POST','GET'])    
def middleman():
    from_loc = request.args.get('ufl')
    to_loc = request.args.get('utl')
    flight = request.args.get('fl')
    print(from_loc)
    print(to_loc)
    print(flight)
    if flight == "flight":
        motd = "flight"
    elif flight == "uber":
        motd = "uber"
    else:
        motd = "drive"

    gen_url = f"https://travel.aru.wtf/travel?from={from_loc}&to={to_loc}&mot={motd}"
    return redirect(gen_url)

@app.route('/travel')
def location():
    user_from = request.args.get('from')
    user_to = request.args.get('to')
    flight_bool = request.args.get('mot')   
    print(user_from)
    print(user_to)

    yelp_api_key = secretkeys.yelpApiKey

    yelp_api = YelpAPI(yelp_api_key)

    from_location = user_from
    end_location = user_to

    # get lat/lon

    geolocator = Nominatim(user_agent="codeday")

    pre_from = geolocator.geocode(from_location)
    pre_end = geolocator.geocode(end_location)

    from_lat = pre_from.latitude
    from_lon = pre_from.longitude
    end_lat = pre_end.latitude
    end_lon = pre_end.longitude

    # end get lat/lon

    # get date

    endDate = date.today() + timedelta(days=10)

    dateSend = endDate.strftime("%m/%d/%Y")

    # end get date

    # start gas price

    R = 6373.0

    lat1 = radians(from_lat)
    lon1 = radians(from_lon)
    lat2 = radians(end_lat)
    lon2 = radians(end_lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c * 0.62137)
    pre_fuel = (R * c * 0.62137)/24.9
    print(distance)
    price = pre_fuel * 2.07
    print("Estimated Gas Price = $" + str(price))

    # end gas price

    # start food

    # breakfast
    search_results = yelp_api.search_query(term='breakfast', location=end_location, sort_by='rating', limit=1)
    data = search_results['businesses'][0]
    b_name = data['name']
    b_temp_url = data['url']
    b_address = data['location']['address1']
    try:
        b_price = data['price']
    except:
        b_price = "Unknown"
    long_url = b_temp_url.split("?adjust_creative")[0]
    url = f"https://api-ssl.bitly.com/v3/shorten?access_token={secretkeys.bitlyApiKey}&longUrl={long_url}"
    data = requests.get(url)
    b_url = data.json()['data']['url']

    print("BREAKFAST\n")
    print(b_name)
    print(b_url)
    print(b_address)

    # lunch
    search_results = yelp_api.search_query(term='lunch', location=end_location, sort_by='rating', limit=1)
    data = search_results['businesses'][0]
    l_name = data['name']
    l_temp_url = data['url']
    l_address = data['location']['address1']
    try:
        l_price = data['price']
    except:
        l_price = "Unknown"
    long_url = l_temp_url.split("?adjust_creative")[0]
    url = f"https://api-ssl.bitly.com/v3/shorten?access_token={secretkeys.bitlyApiKey}&longUrl={long_url}"
    data = requests.get(url)
    l_url = data.json()['data']['url']

    print("\nLUNCH\n")
    print(l_name)
    print(l_url)
    print(l_address)

    # dinner
    search_results = yelp_api.search_query(term='dinner', location=end_location, sort_by='rating', limit=1)
    data = search_results['businesses'][0]
    d_name = data['name']
    d_temp_url = data['url']
    d_address = data['location']['address1']
    try:
        d_price = data['price']
    except:
        d_price = "Unknown"
    d_url = d_temp_url.split("?adjust_creative")[0]
    long_url = d_temp_url.split("?adjust_creative")[0]
    url = f"https://api-ssl.bitly.com/v3/shorten?access_token={secretkeys.bitlyApiKey}&longUrl={long_url}"
    data = requests.get(url)
    d_url = data.json()['data']['url']
    

    print("\nDINNER\n")
    print(d_name)
    print(d_url)
    print(d_address)

    # end food

    # start weather

    sweather = requests.get(f"https://api.darksky.net/forecast/7bec78d2270b671ffc8bb9aef6e077f7/{end_lat},{end_lon},1581858824")
    call = sweather.json()

    try:
        raw_weather = int(call['currently']['temperature'])
        weather = str(call['currently']['temperature']) + "°F"
    except:
        weather = 60
        raw_weather = 60

    # end weather

    # start driving

    if flight_bool == "flight":
        header1 = "Flight Information"
        mildew = from_location + end_location
        flight_num = str(hash(mildew))[-4:]
        sub1 = f"Flight Number: DL{flight_num}"
        flight_price = 50 + distance*0.11
        sub2 = f"Flight Price: ${round(flight_price,2)} USD"
    elif flight_bool == "uber":
        header1 = "Uber Information"
        driving = distance/60*1.17
        sub1 = f"Estimated Driving Time: {round(driving,2)} Hours"
        sub2 = f"Estimated Costs: ${round((distance*1.5),2)}"
    else:
        header1 = "Driving Information"
        driving = distance/60*1.17
        sub1 = f"Estimated Driving Time: {round(driving,2)} Hours"
        sub2 = f"Estimated Gas Costs: ${round(price,2)} USD"

    # end driving

    # start hotel

    search_results = yelp_api.search_query(term='hotel', location=end_location, sort_by='rating', limit=1)
    data = search_results['businesses'][0]
    h_name = data['name']
    h_temp_url = data['url']
    h_address = data['location']['address1']
    try:
        h_price = data['price']
    except:
        h_price = "Unknown"
    long_url = h_temp_url.split("?adjust_creative")[0]
    url = f"https://api-ssl.bitly.com/v3/shorten?access_token={secretkeys.bitlyApiKey}&longUrl={long_url}"
    data = requests.get(url)
    h_url = data.json()['data']['url']

    # end hotel

    # start activities

    # activity 1
    search_results = yelp_api.search_query(term='activities', location=end_location, sort_by='rating', limit=3)
    data = search_results['businesses'][0]
    a1_name = data['name']
    a1_temp_url = data['url']
    a1_address = data['location']['address1']
    try:
        a1_price = data['price']
    except:
        a1_price = "Unknown"
    long_url = a1_temp_url.split("?adjust_creative")[0]
    url = f"https://api-ssl.bitly.com/v3/shorten?access_token={secretkeys.bitlyApiKey}&longUrl={long_url}"
    data = requests.get(url)
    a1_url = data.json()['data']['url']

    # activity 2
    search_results = yelp_api.search_query(term='activities', location=end_location, sort_by='rating', limit=3)
    data = search_results['businesses'][1]
    a2_name = data['name']
    a2_temp_url = data['url']
    a2_address = data['location']['address1']
    try:
        a2_price = data['price']
    except:
        a2_price = "Unknown"
    long_url = a2_temp_url.split("?adjust_creative")[0]
    url = f"https://api-ssl.bitly.com/v3/shorten?access_token={secretkeys.bitlyApiKey}&longUrl={long_url}"
    data = requests.get(url)
    a2_url = data.json()['data']['url']

    # activity 3
    search_results = yelp_api.search_query(term='activities', location=end_location, sort_by='rating', limit=3)
    data = search_results['businesses'][2]
    a3_name = data['name']
    a3_temp_url = data['url']
    a3_address = data['location']['address1']
    try:
        a3_price = data['price']
    except:
        a3_price = "Unknown"
    long_url = a3_temp_url.split("?adjust_creative")[0]
    url = f"https://api-ssl.bitly.com/v3/shorten?access_token={secretkeys.bitlyApiKey}&longUrl={long_url}"
    data = requests.get(url)
    a3_url = data.json()['data']['url']

    # actitvity stop

    # clothes pick start
    freezing_pants = ["khakis","jeans","sweatpants"]
    freezing_shoes = ["boots","tennis shoes","boots"]
    freezing_shirt = ["sweater","sweatshirt","jacket",]
    freezing_accessory = ["set of ear muffs","pair of gloves","beanie"]

    cold_pants = ["khakis","jeans","sweatpants"]
    cold_shoes = ["tennis shoes","vans","air force ones"]
    cold_shirt = ["light jacket","light sweater", "light jacket"]
    cold_accessory = ["pair of gloves","beanie","pair of gloves"]

    hot_pants = ["shorts","womens/mens workout shorts", "jean-shorts"]
    hot_shoes = ["tennis shoes","flip flops","crocks"]
    hot_shirt = ["t-shirt", "tank-top","t-shirt"]
    hot_accessory = ["pair of sunglasses", "bottle of sunscreen", "can of bug spray"]

    print("weather = " + str(raw_weather))
    
    if raw_weather < 32:
        index1 = randint(0,2)
        pants = freezing_pants[index1]
        shirt = freezing_shirt[index1]
        shoes = freezing_shoes[index1]
        accessory = freezing_accessory[index1]
    elif raw_weather > 32 and raw_weather < 60:
        index1 = randint(0,2)
        pants = cold_pants[index1]
        shirt = cold_shirt[index1]
        shoes = cold_shoes[index1]
        accessory = cold_accessory[index1] 
    else:
        index1 = randint(0,2)
        pants = hot_pants[index1]
        shirt = hot_shirt[index1]
        shoes = hot_shoes[index1]
        accessory = hot_accessory[index1]        
    #clothes pick stop       


    return render_template('location.html', date=dateSend,raw_weather=raw_weather,pants=pants,shirt=shirt,shoes=shoes,accessory=accessory,end_location=end_location.title(),header1=header1,sub1=sub1,sub2=sub2,a3_name=a3_name,a3_url=a3_url,a3_address=a3_address,a3_price=a3_price,a2_name=a2_name,a2_url=a2_url,a2_address=a2_address,a2_price=a2_price,a1_name=a1_name,a1_url=a1_url,a1_address=a1_address,a1_price=a1_price,h_name=h_name,h_url=h_url,h_address=h_address,h_price=h_price,b_name=b_name,b_url=b_url,b_address=b_address,b_price=b_price,l_price=l_price,d_price=d_price,l_name=l_name,l_url=l_url,l_address=l_address,d_name=d_name,d_url=d_url,d_address=d_address,weather=weather,gasprice=price)
        

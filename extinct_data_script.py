import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

#Web Scaping helper to convert unicode value to string
def unicodeToString(val):
	return val.encode('latin-1')

#Uses regular expression to get extinction year for a species
def getdate(x, speciesID):
	try:  
		match = re.search('\d{4}', x)
		if match is None:
			return getDateAlternative(speciesID)
		else:
			return match.group()
	except:
		return None

#alternative method to find extinction year if above method fails to get results
def getDateAlternative(speciesID):
	try:
		url = "http://www.iucnredlist.org/details/" + str(speciesID) + "/0"
		page_info = requests.get(url)
		soup = BeautifulSoup(page_info.content)
		script = soup.find_all("table", {"class": "tab_data"})[2].text
		script = unicodeToString(script).split("Justification:")[1].split("Previously published")[0]
		date_list = re.findall('\d{4}', script)
		date_list = [int(x) for x in date_list]
		min_date = min(date_list)
		return min_date
	except:
		return np.nan


def lastseen(row):
    # Parse data
    try:
        df = pd.read_json('http://api.iucnredlist.org/index/species/' + row["Genus"] + '-' + row["Species"] + '.json')
        df = df.fillna("")
        return getdate(df.loc[0, "rationale"], row["Species ID"])
    except:
        return np.nan


#Web Scraping method to get location data for each species
def getLocations(row):
	try:
		url = "http://www.iucnredlist.org/details/" + str(row["Species ID"]) + "/0"
		page_info = requests.get(url)
		soup = BeautifulSoup(page_info.content)
		script = soup.find_all("td", {"class": "rangeList"})[0].find_all("div", {"class": "group"})[0].text
		script = unicodeToString(script)
		script = script.split(':')[1]
		return script
	except:
		return None

#Load the extinct data frame and create relevant columns
extinct = pd.read_table("C:/Users/Wideet/Species Extinction Research/Data_Files/extinct_data_basic.csv", encoding='latin1', sep=",")
extinct_table = extinct
extinct_table["location"] = extinct_table.apply(getLocations, axis=1)
extinct_table["last_seen"] = extinct_table.apply(lastseen, axis=1)
#Export modified file with new columns
extinct_table.to_csv("C:/Users/Wideet/Species Extinction Research/Data_Files/extinct_dates_and_location.csv")










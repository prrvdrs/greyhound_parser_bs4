# Draft

from bs4 import BeautifulSoup
import requests
import csv
import time
import re

# Search Configuration
startDate   = "01-Jan-2018"
endDate     = "31-Dec-2018"
track       = "" # SPK or Empty String for all tracks)

# Get results
def getResults(startDate, endDate, track):
    baseUrl = "https://www.igb.ie/results"
    pageresults = 73
    meetingLocation = []
    meetingDate = [] # Store all meeting dates in a list
    meetingTrack = {"Derry": "DRY",
                    "Drumbo Park": "DBP",
                    "Dundalk": "DLK",
                    "Enniscorthy": "ECY",
                    "Galway": "GLY",
                    "Harolds Cross": "HRX",
                    "Kilkenny": "KKY",
                    "Lifford": "LFD",
                    "Limerick": "LMK",
                    "Longford": "LGD",
                    "Mullingar": "MGR",
                    "Newbridge": "NWB",
                    "Shelbourne Park": "SPK",
                    "Thurles Park": "THR",
                    "Tralee": "TRL",
                    "Tralee Sat Evening": "TRS",
                    "Waterford": "WFD",
                    "Youghal": "YGL"}
    #csvfile = open('race_results.csv', 'w')
    #writer = csv.writer(csvfile, delimiter=',', lineterminator='\n', quotechar='"')
    #writer.writerow(["Date","Race","Position", "Trap", "GreyhoundName","SireName", "DamName",
    #                 "Prize", "Weight", "WinTime", "By", "Going", "EstTime", "Spread","Grade", "Comm"])
    # Get meeting details: Date, Location, Link to Results
    while(True):
        try:
            url = f"{baseUrl}?FromDate={startDate}&ToDate={endDate}&stadium={track}&page={pageresults}"
            print(url)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            pageCheck = soup.find('a', text = 'View Results')
            if pageCheck:
                tables = soup.find_all("table")
                meetingtable = tables[0]
                trs = meetingtable.find_all("tr")
                for rows in trs[1:]:
                    cols = rows.find_all(['th', 'td'])  # find all the <th> or <td> columns inside each row
                    location = cols[0].get_text(strip=True)
                    meeting = cols[1].get_text(strip=True)
                    meetingLocation.append(location)
                    meetingDate.append(meeting.replace(' ','-'))
                    #writer.writerow([meeting])
                time.sleep(2)  # limit requests per second.
                pageresults += 1
            else:
                break
        except:
            break
    # Get race results of meetings and store to csv
    csvfile = open('race_results.csv', 'w')
    writer = csv.writer(csvfile, delimiter=',', lineterminator='\n', quotechar='"')
    writer.writerow(["Date", "Track","Location" ,"RaceTitle", "Distance", "Position", "Trap", "GreyhoundName", "SireName", "DamName",
                     "Prize", "Weight", "WinTime", "ByLenght", "Going", "EstTime", "Spread", "Grade", "Comm"])

    # Looping location list and check for key in dictionary to extract value (used in the result request url)
    # for ml in meetingLocation:
        # if ml in meetingTrack:
            # mt = meetingTrack[ml]

    for m, l in zip(meetingDate, meetingLocation):
        rurl = f"{baseUrl}/view-results/?track={track}&date={m}"
        print(rurl)
        racePage = requests.get(rurl)
        raceSoup = BeautifulSoup(racePage.content, "lxml")
        # Race Date
        # Race Name
        raceTitle = []
        raceHead = raceSoup.find_all("div", {"class": "col-16 clearfix race-heading"})
        for h in raceHead:
            title = h.find("h4").get_text(strip=True)
            raceTitle.append(title)
        # Race Result
        raceTables = raceSoup.find_all("div", {"class": "col-16 clearfix"})
        if len(raceHead) == len(
                raceTables):  # The first table does not contain any results and is part of the page layout.
            for t, r in zip(raceTables, raceTitle):
                tables = t.find("table")
                rowTables = tables.find_all("tr")
                # for r in raceTitle:
                for rows in rowTables[1:]:
                    cols = rows.find_all(['th', 'td'])  # Find all the <th> or <td> columns inside each row.
                    date = m
                    rtrack = "track"
                    location= l
                    race = r
                    distance = re.search('Flat \d+', r).group(0).replace('Flat', '')
                    position = cols[0].text
                    trapStage = cols[1].find('img')
                    trap = trapStage['alt'].replace('Trap ', '')
                    greyhoundName = cols[2].text
                    sireName = cols[3].text
                    damName = cols[4].text
                    prize = cols[5].text
                    weight = cols[6].text
                    winTime = cols[7].text
                    byLenght = cols[8].text.replace('L', '')
                    going = cols[9].text
                    estTime = cols[10].text.replace('&nbsp', '')
                    spread = ""
                    grade = cols[12].text
                    comm = cols[13].text
                    writer.writerow([date, rtrack, location, race, distance, position, trap, greyhoundName, sireName, damName, prize,
                                     weight, winTime, byLenght, going, estTime, spread, grade, comm])
            time.sleep(2)
        else:
            print("Race title/table mismatch")

getResults(startDate, endDate, track)
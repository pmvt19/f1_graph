from bs4 import BeautifulSoup 
import requests 
import numpy as np
import pprint
import pandas as pd
import matplotlib.pyplot as plt  

allRaces = []


def getAllRaceLinks(year):
    global allRaces
    url = "https://www.formula1.com/en/results.html/{}/races.html".format(year)
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser") 

    tags = doc.table.find_all('a')
    
    links = []
    for i, tag in enumerate(tags):
        # links.append((tag['href'], i))
        # allRaces.append(tag['href'].split('/')[6])
        links.append((tag['href'], i))
        allRaces.append(tag.string.strip())
    return np.array(links)


def getSingleRaceResult(linkData):
    link, raceNum = linkData

    url = "https://www.formula1.com{}".format(link)
    result = requests.get(url) 

    doc = BeautifulSoup(result.text, "html.parser") 

    tags = doc.table.tbody.find_all('tr')

    raceResults = []
    raceName = link.split('/')[6]

    for i, tag in enumerate(tags):
        raceResults.append(parseSingleDriverRaceResult(tag, raceNum, raceName))

    return raceResults 


def parseSingleDriverRaceResult(result, raceNum, raceName):
    
    names = result.find_all('span')
    firstname = names[0].string
    lastname = names[1].string

    driverName = "{} {}".format(firstname, lastname) 

    driverPoints = result.find_all('td', class_="bold")[-1].string

    # print(driverName, end=", ")
    # print(raceName, driverPoints)

    return (driverName, (raceNum, raceName, driverPoints))
    


    # pass 

def formatDriverPointsDictionary(driverPoints):
    global allRaces 
    driverCount = {} 
    

    for driver in driverPoints.keys():
        racePoints = driverPoints[driver]
        allRacePoints = np.array([0.0 for i in range(len(allRaces))])
        # print(racePoints)
        for raceId, raceName, points in racePoints:
            allRacePoints[int(raceId)] = float(points)
        driverCount[driver] = allRacePoints
    
    return driverCount 

def createDataFrame(dict):
    global allRaces 
    df = pd.DataFrame(dict).T
    df.columns = allRaces 
    total_points = df.sum(axis=1)
    df['Total'] = total_points
    df = df.sort_values('Total', ascending=False)
    return df 

def generateGraph(df, numDrivers):
    global allRaces
    drivers = list(df.iloc[:numDrivers].index)
    totalPoints = np.zeros((numDrivers, len(allRaces)))
    for i, race in enumerate(allRaces):
        points = np.array(list(df[race][:numDrivers]))
        # print(df[race])
        # points = np.array(list(df.iloc[:numDrivers][i]))
        if i == 0:
            totalPoints[:, i] = points 
        else:
            totalPoints[:, i] = totalPoints[:, i-1] + points

        
        # print(points)
        
        # break 
    print(totalPoints)

    for i in range(len(drivers)):
        driver = drivers[i]
        plt.plot(allRaces, totalPoints[i], label=driver)
    plt.title("Formula 1 Championship")
    plt.xlabel("Race")
    plt.ylabel("Championship Points")
    plt.legend()
    plt.show()



def main():

    driverPointsCounter = {}

    links = getAllRaceLinks(2020)

    for link in links:
        results = getSingleRaceResult(link)

        for name, points in results: 
            if name not in driverPointsCounter.keys():
                driverPointsCounter[name] = [points]
            else:
                driverPointsCounter[name].append(points)

    formattedDriverPoints = formatDriverPointsDictionary(driverPointsCounter)
    df = createDataFrame(formattedDriverPoints)
    # print(df)
    generateGraph(df, 6)

    


if __name__ == "__main__":
    main()

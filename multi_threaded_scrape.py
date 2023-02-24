from threading import Lock
from bs4 import BeautifulSoup 
import requests 
import numpy as np
import pprint
import pandas as pd
import matplotlib.pyplot as plt  
import threading
import sys 

YEAR = 2005
NUM_DRIVERS = 6

allRaces = []
allDrivers = []
allDriversLinks = []
lock = Lock()


def reformatDriverNames(name):
    lastname, firstname = name.split(',')
    return firstname.strip() + ' ' + lastname.strip()

def getAllRaceNames(year):
    global allRaces
    url = "https://www.formula1.com/en/results.html/{}/races.html".format(year)
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.table.find_all('a')
    for i, tag in enumerate(tags):
        allRaces.append(tag.string.strip())

def getAllDriverNames(year):
    global allDrivers, allDriversLinks
    url = "https://www.formula1.com/en/results.html/{}/drivers.html".format(year)
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all('div', class_ = "select-wrap icon-arrow")[2].find_all('option')[1:]

    for i, tag in enumerate(tags):
        allDrivers.append(reformatDriverNames(tag.string.strip()))
        allDriversLinks.append(tag['value'])
    
def buildDataFrame():
    global allRaces, allDrivers, allDriversLinks

    dictCount = {}
    dictCount['Name'] = allDrivers 
    for race in allRaces:
        racePoints = [0.0 for i in range(len(allDrivers))]
        dictCount[race] = racePoints 

    df = pd.DataFrame(dictCount)
    df = df.set_index('Name')

    return df

def fillDataFrameDriver(df, year, driver, link):
    global lock 
    url = "https://www.formula1.com/en/results.html/{}/drivers/{}.html".format(year, link)
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.table.tbody.find_all('tr')

    for j, tag in enumerate(tags):
        race = tag.a.string.strip()
        points = float(tag.find_all('td', class_='bold')[-1].string)

        lock.acquire()
        df.loc[driver, race] = points 
        lock.release()

def fillDataFrame(df, year):
    global allRaces, allDrivers, allDriversLinks
    threads = []
    for i, driver in enumerate(allDrivers):

        t = threading.Thread(target=fillDataFrameDriver, args=[df, year, driver, allDriversLinks[i]])
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()



    total_points = df.sum(axis=1)
    df['Total'] = total_points
    df = df.sort_values('Total', ascending=False)
    return df 

def generateGraph(df, numDrivers, year):
    global allRaces

    drivers = list(df.iloc[:numDrivers].index)
    totalPoints = np.zeros((numDrivers, len(allRaces))).astype(float)
    for i, race in enumerate(allRaces):
        points = np.array(list(df[race][:numDrivers])).astype(float)

        if i == 0:
            totalPoints[:, i] = points 
        else:
            totalPoints[:, i] = totalPoints[:, i-1] + points
    print(totalPoints)

    for i in range(len(drivers)):
        driver = drivers[i]
        plt.plot(allRaces, totalPoints[i], label=driver)
    plt.title("Formula 1 Championship: {}".format(year))
    plt.xlabel("Race")
    plt.ylabel("Championship Points")
    plt.legend()
    plt.show()

def main():

    args = sys.argv 
    if (len(args) == 3):
        YEAR = args[1]
        NUM_DRIVERS = int(args[2])
    elif (len(args) == 2):
        YEAR = args[1]

    global allRaces, allDrivers, allDriversLinks
    getAllRaceNames(YEAR)
    getAllDriverNames(YEAR)
    df = buildDataFrame()
    df = fillDataFrame(df, YEAR)
    print(df)
    generateGraph(df, NUM_DRIVERS, YEAR)

if __name__ == "__main__":
    main()

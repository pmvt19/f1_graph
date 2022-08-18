from bs4 import BeautifulSoup 
import requests 
import numpy as np
import pprint
import pandas as pd
import matplotlib.pyplot as plt  

YEAR = 2022
NUM_DRIVERS = 6

allRaces = []
allDrivers = []
allDriversLinks = []

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
    # print(result.text)

    # tags = doc.div.find('select').find_all('option', value="all")
    # tags = doc.find('option', value='all')
    tags = doc.find_all('div', class_ = "select-wrap icon-arrow")[2].find_all('option')[1:]
    # print(tags)
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

def fillDataFrame(df, year):
    global allRaces, allDrivers, allDriversLinks
    
    for i, driver in enumerate(allDrivers):
        url = "https://www.formula1.com/en/results.html/{}/drivers/{}.html".format(year, allDriversLinks[i])
        result = requests.get(url)
        doc = BeautifulSoup(result.text, "html.parser")

        tags = doc.table.tbody.find_all('tr')

        for j, tag in enumerate(tags):
            race = tag.a.string.strip()
            points = float(tag.find_all('td', class_='bold')[-1].string)
            df.loc[driver, race] = points 

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
    global allRaces, allDrivers, allDriversLinks
    getAllRaceNames(YEAR)
    getAllDriverNames(YEAR)
    df = buildDataFrame()
    df = fillDataFrame(df, YEAR)
    print(df)
    generateGraph(df, NUM_DRIVERS, YEAR)

if __name__ == "__main__":
    main()

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
import os

load_dotenv()
announcementsURL = "http://cs.hacettepe.edu.tr/announcements.html"

def getPage(url):
    try:
        html = requests.get(announcementsURL)
        return html.text
    except requests.exceptions.ConnectionError:
        print("Can't get request")
        return None

def parseHTML(html):
    soup = BeautifulSoup(html, 'html.parser')

    subjectElements = soup.find_all('div', {'class': 'accordionButton'})
    contentElements = soup.find_all('div', {'class': 'accordionContent'})
    annoSubjects = [i.text for i in subjectElements]
    annoIDs = [i.get('id') for i in contentElements]

    return [{'subject': annoSubjects[i], 'url': annoIDs[i]} for i in range(0, len(annoSubjects))]


def readDataFile():
    try:
        savedFile = open("oldAnnouncements.json", "r")
        data = json.load(savedFile)
        savedFile.close()
        return data
    except Exception as e:
        print(e)


def writeDataToFile(data):
    try:
        file = open("oldAnnouncements.json", "w")
        json.dump(data, file)
        file.close()
        print("Written to file.")
    except Exception as e:
        print(e)


def checkDiff(oldData, newData):
    diffList = [i for i in newData if i not in oldData]
    return diffList


def sendTweet(data):
    webHookKey = os.getenv("WEBHOOKS_KEY")
    eventName = os.getenv("IFTTT_EVENT_NAME")
    for anno in data:
        payload = {'value1': anno['subject'], 'value2': announcementsURL+"?"+anno['url']}
        r = requests.post(f'https://maker.ifttt.com/trigger/{eventName}/with/key/{webHookKey}', data=payload)
        if(r.status_code == 200):
            print("Tweet sent.")
        else:
            print(r.status_code)

def main():
    response = getPage(announcementsURL)
    newAnnouncements = parseHTML(response)
    oldAnnouncements = readDataFile()
    diff = checkDiff(oldAnnouncements, newAnnouncements)
    if(len(diff) > 0):
        sendTweet(diff)
        writeDataToFile(newAnnouncements)

if __name__ == '__main__':
    main()



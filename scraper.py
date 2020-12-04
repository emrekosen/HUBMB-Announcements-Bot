from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
import os

load_dotenv()
announcementsURL = "http://cs.hacettepe.edu.tr/"

def getPage(url):
    try:
        html = requests.get(announcementsURL)
        return html.text
    except requests.exceptions.ConnectionError:
        print("Can't get request")
        return None

def parseHTML(html):
    soup = BeautifulSoup(html, 'lxml')
    annoDiv = soup.find('div', {'id': 'duyurular_ic'})
    subjectElements = annoDiv.find_all('p')
    annoSubjects = [i.a.text for i in subjectElements]
    annoIDs = [i.a['href'] for i in subjectElements]

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
        print("Written to file")
    except Exception as e:
        print(e)

def saveTweetDataToFile(data):
    with open('tweet.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(data)

def checkDiff(oldData, newData):
    diffList = [i for i in newData if i not in oldData]
    return diffList


def sendTweet(data):
    webHookKey = os.getenv("IFTTT_WEBHOOKS_KEY")
    eventName = os.getenv("IFTTT_EVENT")

    for anno in data:
        payload = {'value1': anno['subject'], 'value2': announcementsURL +anno['url']}
        saveTweetDataToFile(anno['subject'])
        r = requests.post('https://maker.ifttt.com/trigger/' + eventName + '/with/key/' + webHookKey, data=payload)
        if(r.status_code == 200):
            print("Tweet sent")
        else:
            print(r.status_code)

def main():
    response = getPage(announcementsURL)
    newAnnouncements = parseHTML(response)
    oldAnnouncements = readDataFile()
    diff = checkDiff(oldAnnouncements, newAnnouncements)
    print(diff)
    if(len(diff) > 0):

        sendTweet(diff)
        writeDataToFile(newAnnouncements)
    else:
        saveTweetDataToFile("")

if __name__ == '__main__':
    main()



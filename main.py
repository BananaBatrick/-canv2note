import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
import time
import json
import passwords

token = passwords.token
url = 'https://xxx.instructure.com/'
file_path = 'assignmentID.txt'

# notion stuff
notionToken = passwords.notionToken
hwID = passwords.hwID

headers = {
    "Authorization": "Bearer " + notionToken,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# discord webhooks
general = passwords.general

gov = passwords.gov
sports = passwords.sports
spanish = passwords.spanish
pe = passwords.pe
hug = passwords.hug
lit = passwords.lit

# ping roles
pingGeneral = passwords.pingGeneral
pingBanana = passwords.pingBanana

pingGov = passwords.pingGov
pingSports = passwords.pingSports
pingSpanish = passwords.pingSpanish
pingPE = passwords.pingPE
pingHug = passwords.pingHug
pingLit = passwords.pingLit

# class canvas id
govC = '31843'
sportsC = '31744'
spanishC = '31802'
peC = '31747'
hugC = '31672'
litC = '31369'
# ('24881', philosophy, pingPhilosophy)

classIDs = [(govC, gov, pingGov),
            (sportsC, sports, pingSports),
            (spanishC, spanish, pingSpanish),
            (peC, pe, pingPE),
            (hugC, hug, pingHug),
            (litC, lit, pingLit)]

checkDay = 7

def send(channels, ping, classid, assignid, name, time):
    ping = str(ping)
    classid = str(classid)
    assignid = str(assignid)
    name = str(name)
    time = str(time)
    for channel in channels:
        data = {
            "content": "<@&" + ping + "> https://xxx.instructure.com/courses/" + str(
                classid) + "/assignments/" + str(assignid),
            # "username": "custom username"
        }

        data["embeds"] = [
            {
                #"title": "Assignments due in a week",
                "title": "Assignments due in " + str(checkDay) + " days",
                "description": str(name) + ' is due ' + str(time)
            }
        ]

        result = requests.post(channel, json=data)

        # update sent events
        
        with open(file_path, 'a') as a:
            a.writelines(str(id) + '\n')

def createEntry(text, startDate, subject, assignmentLink, database = hwID, headers = headers):

    createUrl = 'https://api.notion.com/v1/pages'

    newPageData = {
        "parent": {"database_id": database},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": text
                        }
                    }
                ]
            },


            "URL" : {
                "url": assignmentLink
            },


            "Due": {
                "date":
                    {
                        #"2022-06-30T14:00:00Z"
                        "start": startDate,
                        'time_zone': 'America/Chicago'
                    }

            },
            "Class": {
                'select': {
                    'name': subject}
            }
        }
    }

    data = json.dumps(newPageData)
    # print(str(uploadData))

    res = requests.request("POST", createUrl, headers=headers, data=data)

    print(res.status_code)
    print(res.text)

if __name__ == '__main__':

    while True:
        try:

            for subject in classIDs:

                link = 'http://xxx.instructure.com/api/v1/courses/'+subject[0]+'/assignments/?per_page=1000'
                headers = CaseInsensitiveDict()
                headers["Authorization"] = "Bearer " + token

                assignments = requests.get(link, headers=headers)
                assignments = assignments.json()
                for assignment in assignments:
                    #print(assignment)
                    id = assignment['id']

                    name = assignment['name']
                    due_date = assignment['due_at']
                    isGraded = assignment['grading_type']
                    isLocked = assignment['locked_for_user']

                    # to check if assignment already sent
                    alreadySent = []
                    with open(file_path, 'r') as a:
                        alreadySent = a.readlines()

                    # print(alreadySent)

                    checkID = str(id) + '\n'


                    #print(assignment['name'])
                    #print(assignment['due_at'])

                    # this goes through the assignments that have a due date
                    if isGraded != 'not_graded' and due_date != None:

                        print(assignment['updated_at'])
                        # format date
                        due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ")
                        # convert to central time
                        due_date = due_date - timedelta(hours = 6)

                        timediff = due_date - datetime.today()
                        timediffDays = timediff.days

                        hrtime12 = datetime.strftime(due_date, "%m-%d %I:%M %p")
                        #print(hrtime12)

                        # post to discord
                        print(name, due_date, isGraded)
                        if 0 < timediffDays < checkDay:


                            if checkID not in alreadySent:
                                send(channels=[subject[1], general], ping=subject[2], classid=subject[0], assignid=id,
                                     name=name, time=hrtime12)
                                classIDtoTag = {
                                    govC: 'Government',
                                    sportsC: 'Team Sports',
                                    spanishC: 'Spanish',
                                    peC: 'PE II',
                                    hugC: 'Human Geography',
                                    litC: 'English'
                                }

                                classid = subject[0]
                                assignid = id
                                assignmentLink = "https://xxx.instructure.com/courses/" + str(classid) + "/assignments/" + str(assignid)
                                classTag = classIDtoTag[subject[0]]
                                ISOtime = due_date.isoformat()
                                createEntry(name, ISOtime, classTag, assignmentLink)

                    elif not isLocked and "extra credit" in name.lower() or "xc" in name.lower():
                        if checkID not in alreadySent:
                            #print(isLocked)
                            send(channels=[subject[1], general], ping=subject[2], classid=subject[0], assignid=id, name=name, time='at the end of the chapter')

            # delay for 5 minutes
            time.sleep(60*5)

        except Exception as e:
            print(e)

            data = {
                "content": "<@" + pingBanana + "> please check canvasDetector program.",
                # "username": "custom username"
            }
            result = requests.post(general, json=data)

            # give time before restarting program
            time.sleep(300)

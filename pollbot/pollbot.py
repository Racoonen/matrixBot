from bot.client import Bot
from pollbot.entities import Poll, PollTemplate, Vote
import pickle
import re
import time

Client = None
Methods = {}
Templates = {}
CurrentPolls = {}
EndedPolls = {}
PollCreation = {}
TemplateCreation = []


def init(url, username, password):
    global Client, Methods
    fillMethods()
    loadDatabase()
    Client = Bot(url, onMessage, Methods)
    Client.login(username, password)
    Client.inputLoop()


def fillMethods():
    global Methods
    Methods = {
        "!commands": help,
        "!remove": leave,
        "!startTemplate": startTemplate,
        "!createTemplate": createTemplate,
        "!deleteTemplate": deleteTemplate,
        "!endTemplate": endTemplateCreation,
        "!showTemplates": getAllTemplateNames,
        "!info": info,
        "!results": results,
        "!endpoll": endPoll,
        "!vote": vote,
        "!gopoll": goPoll,
        "!startpoll": startPoll,
        "!leave": leave
        }


def loadDatabase():
    global Templates
    try:
        Templates = pickle.load(open("./pollData/pollbot.pickledb", "rb"))
    except (OSError, IOError):
        updateDatabase()


def updateDatabase():
    pickle.dump(Templates, open("./pollData/pollbot.pickledb", "wb"), 4)


def leave(room, event):
    global Client
    room.send_notice("im leaving you now. good luck.")
    Client.removeRoom(room)


def help(room, event):
    help_str = "!startpoll      - Create a poll\n"
    help_str += "!gopoll        - To Start a poll\n"
    help_str += "!info          - View an ongoing poll\n"
    help_str += "!vote          - Vote in an ongoing poll\n"
    help_str += "!endpoll       - End an ongoing poll\n"
    help_str += "!results       - View the results of the last ended poll\n"
    help_str += "!leave         - Pollbot leaves the room\n"
    help_str += "!createTemplate <name> - To create a new poll template\n"
    help_str += "!endTemplate   - To end poll template creation\n"
    help_str += "!startTemplate  <name>  - To start a template poll\n"
    help_str += "!showTemplates - To show all template names\n"
    help_str += "!deleteTemplate <name> - To delete a template"
    room.send_notice(help_str)


def startPoll(room, event):
    global PollCreation
    if CurrentPolls.get(room.room_id, None) is not None:
        room.send_notice("There is already a poll in this room")
        return
    if PollCreation.get(room.room_id, None) is not None:
        room.send_notice("There is already a pollcreation in this room")
        return

    poll = Poll(room.room_id, event['sender'], None, None)
    PollCreation[room.room_id] = poll
    room.send_notice("Please send the question now")


def goPoll(room, event):
    global PollCreation, CurrentPolls
    p = PollCreation.get(room.room_id, None)
    if p is None:
        room.send_notice("There is no poll to start")
    del PollCreation[room.room_id]
    CurrentPolls[room.room_id] = p
    room.send_notice("Poll started!\nPlease vote now\n")
    info(room, event)
    updateDatabase()


def createTemplate(room, event):
    global TemplateCreation
    name = getNameFromBody(16, event)
    if name is None:
        room.send_notice("no name was given")
        return
    if not validTemplateName(name):
        room.send_notice("the name {} is not valid".format(name))
    template = PollTemplate(room.room_id, event['sender'], None, None, name)
    TemplateCreation.append(template)
    room.send_notice("You are creating a new template poll.\n"\
                      "Please send the question.")


def endTemplateCreation(room, event):
    global Templates, TemplateCreation
    poll = getOngoingCreationPoll(room.room_id, event['sender'])
    if poll is None:
        room.send_notice("There is no ongoing poll creation")
        return
    TemplateCreation.remove(poll)
    Templates[poll.name] = poll
    room.send_notice("Template created. Type !startTemplate " +
                     "{} to start this template".format(poll.name))
    updateDatabase()


def deleteTemplate(room, event):
    global Templates
    name = getNameFromBody(16, event)
    poll = Templates.get(name, None)
    if poll is None:
        room.send_notice("There is no template with the name {}".format(name))
        return
    Templates.remove(poll)
    room.send_notice("Template {} deleted".format(name))
    updateDatabase()


def startTemplate(room, event):
    global CurrentPolls
    if CurrentPolls.get(room.room_id, None) is not None:
        room.send_notice("There is already an ongoing poll in here")
        return
    name = getNameFromBody(15, event)
    if name is None:
        room.send_notice("No name given")
        return
    template = Templates.get(name, None)
    if template is None:
        room.send_notice("There is no template with the name {}".format(name))
        return
    poll = Poll(room.room_id, event['sender'],
                template.question, template.choices, name)
    CurrentPolls[room.room_id] = poll
    room.send_notice("Poll started! Infos with !info")
    info(room, event)


def getAllTemplateNames(room, event):
    ans = ""
    count = 1
    for key in Templates:
        ans += "{}. {}\n".format(count, key)
        count += 1
    room.send_notice("There are the following templates:\n{}".format(ans))


def ongoingCreation(room, event):
    p = getOngoingCreationPoll(room.room_id, event['sender'])
    if p is None:
        return
    room.send_notice(addMsgToPoll(p, event['content']['body']))


def vote(room, event):
    global CurrentPolls
    poll = CurrentPolls.get(room.room_id, None)
    if poll is None:
        room.send_notice("There are no polls at the moment")
        return
    vote = getNameFromBody(6, event)
    if vote is None:
        room.send_notice("Please take one choice")
        return
    room.send_notice(poll.vote(vote, event['sender']))
    updateDatabase()


def endPoll(room, event):
    global CurrentPolls
    p = CurrentPolls.get(room.room_id, None)
    if p is None:
        room.send_notice("There are no polls in this room")
        return
    if p.creator != event['sender']:
        room.send_notice("You can only end polls that you have created!")
        return
    del CurrentPolls[room.room_id]
    EndedPolls[room.room_id] = p
    results(room, event)


def info(room, event):
    p = CurrentPolls.get(room.room_id, None)
    if p is None:
        room.send_notice("There are no polls in this room")
        return
    room.send_notice(p.toString())


def results(room, event):
    p = EndedPolls.get(room.room_id, None)
    if p is None:
        room.send_notice("There are no polls in this room")
        return
    room.send_notice("Poll ended! Results:")
    room.send_notice(p.toString())


def addMsgToPoll(poll, msg):
    if poll.question is None:
        poll.question = msg
        return "Okay, now send me the choices one by one."
    if poll.choices is None:
            poll.choices = []

    poll.choices.append(msg)
    if poll.isTemplate():
        return "Response added. Send another choice or "\
               "type !endTemplate to close the creation"

    return "Response added. Send another choice "\
           "or type !startpoll to start the poll"


def getOngoingCreationPoll(room_id, creator_id):
    for p in TemplateCreation:
        if p.room_id == room_id and p.creator == creator_id:
            return p
    for k, v in PollCreation.items():
        if k == room_id and v.creator == creator_id:
            return v


def getNameFromBody(index, event):
    if len(event['content']['body']) <= index:
        return None
    return event['content']['body'][index:]


def onMessage(room, event):
    if re.match("@" + Client.Username, event['sender']):
        return
    if int(time.time()) - int((event['origin_server_ts']/1000)) < 5:
        try:
            command = event['content']['body'].split(" ")
            Client.getCommand(command[0], ongoingCreation)(room, event)
        except KeyError as e:
            print(e)


def validTemplateName(name):
    if Templates.get(name, None) is not None:
        return False
    for p in TemplateCreation:
        if p.name == name:
            return False
    return True

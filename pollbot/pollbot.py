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
    '''Initializes the pollbot

    Arguments:
        url {string} -- URL of the matrix homeserver
        username {string} -- username for the bot to login
        password {string} -- password for the bot to login
    '''

    global Client, Methods
    fillMethods()
    loadDatabase()
    Client = Bot(url, onMessage, Methods)
    Client.login(username, password)
    Client.inputLoop()


def fillMethods():
    '''Fill the commandlist which is provided by this pollbot
    '''

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
        "!leave": leave,
        "!add": addChoice
        }


def loadDatabase():
    '''Load the database which is being used to store template polls
    '''

    global Templates
    try:
        Templates = pickle.load(open("./pollData/pollbot.pickledb", "rb"))
    except (OSError, IOError):
        updateDatabase()


def updateDatabase():
    '''Update the database for the template polls
    '''

    pickle.dump(Templates, open("./pollData/pollbot.pickledb", "wb"), 4)


def leave(room, event):
    '''Leave-handler. The pollbot leaves the room

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    global Client
    room.send_notice("im leaving you now. good luck.")
    Client.removeRoom(room)


def help(room, event):
    '''Help-handler. The pollbot prints all availabe commands.

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    help_str = "!startpoll      - Create a poll\n"
    help_str += "!gopoll        - To Start a poll\n"
    help_str += "!info          - View an ongoing poll\n"
    help_str += "!add <choice>  - To add a choice to the current poll\n"
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


def addChoice(room, event):
    '''Add a choice to the current poll. Will also update the template poll

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    global Templates
    p = CurrentPolls.get(room.room_id, None)
    if p is None:
        room.send_notice("There is no poll in this room")
        return
    newChoice = getNameFromBody(5, event)
    p.appendChoices(newChoice)
    info(room, event)


def startPoll(room, event):
    '''Starts a new pollcreation.

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

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
    '''Starts a new poll. Must be created before!
    Look at startPoll

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

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
    '''Create a new template poll.

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    global TemplateCreation
    name = getNameFromBody(16, event)
    if name is None:
        room.send_notice("no name was given")
        return
    if not validTemplateName(name):
        room.send_notice("the name {} is not valid".format(name))
    template = PollTemplate(room.room_id, event['sender'], None, None, name)
    TemplateCreation.append(template)
    room.send_notice("You are creating a new template poll.\n"
                     "Please send the question.")


def endTemplateCreation(room, event):
    '''End a template poll creation

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

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
    '''Delete a template poll

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    global Templates
    name = getNameFromBody(16, event)
    poll = Templates.get(name, None)
    if poll is None:
        room.send_notice("There is no template with the name {}".format(name))
        return
    del Templates[name]
    room.send_notice("Template {} deleted".format(name))
    updateDatabase()


def startTemplate(room, event):
    '''Start a poll from a template.

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

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
    '''Get all template names

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    ans = ""
    count = 1
    for key in Templates:
        ans += "{}. {}\n".format(count, key)
        count += 1
    room.send_notice("There are the following templates:\n{}".format(ans))


def ongoingCreation(room, event):
    '''All message will be handled by this function.
    It checks wether there is a pollcreation of the sender of this message.

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    p = getOngoingCreationPoll(room.room_id, event['sender'])
    if p is None:
        return
    room.send_notice(addMsgToPoll(p, event['content']['body']))


def vote(room, event):
    '''Vote handler to vote for a choice of a poll

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

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
    '''End the current poll in the room.

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

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
    '''Print information of the current poll

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    p = CurrentPolls.get(room.room_id, None)
    if p is None:
        room.send_notice("There are no polls in this room")
        return
    room.send_notice(p.toString())


def results(room, event):
    '''Print the results of the last poll in this room

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    p = EndedPolls.get(room.room_id, None)
    if p is None:
        room.send_notice("There are no polls in this room")
        return
    room.send_notice("Poll ended! Results:")
    room.send_notice(p.toString())


def addMsgToPoll(poll, msg):
    '''Add the message to the poll
    If there is no question in the poll, the msg will be used for the question.
    Otherwise the msg will be a choice of the poll.

    Arguments:
        poll {Poll/TemplatePoll} -- poll to add the message to
        msg {string} -- message to add

    Returns:
        string -- string to print to the room
    '''

    if poll.question is None:
        poll.question = msg
        return "Okay, now send me the choices one by one."
    if poll.choices is None:
            poll.choices = []

    poll.appendChoices(msg)
    if poll.isTemplate():
        return "Response added. Send another choice or "\
               "type !endTemplate to close the creation"

    return "Response added. Send another choice "\
           "or type !startpoll to start the poll"


def getOngoingCreationPoll(room_id, creator_id):
    '''Get the poll which is currently created in the room.
    Could be a poll oder template poll object.

    Arguments:
        room_id {int} -- room id of the room
        creator_id {string} -- user id of the user

    Returns:
        Poll/TemplatePoll -- Poll which is being created by this user
    '''

    for p in TemplateCreation:
        if p.room_id == room_id and p.creator == creator_id:
            return p
    for k, v in PollCreation.items():
        if k == room_id and v.creator == creator_id:
            return v


def getNameFromBody(index, event):
    '''Get the info from the message in the event.
    Skips the first chars until the index.

    Arguments:
        index {int} -- index to skip to
        event {Event} -- event which has the message.
        Look at the matrix-sdk for more infos

    Returns:
        string -- string from this index to the end of the message
    '''

    if len(event['content']['body']) <= index:
        return None
    return event['content']['body'][index:]


def onMessage(room, event):
    '''All messaged will access this function.
    Checks wether there is a command in this message.

    Arguments:
        room {Room} -- room which must be leaved.
        Look at the matrix-sdk for more info
        event {Event} -- event which has all info like user_id, message, etc..
        Look at the matrix-sdk for more info
    '''

    if re.match("@" + Client.Username, event['sender']):
        return
    if int(time.time()) - int((event['origin_server_ts']/1000)) < 5:
        try:
            command = event['content']['body'].split(" ")
            Client.getCommand(command[0], ongoingCreation)(room, event)
        except KeyError as e:
            print(e)


def validTemplateName(name):
    '''Checks wether the name is already used

    Arguments:
        name {string} -- name to check

    Returns:
        bool -- True/False wether the name is valid or not
    '''

    if Templates.get(name, None) is not None:
        return False
    for p in TemplateCreation:
        if p.name == name:
            return False
    return True

from matrix_client.client import MatrixClient, Room
from matrix_client.api import MatrixRequestError
import sys
import config
import time


def doNothing(room, event):
    return


class Bot(object):

    def __init__(self, url, msgHandler, methods={}):
        '''This is the constructor to create a bot.

        Arguments:
            url {string} -- URL to the matrix homeserver
            msgHandler {function} -- function for handling all messages

        Keyword Arguments:
            methods {dict} -- contains all methods with the command as key
                              i.e. {"!help:printHelp} (default: {{}})
        '''
        self.Methods = methods
        self.Client = MatrixClient(url)
        self.Rooms = []
        self.MessageHandler = msgHandler

    def login(self, username, password):
        '''Method to login into the homeserver

        Arguments:
            username {string} -- Username to login
            password {string} -- Password for the login
        '''

        self.Username = username
        self.Client.login_with_password(username, password)
        self.Client.add_invite_listener(self.handleInvite)

        # Add all rooms we're currently in to self.Rooms
        # and add their callbacks
        for room_id, room in self.Client.get_rooms().items():
            room.add_listener(self.MessageHandler)
            self.Rooms.append(room_id)

    def addCommand(self, command, function):
        '''Add a new command to the method dictonary

        Arguments:
            command {string} -- command-string to listen for
            function {function} -- function which handles the command
        '''

        self.Methods[command] = function

    def removeCommand(self, command):
        '''Remove a existing command

        Arguments:
            command {string} -- command to delete in the method dictonary
        '''

        del self.Methods[command]

    def getCommand(self, command, default=doNothing):
        '''Get a command

        Arguments:
            command {string} -- get function of this command

        Keyword Arguments:
            default {function} -- this function will be returned if
            there is no command for that string (default: {doNothing})

        Returns:
            function -- function which handles the command
        '''

        return self.Methods.get(command, default)

    def inputLoop(self):
        '''This methods starts all listener threads
        and sleeps forever
        '''

        self.Client.start_listener_thread()
        while True:
            time.sleep(60)

    def addRoom(self, room):
        '''Add a new room to listen to

        Arguments:
            room {Room} -- new room to listen to
        '''

        room.add_listener(self.MessageHandler)
        self.Rooms = room.room_id

    def removeRoom(self, room):
        '''Remove a room from the listener list

        Arguments:
            room {Room} -- remove this room
        '''

        self.Rooms.remove(room.room_id)
        room.leave()

    def setOnMessage(self, onMessage):
        '''Set the function which handles all messages

        Arguments:
            onMessage {function} -- this function will handle all messages
        '''

        self.MessageHandler = onMessage

    def handleInvite(self, room_id, state):
        '''This method handles an invite
        It accepts all invites

        Arguments:
            room_id {int} -- room-id of the inviting room
            state {[type]} -- [description]
        '''

        print("Got invite to room: " + str(room_id))
        print("Joining...")
        room = self.Client.join_room(room_id)
        room.add_listener(self.MessageHandler)
        self.Rooms.append(room)

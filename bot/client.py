from matrix_client.client import MatrixClient, Room
from matrix_client.api import MatrixRequestError
import sys
import config
import time


def doNothing(room, event):
    return


class Bot(object):

    def __init__(self, url, msgHandler, methods={}):
        self.Methods = methods
        self.Client = MatrixClient(url)
        self.Rooms = []
        self.MessageHandler = msgHandler

    def login(self, username, password):
        self.Username = username
        self.Client.login_with_password(username, password)
        self.Client.add_invite_listener(self.handleInvite)

        # Add all rooms we're currently in to self.Rooms
        # and add their callbacks
        for room_id, room in self.Client.get_rooms().items():
            room.add_listener(self.MessageHandler)
            self.Rooms.append(room_id)

    def addCommand(self, command, function):
        self.Methods[command] = function

    def removeCommand(self, command):
        del self.Methods[command]

    def getCommand(self, command, default=doNothing):
        return self.Methods.get(command, default)

    def inputLoop(self):
        self.Client.start_listener_thread()
        while True:
            time.sleep(60)

    def addRoom(self, room):
        room.add_listener(self.MessageHandler)
        self.Rooms = room.room_id

    def removeRoom(self, room):
        self.Rooms.remove(room.room_id)
        room.leave()

    def setOnMessage(self, onMessage):
        self.MessageHandler = onMessage

    def handleInvite(self, room_id, state):
        print("Got invite to room: " + str(room_id))
        print("Joining...")
        room = self.Client.join_room(room_id)
        room.add_listener(self.MessageHandler)
        self.Rooms.append(room)

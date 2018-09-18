from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from pollbot import pollbot
import sys
import config


def startBot():
    try:
        pollbot.init(config.config("Homeserver"),
                     config.config("Username"),
                     config.config("Password"))
    except MatrixRequestError as e:
        print(e)
        if e.code == 403:
            print("Bad username or password.", file=sys.stderr)
            sys.exit(4)
        else:
            print("Check your sever details are correct.", file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    startBot()

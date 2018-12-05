# Matrix Pollbot

## Installation and start

In order to start this bot you must install the following pip packages:

    matrix-client
    pyyaml

Modify the config.yml to your own specs.
After that just run

    python3 main.py

to start the bot.

## Getting Started

You need to invite the bot into your chat room. It will accept all invites.

## Commands

| Command | Use |
| ------- | --- |
|!commands|To print all commands|
|!startpoll|To create a new poll|
|!gopoll|To start a poll created with !startpoll|
|!info|To get info about the current poll|
|!vote :number:|To vote in a poll|
|!add :choice:|To add a choice to current poll|
|!endpoll|To end the current poll|
|!results|To Print the results of the last poll|
|!leave|To make the bot leave the room|
|!createTemplate :name:|To create a template poll with that name|
|!endTemplate| To end the current poll template creation|
|!startTemplate :name:| To start the template poll with that name|
|!showTemplates| To show all template names|
|!deleteTemplate :name:| To delete the template poll with that name|


## Using the pollbot
### Polls

The pollbot will print the instructions to create a new poll.

### Templates

Templates are poll which can be started at any time without the need to create a new poll each time. Any template which is created within any room of the chat can be started everywhere.

## Bot SDK

I've created a small bot SDK in the bot directory of this repository. Feel free to use it for other bots.
Pull requests are welcomed.

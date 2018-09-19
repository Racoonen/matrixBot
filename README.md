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

To print all commands just type

| Command | Use |
| ------- | --- |
|!commands!|To print all commands|
|!startpoll|To create a new poll|
|!gopoll!|To start a poll created with !startpoll|
|!info|To get info about the current poll|
|!vote :number:|To vote in a poll|
|!!endpoll|To end the current poll|
|!results|To Print the results of the last poll|
|!leave|To make the bot leave the room|
|!createTemplate :name:|To create a template poll with that name|
|!endTemplate| To end the current poll template creation|
|!startTemplate :name:| To start the template poll with that name|
|!showTemplates| To show all template names|
|!deleteTemplate :name:| To delete the template poll with that name|

## Bot SDK

I've created a small bot SDK in the bot directory of this repository. Feel free to use it for other bots.
Pull requests are welcomed.
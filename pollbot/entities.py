class Vote(object):
    def __init__(self, user_id, choice_nr):
        '''This class is used to identify each vote

        Arguments:
            object {Vote} --
            user_id {string} -- user_id of user which voted
            choice_nr {int} -- choice number of vote
        '''

        self.user_id = user_id
        self.choice_nr = choice_nr


class Poll(object):
    def __init__(self, room_id, creator, question, choices, templateName=None):
        '''This class is used for making a poll

        Arguments:
            object {Poll} --
            room_id {int} -- id of the room in which the poll is
            creator {string} -- user which created the poll
            question {string} -- question which is being asked by the poll
            choices {list} -- choices to vote for

        Keyword Arguments:
            templateName {string} -- if the poll is created from a template
            (default: {None})
        '''

        self.creator = creator
        self.room_id = room_id
        self.question = question
        self.choices = choices
        self.templateName = templateName
        self.votes = []

    def appendChoices(self, choice):
        '''Append the current choices

        Arguments:
            choice {string} -- choice for the append
        '''
        self.choices.append(choice)

    def isTemplate(self):
        '''Returns wether this poll is a template or not

        Returns:
            bool -- True/False if this object is a template
        '''

        return False

    def toString(self):
        '''Get a string representing this object

        Returns:
            string -- String representing this object
        '''

        ans = ""
        ans += self.question + "\n"
        ans += "-" * len(self.question) + "\n"
        for i in range(0, len(self.choices)):
            num_votes = len([x for x in self.votes if x.choice_nr == i])
            ans += "{}. {}: {} votes \n".format(i+1,
                                                self.choices[i],
                                                num_votes)
        return ans

    def vote(self, vote, user_id):
        '''Vote for a choice in this poll

        Arguments:
            vote {int} -- number which was voted
            user_id {string} -- user id of the user which voted

        Returns:
            string -- short string for the info if the vote was valid
        '''

        self.votes = [x for x in self.votes if x.user_id != user_id]
        choice_idx = int(vote) - 1

        # Verify that the given number corresponds to a choice
        if choice_idx < 0 or choice_idx >= len(self.choices):
            return "Invalid Choice"
        # Add this vote
        self.votes.append(Vote(user_id, choice_idx))
        # Get this user's short name (not including server)
        short_name = user_id[:user_id.index(':')]
        # Get the choice they voted for
        choice = self.choices[choice_idx]
        return "{} has voted for '{}'!\n"\
               "!info - Show current results".format(short_name, choice)


class PollTemplate(object):
    def __init__(self, room_id, creator, question, choices, name):
        '''This class is used for creating template polls.

        Arguments:
            object {PollTemplate} --
            room_id {int} -- room id in which this template is created
            creator {string} -- user id of the creator
            question {string} -- question which is being asked by this poll
            choices {list} -- list of choices for this poll
            name {string} -- name of the template
        '''

        self.room_id = room_id
        self.name = name
        self.creator = creator
        self.question = question
        self.choices = choices

    def isTemplate(self):
        '''Returns wether this object is a template

        Returns:
            bool -- True/False
        '''

        return True

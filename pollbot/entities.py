class Vote(object):
    def __init__(self, user_id, choice_nr):
        self.user_id = user_id
        self.choice_nr = choice_nr


class Poll(object):
    def __init__(self, room_id, creator, question, choices, templateName=None):
        self.creator = creator
        self.room_id = room_id
        self.question = question
        self.choices = choices
        self.templateName = templateName
        self.votes = []

    def appendChoices(self, choice):
        print(choice)
        self.choices.append(choice)

    def isTemplate(self):
        return False

    def toString(self):
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
        self.room_id = room_id
        self.name = name
        self.creator = creator
        self.question = question
        self.choices = choices

    def isTemplate(self):
        return True

"""models.py - This file contains the class definitions for the Datastore
entities used by the Game."""

from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)
    total_games = ndb.IntegerProperty(default=0)

    @property
    def win_percentage(self):
        """Return user win percentage"""
        if self.total_games > 0:
            return float(self.wins)/float(self.total_games)
        else:
            return 0.0

    def to_form(self):
        """Returns a UserForm representation of the User"""
        form = UserForm()
        form.user_name = self.name
        form.email = self.email
        form.wins = self.wins
        form.total_games = self.total_games
        form.win_percentage = self.win_percentage
        return form

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.total_games += 1
        self.put()

    def add_loss(self):
        """Add a loss"""
        self.total_games += 1
        self.put()


class Game(ndb.Model):
    """Game object"""
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        game = Game(user=user, game_over=False, history=[])
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, game='', message='',
                 player_hand='', computer_hand='', won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        if player_hand != computer_hand:
            self.game_over = True
            self.put()
            if won:
                self.user.get().add_win()
            else:
                self.user.get().add_loss()

        # Add the game to the score 'board'
        score = Score(user=self.user, game=game, message=message, won=won,
                      player_hand=player_hand, computer_hand=computer_hand)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    game = ndb.StringProperty(required=True)
    message = ndb.StringProperty(required=True)
    player_hand = ndb.StringProperty(required=True)
    computer_hand = ndb.StringProperty(required=True)
    won = ndb.BooleanProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
                         game=self.game,
                         message=self.message,
                         player_hand=self.player_hand,
                         computer_hand=self.computer_hand,
                         won=self.won)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    message = messages.StringField(3, required=True)
    user_name = messages.StringField(4, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    hand = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    game = messages.StringField(2, required=True)
    message = messages.StringField(3, required=True)
    player_hand = messages.StringField(4, required=True)
    computer_hand = messages.StringField(5, required=True)
    won = messages.BooleanField(6, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """UserForm for outbound User information"""
    user_name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_games = messages.IntegerField(4, required=True)
    win_percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):
    """Return multiple UserForms"""
    items = messages.MessageField(UserForm, 1, repeated=True)


class HistoryForm(messages.Message):
    """HistoryForm for outbound History information"""
    items = messages.StringField(1, repeated=True)

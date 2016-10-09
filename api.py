# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import random
import endpoints
from protorpc import (
    remote,
    messages
)
from google.appengine.api import (
    memcache,
    taskqueue
)

from models import (
    User,
    Game,
    Score
)
from models import (
    StringMessage,
    GameForm,
    GameForms,
    NewGameForm,
    MakeMoveForm,
    ScoreForms,
    UserForms,
    HistoryForm
)
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2)
    )
GET_HIGH_SCORES_REQUEST = endpoints.ResourceContainer(
    number_of_results=messages.IntegerField(1),)


@endpoints.api(name='snake_water_gunApi', version='v1')
class snake_water_gunApi(remote.Service):

    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        game = Game.new_game(user.key)

        return game.to_form('Hey! We are sensing you as a pro of Snake Water Gun')  # noqa

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            raise endpoints.ForbiddenException(
                'Illegal action: Game is already over.')

        HANDS = ['gun', 'water', 'snake']
        if request.hand.lower() not in HANDS:
            raise endpoints.BadRequestException(
                'Select one of Snake Water Gun')

        player_hand = request.hand.lower()
        computer_hand = random.choice(HANDS)
        msg = 'Player "' + player_hand + '" vs ' + \
              'Computer "' + computer_hand + '", '

        if computer_hand == player_hand:
            result = 'Tie'
        elif computer_hand == 'water':
            if player_hand == 'snake':
                result = 'Player'
            elif player_hand == 'gun':
                result = 'Computer'
        elif computer_hand == 'snake':
            if player_hand == 'water':
                result = 'Computer'
            elif player_hand == 'gun':
                result = 'Player'
        elif computer_hand == 'gun':
            if player_hand == 'water':
                result = 'Player'
            elif player_hand == 'snake':
                result = 'Computer'

        if result == 'Player':
            message = msg + 'You win!'
            game.history.append(message)
            game.put()
            game.end_game(game=request.urlsafe_game_key, message=message,
                          player_hand=player_hand, computer_hand=computer_hand,
                          won=True)
            return game.to_form(message)
        elif result == 'Computer':
            message = msg + 'You lose!'
            game.history.append(message)
            game.put()
            game.end_game(game=request.urlsafe_game_key, message=message,
                          player_hand=player_hand, computer_hand=computer_hand,
                          won=False)
            return game.to_form(message)
        elif result == 'Tie':
            message = msg + 'Tie! You can\'t beat me. I am challenging you!'
            game.history.append(message)
            game.put()
            game.end_game(game=request.urlsafe_game_key, message=message,
                          player_hand=player_hand, computer_hand=computer_hand,
                          won=False)
            return game.to_form(message)

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Get an individual user's current games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        games = Game.query(Game.user == user.key)
        games = games.filter(Game.game_over == False)
        if games.count() > 0:
            return GameForms(items=[game.to_form("{}'s active games.".format(
                request.user_name)) for game in games])
        else:
            raise endpoints.NotFoundException('This user has no active games!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/cancel_game',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel a game in progress"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.end_game(won=False)
            game.key.delete()
            return StringMessage(
                message='Game {} has been cancelled'.format(
                    request.urlsafe_game_key))
        elif game and game.game_over:
            return StringMessage(
                message='Game {} is already over!'.format(
                    request.urlsafe_game_key))
        else:
            raise endpoints.NotFoundException('Game not found.')

    @endpoints.method(request_message=GET_HIGH_SCORES_REQUEST,
                      response_message=UserForms,
                      path='scores/high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Generate a list of high scores of won games in descending order"""
        users = User.query().fetch(limit=request.number_of_results)
        users = sorted(users, key=lambda x: x.wins, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by their win percentage"""
        users = User.query(User.total_games > 0).fetch()
        users = sorted(users, key=lambda x: x.win_percentage, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryForm,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Retrieves an individual game history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return HistoryForm(items=game.history)
        else:
            raise endpoints.NotFoundException('Game not found!')

api = endpoints.api_server([snake_water_gunApi])

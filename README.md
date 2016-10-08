#Design A Game - snake, water, gun
** Play and test @ https://snakewatergun.appspot.com/_ah/api/explorer **

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
2.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default:

        localhost:8080/_ah/api/explorer

3. Open Chrome with command:

        /Google\ Chrome --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080

##Game Description:
Challenge a sophisticated computer with your favorite hand! You can choose from
either `snake`, `water`, or `gun`. If you and the computer both choose the
same hand, you will get a "tie" and it doesn't count towards any points, and it
will not terminate the ongoing game. If your hand counters the computer's, you
score **1** winning point! Your win percentage is calculated as:
**games won** / **total games played**

Many different snake water gun games can be played by many different Users
at any given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, hand
    - Returns: GameForm with new game state.
    - Description: Accepts a 'hand' and returns the updated state of the game.
    'hand' must be either `Snake`, `Water`, or `Gun` - will raise a
    BadRequestException if not. If the result is 'tie', the game is not yet over,
    player needs to continue the game. If this causes a game to end, a corresponding Score entity will be created.

 - **get_all_game_history**
    - Path: 'history'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Game history(Scores) in the database (unordered).

 - **get_user_history**
    - Path: 'history/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms
    - Description: Returns all history(Scores) recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms
    - Description: Get an individual user's current games. Will raise a NotFoundException if there are no active games for the requested user.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel_game'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: Cancel a game in progress. Will raise a
    NotFoundException if the game can't be found.

 - **get_high_scores**
    - Path: 'scores/high_scores'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: Generate a list of high scores of won games in descending order.

 - **get_user_rankings**
    - Path: 'users/rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: Get the rankings of each player. Ordered by the winning percentage.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name)
 - **MakeMoveForm**
    - Inbound make move form (hand).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, game, message, player_hand, computer_hand, won)
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **UserForm**
    - Representation of a User's state (user_name, email, wins, total_games, win_percentage)

# How to install and run the code

## Installation

I have used `poetry` for dependency specification, but also exported to `requirements.txt` for portability.

1. Set up a virtual environment (I wrote the code using Python 3.8):

  `python3 -m venv venv`

2. Activate the virtual environment (assuming MacOS):

  `. venv/bin/activate`

3. Install dependencies:

  `pip install -r requirements.txt`

## Run the application

The application is written using `flask` and I have included a script to launch:

`python app.py`

This will launch a development server at `http://localhost:5000`

# Design Notes

I chose to implement the API using `flask`, `flask-sqlalchemy`, and `flask-smorest`.
This is primarily due to my familiarity.
The API docs are at `/api/docs`.

Additionally, I was unsure of whether the task included the UI or not, so I spun up a simple  `Dash` app.
One of the challenges with `Dash` is that it can get a bit messy and I usually end up refactoring
and building my own abstractions when things get complex (as in with multiple pages, etc.).
I was able to build a fun little application which allows gameplay, and also display of historical statistics.
With a bit more time, this part of the code could definitely use some refactoring.

After coding against the API, I would likely re-visit my choice of data type for representing the board state.
While a string is convenient for database storage, I would likely replace the API schema to represent the board as a list of strings, or as a more grid-like structure.
This would make consumption easier, and conversion between the string and the list would be handled with a custom serializer.

I also had thoughts of being clever to minimize database storage volume, but felt it would be a bit obscure and not very readable.
In any case, two potential ideas come to mind, both involving storing the board state as an integer and using bit-wise operations:

1. We have three states, 0, 1, 2 representing `NULL`, `X`, `O`.
   We could represent these in binary using two bits: `0b00`, `0b01`, `0b10`.
   Thus, you could represent the nine cells using 18 bits and extract the values using bit masking.
   For this, you'd need a 32-bit integer, as a 16-bit integer is too small.
2. However, since there are only three states, and since `3^9 < 2^16`, you could actually represent the board using a 16 bit integer by interpreting it as base 3.
   Unfortunately (since it'd be fun), despite the marginal savings in storage, both of these options
   are likely to anger your stakeholders (and colleagues), and should be avoided at all costs!

Thanks for the fun challenge! -MRK

P.S. This work is original, assuming reading package API docs is okay.
In any case, I hope you get a sense for my style and capabilities.
I am definitely interested in building my skills up further in this area.

# Anaconda: Tic-Tac-Toe Coding Challenge
Your mission, should you choose to accept it, is to implement a two-player game of Tic-tac-toe in the web browser.

## Rules

HONOR RULES: You must do this challenge on your own, without assistance or review from others, and without copying from the Internet. You will be asked to affirm that you developed your work independently.

TIME LIMIT: You have 3 days from the date you receive a link to this site. You may submit your work earlier.

TASK: Your task it implement a simple but comprehensive REST API for a [tic-tac-toe game](https://en.wikipedia.org/wiki/Tic-tac-toe)

## Requirements

The basic requirements for the game are:

store a game board data structure that contains the game information
allow two players to enter their names, and automatically assign one of them the circle and the other the 'x'allow each to play a turn, one at a time, during which the player selects a square of the board and it is filled in with their symbol
indicate when one of the players has won, or the game is a draw
In addition to implementing basic gameplay, the user must be able to save their game to the server.

Since this is a coding challenge, the success of your mission depends on building a good rest API implementation.

Make sure to provide instruction about how to setup, run and consume your REST API.

## Technologies

You can use any REST framework you prefer to implement the API (Flask, Tornado, etc.)

Game data structure
A game consists of:

two players, represented by their names as strings
a board data structure (we are leaving you the choice of what data structure is more appropriate for the task). Keep in mind that this data structure needs to trak the status of each board element. Each element is null if the square is blank, or either 0 or 1 to indicate which player controls the square.

Server API
The server should complies with the JSON API specification.

- `GET /api/games`: Return a list of the Games known to the server, as JSON.


- `POST /api/games`: Create a new `Game`, assigning it an ID and returning the newly created `Game`.

- `GET /api/games/<id>`: Retrieve a `Game` by its ID, returning a `404` status
  code if no game with that ID exists.

- `POST /api/games/<id>`: Update the `Game` with the given ID, replacing its data with the newly `POST`ed data.

## Optional

If you have extra time and want to take on an additional challenge, you may choose to implement:

 - viewing & restoring saved games
 - an "AI" player option, where someone can play against the computer

However, please be aware that we'd prefer a more polished implementation to more features!

## Submission

When you are ready, please submit your challenge as a pull request
against this repository.

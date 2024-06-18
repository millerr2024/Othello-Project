from app import app, sock
from flask import render_template, jsonify, abort
from othelloEngine import *
import psycopg2  # type: ignore
import json
from flask import Flask, jsonify
import requests
# from ai.ai import AITurn
import sys
import time

DB_ON = True
DB_NAME = "login"
DB_USER = "webapp"
DB_PASSWORD = "dbPass"
DB_HOST = "database"
DB_PORT = "5432"

gameDict = {}


# Dictionary of Web Sockets
# The dictionary key is a pair (gameID, playerID)
# ... the dictionary value is a WebSocket object for that game/player pair
web_sockets = {}


@sock.route("/sockStartGame/<gameID>/<playerID>")
def sockStartGame(ws, gameID, playerID):
    gameID = int(gameID)
    playerID = str(playerID)
    global web_sockets
    print("Websocket Opened for startGame! gameID: " + str(gameID) +
          " playerID: " + str(playerID) + "\n", file=sys.stderr)
    web_sockets[(gameID, playerID)] = ws
    while True:
        time.sleep(10)
    return ""


@sock.route("/sockJoinGame/<gameID>/<playerID>")
def sockJoinGame(ws, gameID, playerID):
    gameID = int(gameID)
    playerID = str(playerID)
    global web_sockets
    print("Websocket Opened for joinGame! gameID: " + str(gameID) +
          " playerID: " + str(playerID) + "\n", file=sys.stderr)

    if gameID not in gameDict or gameDict[gameID]['status'] != 'notYetStarted':
        print("Error, tried to join game that isn't notYetStarted", file=sys.stderr)
        abort(404)  # Not sure if this is the right thing to return

    # TODO: Make these changes in the DB as well --- THINK this is done
    gameInfo = gameDict[gameID]
    gameInfo['status'] = "inProgress"
    # TODO: Change this depending on which player is which color
    gameInfo['W'] = playerID
    gameDict[gameID] = gameInfo

    if DB_ON:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        with conn.cursor() as cursor:
            gameIDstr = str(gameID)
            gameJSON = json.dumps(gameInfo)
            cursor.execute(
                "UPDATE gameInfo SET gameJSON = %s WHERE gameID = %s", (gameJSON, gameIDstr))
        conn.commit()
        conn.close()

    web_sockets[(gameID, playerID)] = ws
    notify_sockets(gameID, "GameStarted")

    while True:
        time.sleep(10)
    return ""


@app.route("/startGame/<playerID>/<gameType>")
def startGame(playerID, gameType):
    playerID = str(playerID)
    gameType = str(gameType)

    # gameType must be one of these strings!
    if gameType not in ['ai', 'ai2', 'multiplayer']:
        print('Error, invalid game type', file=sys.stderr)

    # Get the next available gameID
    if DB_ON:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # Get the next value from the sequence for the game ID
        with conn.cursor() as cursor:
            cursor.execute("SELECT nextval('game_id_sequence');")
            gameID = cursor.fetchone()[0]

    else:
        gameID = len(gameDict) + 1

    # Instantiate board variables.
    boardString = start_board()
    board = string_to_array(boardString)
    legalMoves = get_possible_moves(board, "B")
    flips = []
    lastMove = ()
    status = ''
    opponentID = ''

    if gameType == 'ai' or gameType == 'ai2':
        status = 'inProgress'
        opponentID = gameType
        gameType = 'ai'
    elif gameType == 'multiplayer':
        status = 'notYetStarted'
        opponentID = None

    # TODO: Change this to determine which player plays which color. (Random assignment?)
    whitePlayerID = opponentID
    blackPlayerID = playerID

    gameJSON = {
        "gameID": gameID,
        "board": boardString,
        "W": whitePlayerID,
        "B": blackPlayerID,
        "legalMoves": legalMoves,
        "turn": "B",
        "flips": flips,
        "lastMove": lastMove,
        "status": status
    }

    # Store the board info as JSON in the DB
    jDumps = json.dumps(gameJSON)
    if DB_ON:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO gameInfo (gameID, gameJSON, blackPlayerID, whitePlayerID) VALUES (%s, %s, %s, %s)",
                           (gameID, jDumps, blackPlayerID, whitePlayerID))
        conn.commit()
        # Close the database connection
        conn.close()

    # Store the board info as a dictionary in the server dict
    gameDict[gameID] = gameJSON

    # Return JSON to the player who started the game (possibly remove)
    return gameJSON


@app.route("/playMove/<gameID>/<playerID>/<move>")
def playMove(gameID, playerID, move):
    # Parameter type formatting
    gameID = int(gameID)
    playerID = str(playerID)
    move = str(move)
    move_row = int(move[0])
    move_col = int(move[1])

    # Fetch the game state using the gameID from wherever it's stored (DB or dictionary)
    if DB_ON:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            with conn.cursor() as cursor:
                gameIDstr = str(gameID)
                cursor.execute(
                    "SELECT * FROM gameInfo WHERE gameID = %s;", gameIDstr)
                response = cursor.fetchone()
                if response != None:
                    print(response[0], file=sys.stderr)
                    gameInfo = response[1]
        except:
            print("Error with getting game info from DB, using dict.", file=sys.stderr)
            gameInfo = gameDict[gameID]
    else:
        # For gameInfo in the server dictionary
        gameInfo = gameDict[gameID]

    # check which color this player is
    if gameInfo["W"] == playerID:
        playerColor = "W"
        opponentColor = "B"
    elif gameInfo["B"] == playerID:
        playerColor = "B"
        opponentColor = "W"
    else:
        print("PLAYER COLOR ERROR", file=sys.stderr)

    board = string_to_array(gameInfo["board"])
    if move == "99":
        # PASS, no replacement, no flips
        flips = []
        print("Successfully passed!", file=sys.stderr)
    else:
        # Legal move, replace piece, calculate flips, and update board
        print("Move = ", move)
        board = replace_at_coord(board, playerColor, move_row, move_col)
        flips = get_flips(board, move_row, move_col)
        board = flip_pieces(board, flips)
        gameInfo["board"] = array_to_string(board)

    gameInfo["lastMove"] = (move_row, move_col)
    gameInfo["flips"] = flips

    # UPDATE WHOSE TURN IT IS
    gameInfo["turn"] = opponentColor
    # calculate and UPDATE LEGAL MOVES
    possible = get_possible_moves(board, opponentColor)
    legalMoves = get_best_move(possible, board, opponentColor)
    gameInfo["legalMoves"] = legalMoves

    # store the game state stuff again
    if DB_ON:
        with conn.cursor() as cursor:
            gameIDstr = str(gameID)
            gameJSON = json.dumps(gameInfo)
            cursor.execute(
                "UPDATE gameInfo SET gameJSON = %s WHERE gameID = %s", (gameJSON, gameID))
        conn.commit()
        # conn.close()

    gameDict[gameID] = gameInfo

    # Send the update message to both players
    notify_sockets(gameID, "Update")

    # CHECK FOR endgame conditions (full board/win). if a win, go to the endgame endpoint. if not, carry on below
    winner = is_endgame(board)
    # print("Is end game: ", winner, file=sys.stderr)
    if winner != "0":
        print(winner, "has won the game!", file=sys.stderr)
        gameInfo["status"] = winner
        gameDict[gameID] = gameInfo
        if DB_ON:
            with conn.cursor() as cursor:
                gameIDstr = str(gameID)
                gameJSON = json.dumps(gameInfo)
                cursor.execute(
                    "UPDATE gameInfo SET gameJSON = %s WHERE gameID = %s", (gameJSON, gameIDstr))
            conn.commit()
            conn.close()
        return gameInfo

    currTurn = gameInfo[gameInfo["turn"]]
    if currTurn == "ai" or currTurn == "ai2":
        print("Calling the AI!", file=sys.stderr)
        ai_url = "http://ai:5000/aiTurn/" + str(gameID)
        response = requests.get(ai_url)
        aiMove = response.text
        print("THE AI RESPONDED WITH:", aiMove, file=sys.stderr)
        time.sleep(1)
        return playMove(gameID, currTurn, aiMove)

    # print_board(string_to_array(gameInfo[board]))
    return gameInfo

@app.route("/emoji/<gameID>/<playerID>/<reaction>")
def emoji(gameID, playerID, reaction):
    notifyString = str(playerID) + "!" + str(reaction)
    notify_sockets(int(gameID), notifyString)
    return {"status": "sucess"}

@app.route("/endGame/<gameID>")
def endGame(gameID):
    gameID = int(gameID)
    if DB_ON:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT gameJSON FROM gameInfo WHERE gameID = %s;", (gameID,))
                response = cursor.fetchone()
                if response:
                    gameInfo = json.loads(response[0])
                else:
                    return {"error": "Game not found"}, 404
        except Exception as e:
            # print(f"Error fetching game info from DB: {e}", file=sys.stderr)
            return {"error": "Database error"}, 500
    else:
        # For gameInfo in the server dictionary
        gameInfo = gameDict.get(gameID)
        if not gameInfo:
            return {"error": "Game not found"}, 404

    board = string_to_array(gameInfo["board"])
    winner = is_endgame(board)

    gameInfo["winner"] = winner

    # Update the database with the winner information
    if DB_ON:
        try:
            with conn.cursor() as cursor:
                gameJSON = json.dumps(gameInfo)
                cursor.execute(
                    "UPDATE gameInfo SET gameJSON = %s WHERE gameID = %s", (gameJSON, gameID))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating game info in DB: {e}", file=sys.stderr)
            return {"error": "Database error"}, 500
    else:
        # Update the server dictionary with the winner information
        gameDict[gameID] = gameInfo

    return {"gameID": gameID, "winner": winner}


@app.route("/fetchGameInfo/<gameID>")
def fetchGameInfo(gameID):
    gameInfo = {}
    # Fetch the game state using the gameID from wherever it's stored (DB or dictionary)
    if DB_ON:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            with conn.cursor() as cursor:
                gameIDstr = int(gameID)
                cursor.execute("SELECT * FROM gameInfo WHERE gameID = %s;", (gameIDstr,))
                response = cursor.fetchone()
                if response != None:
                    # print(response[0], file=sys.stderr)
                    gameInfo = response[1]
        except:
            print("Error with getting game info from DB, using dict.", file=sys.stderr)
            gameInfo = gameDict[gameID]
    # gameID = int(gameID)
    return jsonify(gameInfo)


# TODO: Add endpoint for fetching game history
@app.route("/fetchGameHistory/<playerID>")
def fetchGameHistory(playerID):
    gameArray = []
    if DB_ON:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM gameInfo WHERE blackPlayerID = %s OR whitePlayerID = %s;", (playerID, playerID))
                response = cursor.fetchall()
                if response != None:
                    print(response, file=sys.stderr)
                    gameArray = response
        except:
            print(
                "Error with getting game history  from DB... What do I do?", file=sys.stderr)
    else:
        print("DB is off right now... What do I do?", file=sys.stderr)
    return jsonify(gameArray)


def notify_sockets(gameToUpdate, message):
    global web_sockets

    for gameID, playerID in web_sockets:
        ws = web_sockets[(gameID, playerID)]
        if gameID == gameToUpdate:
            ws.send(message)

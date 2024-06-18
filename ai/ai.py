from flask import Flask, request
from flask import render_template, redirect, url_for
import requests
import random


app = Flask(__name__)

@app.route("/aiTurn/<gameID>")
def AITurn_2(gameID):
    server_url = f"http://gameserver:5000/fetchGameInfo/{gameID}"
    response = requests.get(server_url)
    gameInfo = response.json()
    legalMoves = gameInfo["legalMoves"]
    if len(legalMoves) == 0:
        moveString = "99"
    elif gameID == "ai2":
       chosenMove = legalMoves[0]
       moveString = str(chosenMove[0]) + str(chosenMove[1])
    else:
        chosenMove = random.choice(legalMoves)
        moveString = str(chosenMove[0]) + str(chosenMove[1])
    return moveString

if __name__ == '__main__':
    my_port = 5000
    app.run(host='0.0.0.0', port = my_port)
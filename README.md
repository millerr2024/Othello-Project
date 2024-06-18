<h2>Project Summary</h2>

This project allows a user to play Othello, also known as Reversi, in AI mode or multiplayer mode. AI mode has an easy and medium AI while multiplayer involves sending a code to a friend to play together. 

This project is hosted across three different docker containers: 

*  **gameserver:** Othello's frontend and game logic

*  **ai:** easy and medium level AIs

*  **database:** a PostgreSQL database which is backed up at /var/lib/postgresql

Created by Valentina Guerrero Chala, Evan Lauer, Avery Hall, Catherine Bregou, Mary Blanchard, and Rachel Miller for Carleton College's Advanced Software Design course.


<h2>Setup to Run Locally</h2>

In order to run this repository locally, follow these steps:

1. Clone the repository
2. Make a .env file in the **gameserver** directory:

```
       vi .env
```

3. Add the following line to the .env file, substituting **typeKeyHere** with a key of your choice:

```
      SECRET_KEY=typeKeyHere
```

4. Get the docker container up and running:

```
     docker compose build
   
     docker compose up
```
   
5. Navigate to http://localhost
   

<h2>Repository Contents and Structure</h2>

This reposity contains the following files and directories:
*  **gameserver:**
    -  **static:** CSS and Javascript files for all frontend featues
    -  **templates:** HTML files for all frontend features
    -  **othelloEngine.py:** Python code to play Othello
    -  **gameServer.py:** Flask endpoints related to playing Othello. Calls various functions in othelloEngine.py
    -  **login.py:** Flask endpoints related to user login, logout, and account creation
*  **database:**
    -  **db-setup.sql:** sets up the PostgreSQL database. See below for more details
*  **ai:**
    - **ai.py:** selects legal move for AI player
      

<h2>Database Structure</h2>

The PostgreSQL database, known as **login**, contains the following tables:

*  **userInfo:**
      -  **username** (TEXT)
      -  **pass** (TEXT)
      -  **date_joined** (TEXT)

*  **gameInfo:**
      - **gameID** (INT)
      - **gameJSON** (JSON)
      - **blackPlayerID** (TEXT)
      - **whitePlayerID** (TEXT)

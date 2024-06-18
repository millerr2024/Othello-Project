import $ from "https://cdn.skypack.dev/cash-dom";

var socket;
var legalMoves;
var playerID; // This is equal to username
var playerColor; //"B" or "W"
var opponentID; 
var gameID;

// Set global playerID variable according to URL
window.onload = (event) => {
  const urlParams = new URLSearchParams(window.location.search);
  playerID = urlParams.get("username");
};

// Add event listeners to all buttons
$(".playAgainstAIBtn").on("click", function (event) {
  $(".choose-your-opponent-container").hide();
  $(".choose-ai-container").css("display", "grid");
});

$(".easyAI").on("click", function (event) {
  $(".pop-up-container").hide();
  opponentID = "AI";
  fetchStartGame(playerID, "ai");
});

$(".mediumAI").on("click", function (event) {
  $(".pop-up-container").hide();
  opponentID = "AI";
  fetchStartGame(playerID, "ai2");
});

$(".multiplayerBtn").on("click", function (event) {
  $(".choose-your-opponent-container").hide();
  $(".multiplayer-container").css("display", "grid");
});

$(".createARoomBtn").on("click", () => {
  $(".multiplayer-container").hide();
  $(".create-a-room-container").css("display", "grid");
  fetchStartGame(playerID, "multiplayer");
});

$(".joinARoomBtn").on("click", () => {
  $(".multiplayer-container").hide();
  $(".join-a-room-container").css("display", "grid");
});

document.addEventListener("DOMContentLoaded", () => {
  const instructionsButton = document.querySelector("header a.instructions");
  const instructionsPopup = document.getElementById("instructionsPopup");
  const closeInstructionsPopup = document.getElementById("closeInstructionsPopup");

  instructionsButton.addEventListener("click", () => {
    instructionsPopup.style.display = "flex";
  });

  closeInstructionsPopup.addEventListener("click", () => {
    instructionsPopup.style.display = "none";
  });

  // Close the popup when clicking outside of it
  window.addEventListener("click", (event) => {
    if (event.target === instructionsPopup) {
      instructionsPopup.style.display = "none";
    }
  });
});

$(".play-again").on("click", () => {
  $(".game-over").hide();
  $(".choose-your-opponent-container").css("display", "grid");
  restartGame();
});

$(".joinGame").on("click", () => {
  // Grab code from input box and clean it to get rid of first three characters ('OTH')
  var gameCode = $('.code-text-input').prop('value').split("OTH");
  gameID = gameCode[1];
  console.log($('.code-text-input').prop('value'));
  openSocket(gameID, 'joinGame');
});

$(".copy-code").on("click", function (event) {
  var gameCode = $(".game-code").text();
  console.log(gameCode);
  navigator.clipboard.writeText(gameCode);
});

$(".pass").on("click", () => {
  console.log("user clicked pass");
  $(".pop-up-container").hide();
  playMove(9, 9);
});

$('.continue').on("click", () => {
  console.log("user clicked continue");
  $(".pop-up-container").hide();
});

$(".multiplayer-back-arrow").on("click", () => {
  $(".multiplayer-container").hide();
  $(".choose-your-opponent-container").css("display", "grid");
});

$(".create-room-back-arrow").on("click", () => {
  $(".create-a-room-container").hide();
  $(".multiplayer-container").css("display", "grid");
});

$(".join-room-back-arrow").on("click", () => {
  $(".join-a-room-container").hide();
  $(".multiplayer-container").css("display", "grid");
});

$(".choose-ai-back-arrow").on("click", () => {
  $(".choose-ai-container").hide();
  $(".choose-your-opponent-container").css("display", "grid");
});

$(".log-out").on("click", () => {
  const apiUrl = `/logout`;
    fetch(apiUrl)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (data["status"] == "success") {
          console.log("log out successfully");
          window.location.href = `/`;
        }
      });
});

$(".stats").on("click", () => {
  window.location.href = `/stats?username=${playerID}&profile=${playerID}`;  
});


// Add event listeners to all board squares to detect when user clicks on any of them
$(".board-square").on("click", function (event) {
  // The class of each square stores its coordinates in the following format: "p[x-coordinate][y-coordinate]"
  var classList = $(event.currentTarget).attr("class");
  var piece = classList.split(/\s+/)[1];
  var rowCoordinate = parseInt(piece[1]);
  var columnCoordinate = parseInt(piece[2]);

  // Check if the square selected by the user is a legal move
  if (
    legalMoves.find(
      (coordinates) =>
        coordinates[0] === rowCoordinate && coordinates[1] === columnCoordinate
    )
  ) {
    playMove(rowCoordinate, columnCoordinate);
  }
});

function flipPiece(rowCoordinate, columnCoordinate) {
  console.log("Flip piece", rowCoordinate, columnCoordinate);
  var piece = $(`.p${rowCoordinate}${columnCoordinate}`).find(".piece");

  piece.addClass("reverse");
  if (piece.hasClass("B")) {
    piece.removeClass("B");
    piece.addClass("W");
  } else if (piece.hasClass("W")) {
    piece.removeClass("W");
    piece.addClass("B");
  }
}

function addPiece(color, rowCoordinate, columnCoordinate) {
  var piece = $(`.p${rowCoordinate}${columnCoordinate}`).find(".piece");
  piece.addClass(`${color}`);
}

function updateGameStats(board) {
  var numberWhitePieces = board.match(/W/g).length;
  // TODO: Check if match does not return null... if it does, set legth to 0

  var numberWhitePieces = board.match(/W/g).length;
  var numberBlackPieces = board.match(/B/g).length;
  if (playerColor == "W") {
    $(".num-player-pieces").text(`${numberWhitePieces}`);
    $(".num-opponent-pieces").text(`${numberBlackPieces}`);
  }
  if (playerColor == "B") {
    $(".num-player-pieces").text(`${numberBlackPieces}`);
    $(".num-opponent-pieces").text(`${numberWhitePieces}`);
  }
}

function removeLegalMoves() {
  for (let coordinates in legalMoves) {
    var square = $(
      `.p${legalMoves[coordinates][0]}${legalMoves[coordinates][1]}`
    );
    square.removeClass("legal-move");
  }
  legalMoves = []; // Reset legalMoves
}

function addLegalMoves() {
  for (let coordinates in legalMoves) {
    var square = $(
      `.p${legalMoves[coordinates][0]}${legalMoves[coordinates][1]}`
    );
    square.addClass("legal-move");
  }
}

function updateTurn(currentPlayerID) {
  if (currentPlayerID == playerID) {
    $(".player-id").addClass("turn");
    $(".player-piece-stats").addClass("stats-turn");
    $(".opponent-id").removeClass("turn");
    $(".opponent-piece-stats").removeClass("stats-turn");
  } else {
    $(".opponent-id").addClass("turn");
    $(".opponent-piece-stats").addClass("stats-turn");
    $(".player-id").removeClass("turn");
    $(".player-piece-stats").removeClass("stats-turn");
  }
}

function displayGameOver(winner){
  console.log("status:", winner);
  
  // Display game over container, hide all other unnecessary containers
  $(".pop-up-container").css('display', 'flex');
  $(".pop-up-div").css('display', 'flex');
  $(".choose-ai-container").hide();
  $('.game-over').css('display', 'flex');

  // updateBoard() displays this div when game is over
  // However we still need to execute all the other functions of updateBoard(), which is why it's just easier to hide this div
  $(".no-legal-moves-div").hide();
  $(".no-legal-moves-opponent-div").hide();

  // Display message depending on who won
  if(winner == 'T'){
    $('.game-over-text').text('It is a tie');
  }
  else if(winner == playerColor){
    $('.game-over-text').text('You won!');
  }
  else if(winner != playerColor){
    $('.game-over-text').text('You lost');
  }
}

function fetchStartGame(playerID, gameType) {
  const apiUrl = `/startGame/${playerID}/${gameType}`;
  fetch(apiUrl)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log("debug", data)
      if(gameType == 'multiplayer'){
        $(".game-code").text(`OTH${data['gameID']}`);
      }
      startGame(data);
      return gameID;
    })
    .then((gameID) => {
      openSocket(gameID, 'startGame');
    })
}


function restartGame(){
  // Reset all global variables except for playerID 
  socket = '';
  legalMoves = [];
  playerColor = ''; 
  opponentID = ''; 
  gameID = '';

  // Remove all pieces from board 
  for (let row = 0; row <= 7; row++) {
    for (let column = 0; column <= 7; column++) {
      $(`.p${row}${column}`).children().removeClass("B");
      $(`.p${row}${column}`).children().removeClass("W");
      console.log($(`.p${row}${column}`).children());
    }
  }

}

function startGame(data){

  gameID = data["gameID"];

  // Set opponentID and update game stats to reflect who is playing black and who is playing white and 
  if (data["W"] == playerID) {
    playerColor = "W";
    opponentID = data["B"];
    $(".opponent-piece-stats").addClass("piece-stats-black");
    $(".player-piece-stats").addClass("piece-stats-white");
  } else {
    playerColor = "B";
    opponentID = data["W"];
  }

  // Update players's IDs on the board
  $(".opponent-id").text(opponentID);
  $(".player-id").text(`${playerID}`);

  // Add the first four pieces to the board
  addPiece("W", 3, 3);
  addPiece("W", 4, 4);
  addPiece("B", 3, 4);
  addPiece("B", 4, 3);

  // If it's player's turn add legal moves to the board
  if (data["turn"] == playerColor) {
    updateTurn(playerID);
    legalMoves = data["legalMoves"];
    addLegalMoves();
  }

  updateGameStats(data["board"]);
}

function playMove(rowCoordinate, columnCoordinate) {
  addPiece(playerColor, rowCoordinate, columnCoordinate);
  removeLegalMoves();

  const apiUrl = `/playMove/${gameID}/${playerID}/${rowCoordinate}${columnCoordinate}`;
  fetch(apiUrl)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log("playMove", data);
    })
}

function fetchUpdate() {
  const apiUrl = `/fetchGameInfo/${gameID}`;
  return fetch(apiUrl)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log("fetch update", data)
      updateBoard(data);
      return data;
    })
}

function emojiReaction(data)
{
  let sender = data.split("!")[0];
  let emoji = data.split("!")[1];
  if (sender != playerID)
  {
    if (emoji == "sad")
    {
      var element = document.getElementById("sadEmojiOp");
      element.classList.add("emoji-style");
      setTimeout(removeEmoji, 3000, "sadEmojiOp");
    }
    else if (emoji == "mad")
    {
      var element = document.getElementById("madEmojiOp");
      element.classList.add("emoji-style");
      setTimeout(removeEmoji, 3000, "madEmojiOp");
    }
    else if (emoji == "happy")
    {
      var element = document.getElementById("happyEmojiOp");
      element.classList.add("emoji-style");
      setTimeout(removeEmoji, 3000, "happyEmojiOp");
    }
    else
    {
      var element = document.getElementById("sleepyEmojiOp");
      element.classList.add("emoji-style");
      setTimeout(removeEmoji, 3000, "sleepyEmojiOp");
    }
  }
  else
  {
    if (emoji == "sad")
      {
        var element = document.getElementById("sadEmojiPlayer");
        element.classList.add("emoji-style");
        setTimeout(removeEmoji, 3000, "sadEmojiPlayer");
      }
      else if (emoji == "mad")
      {
        var element = document.getElementById("madEmojiPlayer");
        element.classList.add("emoji-style");
        setTimeout(removeEmoji, 3000, "madEmojiPlayer");
      }
      else if (emoji == "happy")
      {
        var element = document.getElementById("happyEmojiPlayer");
        element.classList.add("emoji-style");
        setTimeout(removeEmoji, 3000, "happyEmojiPlayer");
      }
      else
      {
        var element = document.getElementById("sleepyEmojiPlayer");
        element.classList.add("emoji-style");
        setTimeout(removeEmoji, 3000, "sleepyEmojiPlayer");
      }
  }
}

function removeEmoji(elementID)
{
  var element = document.getElementById(elementID);
  element.classList.remove("emoji-style"); 
}

function updateBoard(data) {

  // Opponent just played: add previous move, flip pieces, add new legal moves
  if (data["turn"] == playerColor) {
    console.log("opponent just played");

    // Opponent passed because there were no legal moves left
    if(data["lastMove"][0]== 9 && data["lastMove"][1]== 9 && data['status'] == "inProgress" ){
      console.log("Opponent just passed");
      $(".pop-up-container").show();
      $(".pop-up-div").hide();
      $('.no-legal-moves-opponent-div').css("display","flex");
    }

    // Add opponent last move to the board
    else{
      if (playerColor === "W") {
        addPiece("B", data["lastMove"][0], data["lastMove"][1]);
      } else {
        addPiece("W", data["lastMove"][0], data["lastMove"][1]);
      }
    }

    // Flip all pieces that opponent last move just flipped
    for (let flippedPieces in data["flips"]) {
      flipPiece(
        data["flips"][flippedPieces][0],
        data["flips"][flippedPieces][1]
      );
    }

    removeLegalMoves();
    legalMoves = data["legalMoves"];
    addLegalMoves();

    // There are no legal moves for user, display corresponding container
    if (legalMoves.length == 0 && data['status'] == "inProgress") {
      console.log("No legal moves");
      $(".pop-up-container").show();
      $(".pop-up-div").hide();
      $(".no-legal-moves-div").css("display","flex");
    }

    updateTurn(playerID);
  }

  // Player just played: flip pieces
  if (data["turn"] != playerColor) {
    for (let flippedPieces in data["flips"]) {
      flipPiece(
        data["flips"][flippedPieces][0],
        data["flips"][flippedPieces][1]
      );
    }
    updateTurn(opponentID);
  }

  // Count # of white and black pieces on the board
  updateGameStats(data["board"]);

  // If game has ended, display corresponding message
  if(data['status'] != 'inProgress' && data['status'] != 'notYetStarted'){
    setTimeout(() => {
      displayGameOver(data['status']) // The delay allows the user to see all the flipped pieces
    }, 1500);
  }
}

function openSocket(gameID, actionType) {
  if (actionType == "joinGame"){
    socket = new WebSocket(
      `ws://${location.host}/sockJoinGame/${gameID}/${playerID}`
    );
  }
  else if(actionType = "startGame"){
    socket = new WebSocket(
      `ws://${location.host}/sockStartGame/${gameID}/${playerID}`
    );
  }
  // Fetch a new update whenever the socket receives a message
  socket.onmessage = function (event) {
    if(event.data == "GameStarted"){
      // Close all pop ups
      $(".join-a-room-container").hide();
      $(".create-a-room-container").hide();
      $(".pop-up-container").hide();
      // Start game
      fetchUpdate().then(data => startGame(data));
    }
    else if (event.data == "Update"){
      fetchUpdate();
    }
    else{
      emojiReaction(event.data);
    }

  };
}

$(".emojiButtonHappy").on("click", () => {
  const apiUrl = ('/emoji/' + gameID + '/' + playerID + '/happy');
  fetch(apiUrl);
});

$(".emojiButtonSad").on("click", () => {
  const apiUrl = ('/emoji/' + gameID + '/' + playerID + '/sad');
  fetch(apiUrl);
});

$(".emojiButtonMad").on("click", () => {
  const apiUrl = ('/emoji/' + gameID + '/' + playerID + '/mad');
  fetch(apiUrl);
});

$(".emojiButtonSleepy").on("click", () => {
  const apiUrl = ('/emoji/' + gameID + '/' + playerID + '/sleepy');
  fetch(apiUrl);
});

// Check fetch update and sockJoinGame (something like startGame)
// Change motion for buttons in CSS - change color
// Reset the board (?) when user hits play again in game over div

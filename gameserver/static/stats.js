import $ from "https://cdn.skypack.dev/cash-dom";

var socket;
var legalMoves;
var playerID;
var playerColor;
var opponentID;
var gameID;
var profileID;

const urlParams = new URLSearchParams(window.location.search);
playerID = urlParams.get('username');
profileID = urlParams.get('profile')

$(".log-out").on("click", () => {
  const apiUrl = `/logout`;
  fetch(apiUrl)
    .then((response) => {
      if (response.status === 404) {
        console.log("log out error");
      }
      return response.json();
    })
    .then((data) => {
      if (data["status"] == "success"){
        console.log("log out successfully");
        window.location.href = `/`;
      }
    })
});

$(".play").on("click", () => {
  window.location.href = `/board?username=${playerID}`;
});


$(document).ready(async ()=>{
  const apiUrl = `/fetchGameHistory/${profileID}`
  const response = await fetch(apiUrl)
  const data = await response.json();

  // Filter out games that haven't finished (or quit early, etc.)
  const finishedGames = data.filter((game)=>{
    return game[1].status === "B" || game[1].status === "W" || game[1].status === "Tie"
  })
  
  const wonGames = finishedGames.filter((game)=>{
    if (game[1].B === profileID) { // Player was black
      return game[1].status === "B";
    } else { // Player was white
      return game[1].status === "W";
    }
  });

  var playerTotalScore = 0;
  var opponentsTotalScore = 0;

   finishedGames.forEach((game)=>{
    const playerColor = game[1].W === profileID ? "W" : "B";
    const gameBoardArr = game[1].board.split("");
    playerTotalScore += gameBoardArr.filter((ch)=>{return ch===playerColor}).length
    opponentsTotalScore += gameBoardArr.filter((ch)=>{return ch!==playerColor && (ch==='W' || ch==='B')}).length
  });
 
  const avgScoreDiff = finishedGames.length === 0 ? "0" : String(Math.round(((playerTotalScore - opponentsTotalScore)/finishedGames.length) * 10) / 10);
  const avgPoints = finishedGames.length === 0 ? "0" : String(Math.round((playerTotalScore / finishedGames.length) * 10) / 10);
  
  document.getElementById('player-id').innerHTML = profileID;
  document.getElementById('games-played').innerHTML = finishedGames.length;
  document.getElementById('games-won').innerHTML = wonGames.length;
  document.getElementById('win-rate').innerHTML = String(Math.floor((wonGames.length / finishedGames.length) * 100)) + '%';
  document.getElementById('score-diff').innerHTML = avgScoreDiff;
  document.getElementById('avg-points').innerHTML = avgPoints;
  document.getElementById('total-score').innerHTML = playerTotalScore;

  finishedGames.forEach((game) => {
    const gameBoardArr = game[1].board.split("");
    const whiteScore = gameBoardArr.filter((ch)=>{return ch==="W"}).length;
    const blackScore = gameBoardArr.filter((ch)=>{return ch==="B"}).length;
    const whiteClass = game[1].W === profileID ? "player" : "";
    const blackClass = game[1].B === profileID ? "player" : "";
    const playerColor = game[1].B === profileID ? "B" : "W";
    const resultText = game[1].status !== "Tie" ? (game[1].status === playerColor ? "W" : "L") : "T";
    const whitePlayerHTML = playerColor === "W" ? game[1].W : `<a href="/stats?username=${playerID}&profile=${game[1].W}">${game[1].W}</a>`
    const blackPlayerHTML = playerColor === "B" ? game[1].B : `<a href="/stats?username=${playerID}&profile=${game[1].B}">${game[1].B}</a>`
    $(`
    <div id="game${game[0]}" class="gameEntry">
      <div class="gameStat result ${resultText}">${resultText}</div>
      <div class="gameStat whitePlayer ${whiteClass}">${whitePlayerHTML}</div>
      <div class="gameStat whiteScore">${whiteScore}</div>
      <div class="dash">-</div>
      <div class="gameStat blackScore">${blackScore}</div>
      <div class="gameStat blackPlayer ${blackClass}">${blackPlayerHTML}</div>
      <div class="gameStat result"></div>
    </div>`).appendTo("#game-history-container");
  })
})

// TODO: Write a method that gets all games of a user


// Fetch end of game endpoint
// Implement choose AI

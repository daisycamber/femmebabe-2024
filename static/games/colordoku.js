  // By Jasper Camber Holton. V1.2.811
(function colordoku(){

  let seed = Math.floor(Math.random() * 5000);

  function RNG(seed) {
    // LCG using GCC's constants
    this.m = 0x80000000; // 2**31;
    this.a = 1103515245;
    this.c = 12345;
    this.state = seed ? seed : Math.floor(Math.random() * (this.m - 1));
  }
  RNG.prototype.nextInt = function() {
    this.state = (this.a * this.state + this.c) % this.m;
    return this.state;
  }
  RNG.prototype.nextFloat = function() {
    // returns in range [0,1]
    return this.nextInt() / (this.m - 1);
  }
  RNG.prototype.nextRange = function(start, end) {
    // returns in range [start, end): including start, excluding end
    // can't modulu nextInt because of weak randomness in lower bits
    let rangeSize = end - start;
    let randomUnder1 = this.nextInt() / this.m;
    return start + Math.floor(randomUnder1 * rangeSize);
  }
  RNG.prototype.choice = function(array) {
    return array[this.nextRange(0, array.length)];
  }
  let rng = new RNG(seed);
  let canvasid = "game197";
  let canvas = document.getElementById(canvasid);
  let width = canvas.width;
  if(window.innerHeight < width) width = window.innerHeight - 200;
  canvas.width = width;
  canvas.height = width;
  let height = canvas.height;
  let ADHEIGHT = 0;
  let less = width;
  if (height < less) {
    less = height - ADHEIGHT;
  }
  let TEXTTYPE = "bold " + 42 + "px Arial";
  let last = 0;
  let stage = new createjs.Stage(canvasid);
  let container = new createjs.Container();
  scale = container.scale = less / 1000;
  background = new createjs.Shape();
  background.graphics.beginFill("#b0afb3").drawRect(0, 0, 1000, 1000); //
  stage.addChild(background);
  stage.addChild(container);
  leftbound = ((width - less) / 3 / scale);
  topbound = (((height - less) / 20) / scale)-10;
  // red, orange, yellow, dark green, light green, dark blue, light blue, dark purple, pink
  let colors = ["#f50521", "#fa8907", "#fafa07", "#2e8008", "#33f707", "#214bcc", "#07eef2", "#9b5bf0", "#fa75e6", "grey"];
  let selectorBallOffset = 5;
  let ballSize = 37;
  let selectorBall = new createjs.Shape();
  selectorBall.graphics.beginFill("white").drawCircle(0, 0, ballSize + 7);
  selectorBall.x = leftbound + 100 + 800 / 20 + selectorBallOffset;
  selectorBall.y = topbound + 900 + 800 / 18 / 2;
  container.addChild(selectorBall)
  let selectedBall = 0;
  let selectorBalls = [];
  let text;
  let text2;
  let hints = 0;
  for (let i = 0; i < 10; i++) {
    selectorBalls[i] = new createjs.Shape();
    selectorBalls[i].graphics.beginFill(colors[i]).drawCircle(0, 0, ballSize);
    selectorBalls[i].x = leftbound + 100 + 800 / 10 * i + 800 / 20 + selectorBallOffset;
    selectorBalls[i].y = topbound + 900 + 800 / 18 / 2;
    selectorBalls[i].index = i
    selectorBalls[i].on("mousedown", function(event) {
      let balls = game1.get_available_balls();
      if(balls[event.target.index + 1] || (hints > 0 && event.target.index == 9)){
        selectorBall.x = event.target.x;
        selectedBall = event.target.index
      }
    });
    if (i == 9) {
      //text = new createjs.Text("\u21ba", TEXTTYPE, "#000000")
      text2 = new createjs.Text("?", TEXTTYPE, "#000000")
      text2.x = selectorBalls[i].x - 13;
      text2.y = selectorBalls[i].y - 20;
    }
    container.addChild(selectorBalls[i])
  }
  container.addChild(text2)

  // Sudoku game class
  class Sudoku {
    constructor() {
      this.board = this.blank_board_array();
      this.ogboard = this.blank_board_array();
    }
    blank_board_array() {
      return [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
      ];
    }
    // I can't figure out how to get this working with the "set" keyword, so making a method for now
    set_board(board_string, completed_board_string) {
      this.board = this.blank_board_array();
      this.completedboard = this.blank_board_array();
      this.ogboard = this.blank_board_array();
      for (let row = 0; row <= 8; row++) {
        for (let column = 0; column <= 8; column++) {
          this.completedboard[row][column] = completed_board_string.charAt(row * 9 + column);
          this.board[row][column] = board_string.charAt(row * 9 + column);
          this.ogboard[row][column] = board_string.charAt(row * 9 + column);
        }
      }
    }

    get_board_array() {
      return this.board;
    }

    get_cell(row, col) {
      return this.board[row][col];
    }

    get_completed_cell(row, col) {
      return this.completedboard[row][col];
    }

    get_available_balls() {
      let balls = [];
      let ballCounts = [];
      for (let i = 0; i < 10; i++) {
        ballCounts[i] = 0;
      }
      for (let x = 0; x < 9; x++) {
        for (let y = 0; y < 9; y++) {
          ballCounts[this.board[x][y]]++;
        }
      }
      for (let i = 1; i < 10; i++) {
        balls[i] = true;
        if (ballCounts[i] == 9) {
          balls[i] = false;
        }
      }
      return balls;
    }

    make_move(row, col, value) {
      this.board[row][col] = value;
      let willDropConfetti = true;
      for (let x = 0; x < 9; x++) {
        for (let y = 0; y < 9; y++) {
          if (this.board[x][y] == 0) {
            willDropConfetti = false;
          }
        }
      }
      if (willDropConfetti && !isFinished) {
        isFinished = true;
        wonGame();
        dropConfetti();
      }
    }

    is_legal_move(row, col, value) {

      if (this.ogboard[row][col] > 0) {
        return false;
      }
      if (value == 10) {
        return true;
      }

      if (this.completedboard[row][col] == value) {
        return true;
      }
      return false;

      // check for non numbers
      // weird that JS match function doesn't put quotes around regex
      // check row

      for (let i = 0; i <= 8; i++) {
        if (value == this.board[row][i]) {
          return false;
        }
      }

      // check column
      for (let i = 0; i <= 8; i++) {
        if (value == this.board[i][col]) {
          return false;
        }
      }
      // check 3x3 grid
      let row_offset = Math.floor(row / 3) * 3;
      let col_offset = Math.floor(col / 3) * 3;
      for (let i = 0 + row_offset; i <= 2 + row_offset; i++) {
        for (let j = 0 + col_offset; j <= 2 + col_offset; j++) {
          if (value == this.board[i][j]) {
            return false;
          }
        }
      }


      return true;
    }
  };

  line1 = new createjs.Shape();
  line1.graphics.beginFill("grey").drawRect(0, 0, 800, 5);
  line1.x = leftbound + 100 * 1;
  line1.y = topbound + 100 + 645 / 3;
  container.addChild(line1)

  line2 = new createjs.Shape();
  line2.graphics.beginFill("grey").drawRect(0, 0, 800, 5);
  line2.x = leftbound + 100 * 1;
  line2.y = topbound + 582;
  container.addChild(line2)

  line3 = new createjs.Shape();
  line3.graphics.beginFill("grey").drawRect(0, 0, 5, 800);
  line3.x = leftbound + 148 + 645 / 3;
  line3.y = topbound + 50;
  container.addChild(line3)

  line4 = new createjs.Shape();
  line4.graphics.beginFill("grey").drawRect(0, 0, 5, 800);
  line4.x = leftbound + 630;
  line4.y = topbound + 50;
  container.addChild(line4)
  line5 = new createjs.Shape();
  line5.graphics.beginFill("grey").drawRect(0, 0, 5, 800);
  line5.x = leftbound + 100 * 1;
  line5.y = topbound + 50;
  container.addChild(line5)

  line8 = new createjs.Shape();
  line8.graphics.beginFill("grey").drawRect(0, 0, 5, 800);
  line8.x = leftbound + 100 * 1 + 800;
  line8.y = topbound + 50;
  container.addChild(line8)

  line6 = new createjs.Shape();
  line6.graphics.beginFill("grey").drawRect(0, 0, 800, 5);
  line6.x = leftbound + 100;
  line6.y = topbound + 50;
  container.addChild(line6)

  line7 = new createjs.Shape();
  line7.graphics.beginFill("grey").drawRect(0, 0, 800, 5);
  line7.x = leftbound + 100;
  line7.y = topbound + 50 + 800;
  container.addChild(line7)

  let game1 = new Sudoku();

  let rand = rng.nextRange(0, 399);
  let import_string = games[rand * 2];
  let completed_import_string = games[rand * 2 + 1];
  game1.set_board(completed_import_string, completed_import_string);
  let sudoku_squares = createArray(9, 9);
  let balls = [];
  for (let i = 0; i < 9; i++) {
    balls[i] = [];
    for (let j = 0; j < 9; j++) {
      balls[i][j] = new createjs.Shape();
      balls[i][j].graphics.beginFill("white").drawCircle(0, 0, ballSize); //
      balls[i][j].x = leftbound + 100 + 800 / 9 * i + 800 / 18;
      balls[i][j].y = topbound + 50 + 800 / 9 * j + 800 / 18;
      balls[i][j].row = j;
      balls[i][j].col = i;
      balls[i][j].on("mousedown", function(evt) {
        if (!game1.is_legal_move(evt.target.row, evt.target.col, selectedBall + 1)) {
          evt.target.graphics.beginFill("grey").drawCircle(0, 0, ballSize);
          if (game1.get_board_array()[evt.target.row][evt.target.col] > 0) {
            setTimeout(() => {
              evt.target.graphics.beginFill(colors[game1.get_cell(evt.target.row, evt.target.col) - 1]).drawCircle(0, 0, ballSize);
            }, 2000);
          } else {
            setTimeout(() => {
              evt.target.graphics.beginFill("white").drawCircle(0, 0, ballSize);
            }, 1000);
          }
        } else {
          if (selectedBall != 9) {
            game1.make_move(evt.target.row, evt.target.col, selectedBall + 1);
            evt.target.graphics.beginFill(colors[selectedBall]).drawCircle(0, 0, ballSize);
          } else if (hints > 0) {
            game1.make_move(evt.target.row, evt.target.col, game1.get_completed_cell(evt.target.row, evt.target.col));
            evt.target.graphics.beginFill(colors[game1.get_completed_cell(evt.target.row, evt.target.col) - 1]).drawCircle(0, 0, ballSize);
            hints = hints - 1;
            if (hints == 0) {
              selectorBalls[selectedBall].alpha = 0.3;
              let balls = game1.get_available_balls();
              if(!balls[selectedBall+1]){
                for (let i = 1; i < 10; i++) {
                  if(balls[i]){
                    selectedBall = i-1
                    selectorBall.x = selectorBalls[selectedBall].x
                    break;
                  }
                }
              }
            }
          } else if (hints == 0) {
            evt.target.graphics.beginFill("grey").drawCircle(0, 0, ballSize);
            if (game1.get_board_array()[evt.target.row][evt.target.col] > 0) {
              setTimeout(() => {
                evt.target.graphics.beginFill(colors[game1.get_cell(evt.target.row, evt.target.col) - 1]).drawCircle(0, 0, ballSize);
              }, 2000);
            } else {
              setTimeout(() => {
                evt.target.graphics.beginFill("white").drawCircle(0, 0, ballSize);
              }, 1000);
            }
          }
        }
        let balls = game1.get_available_balls();
        for (let i = 1; i < 10; i++) {
          if (!balls[i]) {
            selectorBalls[i - 1].alpha = 0.3; //graphics.beginFill("grey").drawCircle(0,0,ballSize);
          } else {
            selectorBalls[i - 1].alpha = 1;
          }
        }
        if(selectedBall < 9 && !balls[selectedBall+1]){
          for (let i = 1; i < 10; i++) {
            if(balls[i]){
              selectedBall = i-1
              selectorBall.x = selectorBalls[selectedBall].x
              break;
            }
          }
        }
      });
      container.addChild(balls[i][j])

    }
  }

  function print_sudoku_to_webpage(sudoku_object) {
    let board = sudoku_object.get_board_array();
    for (let row = 0; row <= 8; row++) {
      for (let col = 0; col <= 8; col++) {
        let input = balls[col][row];
        if (board[row][col] != 0) {
          input.graphics.beginFill(colors[board[row][col] - 1]).drawCircle(0, 0, ballSize);
        } else {
          input.graphics.beginFill("white").drawCircle(0, 0, ballSize);
        }
      }
    }
  }
  print_sudoku_to_webpage(game1)

  // This code is borrowed from another website. Thanks google.
  function createArray(length) {
    let arr = new Array(length || 0),
      i = length;

    if (arguments.length > 1) {
      let args = Array.prototype.slice.call(arguments, 1);
      while (i--) arr[length - 1 - i] = createArray.apply(this, args);
    }
    return arr;
  }

  COLORS = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple"];
  let confettiCount = 60;
  let confetti = [];
  let confettivx = [];
  let confettivy = [];
  let confettiv = 4;
  let confettimin = -600;

  function drawConfetti() {
    for (i = 0; i < confettiCount; i++) {
      confetti[i] = new createjs.Shape();
      confetti[i].graphics.beginFill(COLORS[0, rng.nextRange(0, COLORS.length)]).drawCircle(0, 0, rng.nextRange(7, 15));
      confetti[i].x = rng.nextRange(0, window.innerWidth);
      confetti[i].y = rng.nextRange(window.innerHeight + 30);
      confetti[i].visible = false;
      confettivx[i] = rng.nextRange(-1, 1) / 5.0;
      confettivy[i] = rng.nextRange(-1, 1) / 5.0;
      stage.addChild(confetti[i]);
    }
  }

  function dropConfetti() {
    droppedConfetti = false;
    for (i = 0; i < confettiCount; i++) {
      confetti[i].visible = true;
      confetti[i].y = rng.nextRange(confettimin, -20);
      confetti[i].x = rng.nextRange(0, width);
      confettivx[i] = rng.nextRange(-3, 3) / 7.0;
      confettivy[i] = rng.nextRange(-3, 3) / 3.0;
    }
  }

  drawConfetti();

  //Update stage will render next frame

  createjs.Ticker.setFPS(60);
  createjs.Ticker.addEventListener("tick", stage);
  createjs.Ticker.addEventListener("tick", handleTick);

  let droppedConfetti = false;

  function handleTick(event) {
    if (!droppedConfetti) {
      dropped = true;
      for (i = 0; i < confettiCount; i++) {
        if (confetti[i].y < window.innerHeight + 20) {
          confetti[i].x = confetti[i].x + confettivx[i]
          confetti[i].y = confetti[i].y + confettivy[i] + confettiv
          dropped = false;
        } else {
          confetti[i].visible = false;
        }
      }
      if (dropped) {
        droppedConfetti = true;
      }
    }
    stage.update();
  }

  let gamesfactor = 4*2; // gamesFactor is number of games / 400 (1600 games gamesFactor is 4)
  function newGame(difficulty) {
    // New game
    selectedBall = 0
    selectorBall.x = selectorBalls[selectedBall].x
    let d = difficulty * gamesfactor * 100 + 100*gamesfactor;
    let rand = rng.nextRange(d - 100*gamesfactor, d);
    let import_string = games[rand * 2];
    let completed_import_string = games[rand * 2 + 1];
    game1.set_board(import_string, completed_import_string);
    print_sudoku_to_webpage(game1);
    let balls = game1.get_available_balls();
    selectorBalls[9].alpha = 1;
    hints = 3;
    for (let i = 1; i < 10; i++) {
      if (!balls[i]) {
        selectorBalls[i - 1].alpha = 0.3; //graphics.beginFill("grey").drawCircle(0,0,ballSize);
      } else {
        selectorBalls[i - 1].alpha = 1;
      }
    }
    if(!balls[selectedBall+1]){
      for (let i = 1; i < 10; i++) {
        if(balls[i]){
          selectedBall = i-1
          selectorBall.x = selectorBalls[selectedBall].x
          break;
        }
      }
    }
  }

  let difficultyColors = ["#bafa25", "#e4f218", "#faa537", "#c70808"];
  let difficultyNames = ["Easy", "Medium", "Difficult", "Expert"]; //["Simple", "Easy", "Intermed.", "Expert"];

  let difficultyContainer;

  function drawDifficultySelector() {
    difficultyContainer = new createjs.Container();
    let difficulties = [];
    let diffText = [];
    for (let i = 0; i < difficultyColors.length; i++) {
      difficulties[i] = new createjs.Shape();
      difficulties[i].graphics.beginFill(difficultyColors[i]).drawCircle(0, 0, 110);
      difficulties[i].x = leftbound + 1000 / 4.0 * (i) + 125;
      difficulties[i].y = topbound + 1000 / 2.0;
      difficulties[i].diff = i;
      diffText[i] = new createjs.Text(difficultyNames[i], TEXTTYPE, "#000000")
      diffText[i].x = leftbound + 1000 / 4.0 * (i) + 125;
      diffText[i].y = topbound + 1000 / 2.0 - 20;
      diffText[i].textAlign = 'center';
      difficultyContainer.addChild(difficulties[i]);
      difficultyContainer.addChild(diffText[i]);
      difficulties[i].on("mousedown", function(event) {
        newGame(event.target.diff);
        container.removeChild(difficultyContainer);
      });
    }
    container.addChild(difficultyContainer);
  }

  let wonContainer;
  let wonDialog;
  let isFinished = false;
  // Draw a dialog to create a new game
  function wonGame() {
    wonContainer = new createjs.Container();
    wonDialog = new createjs.Shape();
    wonDialog.graphics.beginFill(colors[0]).drawCircle(0, 0, 1000);
    wonDialog.y = topbound + 1000 + 900;
    wonDialog.x = leftbound + 500;
    let wonText = new createjs.Text("You won! (Tap)", TEXTTYPE, "#000000")
    wonText.x = leftbound + 360;
    wonText.y = topbound + 925;
    wonContainer.on("mousedown", function(event) {
      container.removeChild(wonContainer);
      drawDifficultySelector();
      isFinished = false;
    });
    wonContainer.addChild(wonDialog);
    wonContainer.addChild(wonText);
    container.addChild(wonContainer);

  }
  drawDifficultySelector();
  stage.update();

  //dropConfetti();
  //wonGame();
})();

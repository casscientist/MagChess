# MagChess ![knight](READMEicon.png)
This is a personal project:
- Chess interface for playing similar to online using pysimplegui
- Designed to work with custom board and magnetic pieces that are tracked through a hall effect sensor array and uploaded to a Teensy, where on/off states are converted into a move that is recieved to python through pyserial, and placed on the GUI
- Includes options for sounds, piece promotion, various board layouts, timers with different options, pause/play/resign features, and analysis through Lichess at the end of the game
- This means an over the board game of chess could be played normally, but saved and tracked through a computer, combining the best of both worlds
- The intention is to recreate a DGT board myself, and have all-in-one software to play over the board
- Currently only utilizes manual move selection as board is not complete
## Intended Features
- [ ] Trying to play a move while paused will resume
- [ ] Seperate out menu layout creation from playGame, create skeleton for computer move options
- [ ] Text on right side of moves gets pushed to side if the left side is a longer move
- [ ] Time increment gives it to the other player after the move is made
- [ ] Make timer increment in 1/10 second and display 1/10 second after under 10.0 seconds
- [ ] Add popup-text appearing when resigning and telling player to analyze
- [ ] Make entire interface larger with full screen ability
- [ ] Add option to play computer with built-in engine and levels
- [ ] Add txt file that can track games played and save them to a folder with pgn, time/date, names of players, result, etc. that can be searched later 
- [ ] Add option to veiw current evaluation with bar using imported chess engine while playing live(stockfish)
- [ ] Crash when untimed and hitting pause or resign
- [ ] Add "Play Random Game" Feature with random moves, fast forward option to generate game pgn with random moves ending in a checkmate (for fun)
- [ ] Add Draw Offer ability, detection of stalemate and 3 move repetition


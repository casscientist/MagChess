# MagChess ![knight](READMEicon.png)
### Incomplete! Only documentation at the moment, a work in progress
This is a personal project:
- Chess interface for playing similar to online using pysimplegui
- Designed to work with custom board and magnetic pieces that are tracked through a hall effect sensor array and uploaded to a Teensy, where on/off states are converted into a move that is recieved to python through pyserial, and placed on the GUI
- Includes options for sounds, piece promotion, various board layouts, timers with different options, pause/play/resign features, and analysis through Lichess at the end of the game
- This means an over the board game of chess could be played normally, but saved and tracked through a computer, combining the best of both worlds
- The intention is to recreate a DGT board myself, and have all-in-one software to play over the board
- Currently only utilizes manual move selection as board is not complete
## Intended Features
- [ ] Make entire interface larger with full screen ability
- [ ] Add option to play computer with built-in engine and levels
- [ ] Add txt file that can track games played and save them to a folder with pgn, time/date, names of players, result, etc. that can be searched later 
- [ ] Add option to veiw current evaluation with bar using imported chess engine while playing live(stockfish)
- [ ] Add "Play Random Game" Feature with random moves, fast forward option to generate game pgn with random moves ending in a checkmate (for fun)
- [ ] Add Draw Offer ability, detection of stalemate and 3 move repetition
- [ ] Change interface for Pause/Play,Resign, Draw, etc. with popup showing options after game, winner, whether to save game or not, analysis, reset board, etc.
## Todo
- Add arduino script for calculating moves
## Packages
- chess
- PySimpleGUI
- playsound
- pyperclip
- webbrowser

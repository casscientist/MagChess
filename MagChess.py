import chess
import math
import copy
import PySimpleGUI as sg
import time
import threading
import os
from playsound import playsound
import pyperclip
import webbrowser

ChessBoard = chess.Board()

BLANK = 0               # piece values
PAWNB = 1
KNIGHTB = 2
BISHOPB = 3
ROOKB = 4
KINGB = 5
QUEENB = 6
PAWNW = 7
KNIGHTW = 8
BISHOPW = 9
ROOKW = 10
KINGW = 11
QUEENW = 12

def soundSettings(setting):  #plays muted sound instead of turning off sounds, which is probably the correct way to do it but idk
    if setting == True:
        moveSound = 'Sounds\\move.mp3'
        checkSound = 'Sounds\\check.mp3'
        captureSound = 'Sounds\\capture.mp3'
        checkmateSound = 'Sounds\\checkmate.mp3'
    else:
        moveSound = 'Sounds\\mute.mp3'
        checkSound = 'Sounds\\mute.mp3'
        captureSound = 'Sounds\\mute.mp3'
        checkmateSound = 'Sounds\\mute.mp3'
    return(moveSound, checkSound, captureSound, checkmateSound)

moveSound, checkSound, captureSound, checkmateSound = soundSettings(True) #default sounds are on

sounds = True #Tracks if sounds are on or off
isAutoQueen = True
isPaused = False

def pieceTheme(theme): 
    if theme == 'Modern':
        filePath = ['neoPieces\\', 'neo.png'] #folder path and then piece name array
        lightSquareColor, darkSquareColor = '#eeeed2','#769656'
        darkHighlightColor, lightHighlightColor = '#bbcb2b', '#f7f769'
    elif theme == 'Lichess':
        filePath = ['lichessPieces\\', 'Lichess.png']
        lightSquareColor, darkSquareColor = '#ced6de','#4e81b1'
        darkHighlightColor, lightHighlightColor = '#85b878', '#bad184'
    elif theme == 'Classic':
        filePath = ['classicPieces\\', 'classic.png']
        lightSquareColor, darkSquareColor = '#bda27f','#7c5940'
        darkHighlightColor, lightHighlightColor = '#a88137', '#c7a355'
    elif theme == 'Alice in Wonderland':
        filePath = ['AliceInWonderlandPieces\\', 'alice.png']
        lightSquareColor, darkSquareColor = '#ffffff','#fcd8dd'
        darkHighlightColor, lightHighlightColor = '#ed9aa6', '#eeaeb7'
    else:
        filePath = ['neoPieces\\', 'neo.png'] #modern is default theme
        lightSquareColor, darkSquareColor = '#eeeed2','#769656'
        darkHighlightColor, lightHighlightColor = '#bbcb2b', '#f7f769'
    blank = os.path.join(filePath[0], 'blank.png')
    bishopB = os.path.join(filePath[0],f'bB{filePath[1]}')
    bishopW = os.path.join(filePath[0], f'wB{filePath[1]}')
    pawnB = os.path.join(filePath[0], f'bP{filePath[1]}')
    pawnW = os.path.join(filePath[0], f'wP{filePath[1]}')
    knightB = os.path.join(filePath[0], f'bN{filePath[1]}')
    knightW = os.path.join(filePath[0], f'wN{filePath[1]}')
    rookB = os.path.join(filePath[0], f'bR{filePath[1]}')
    rookW = os.path.join(filePath[0], f'wR{filePath[1]}')
    queenB = os.path.join(filePath[0], f'bQ{filePath[1]}')
    queenW = os.path.join(filePath[0], f'wQ{filePath[1]}')
    kingB = os.path.join(filePath[0], f'bK{filePath[1]}')
    kingW = os.path.join(filePath[0], f'wK{filePath[1]}')

    images = {BISHOPB: bishopB, BISHOPW: bishopW, PAWNB: pawnB, PAWNW: pawnW, KNIGHTB: knightB, KNIGHTW: knightW,
          ROOKB: rookB, ROOKW: rookW, KINGB: kingB, KINGW: kingW, QUEENB: queenB, QUEENW: queenW, BLANK: blank}

    return(images, lightSquareColor, darkSquareColor, lightHighlightColor, darkHighlightColor)

images, lightSquareColor, darkSquareColor, lightHighlightColor, darkHighlightColor = pieceTheme('Modern') #Default theme

initial_board = [[ROOKB, KNIGHTB,  BISHOPB, QUEENB, KINGB, BISHOPB, KNIGHTB, ROOKB ],
                [PAWNB,]*8,
                [BLANK,]*8,
                [BLANK,]*8,
                [BLANK,]*8,
                [BLANK,]*8,
                [PAWNW,]*8,
                [ROOKW, KNIGHTW, BISHOPW, QUEENW, KINGW, BISHOPW, KNIGHTW, ROOKW]]

def render_square(label, image, key, location):
    if (location[0] + location[1]) % 2:
        color = darkSquareColor
        text_color = lightSquareColor
    else:
        color = lightSquareColor
        text_color = darkSquareColor
    return sg.Button(label, image_filename=image, font = 'Any 9 bold', size=(1, 1), border_width = 0, button_color=(text_color, color), pad=(0, 0), key=key)

class Timer():
    def __init__(self,startMin, startSec,gameTimeInc):
        self.timestarted = None
        self.paused = False
        self.gameTimeInc = gameTimeInc
        self.startSec, self.startMin = startSec,startMin
        self.startTime = self.startMin*60 + self.startSec
    def start(self):
        self.timestarted = True
        while self.startTime > 0:
            time.sleep(1.1) #idk seemed a little fast
            self.startTime-=1
            if self.paused == True:
                break 
        if self.startTime == 0:
            self.stop()
    def Threading(self):
        x = threading.Thread(target=self.start)
        x.start()
    def pause(self):
        self.paused = True
    def resume(self):
        self.paused = False
        self.Threading()
    def stop(self):
        self.paused = True
        self.startTime = 0
    def addInc(self):
        self.startTime+=self.gameTimeInc

def PlayGame():
    #lets define some global variables so things work don't @ me
    global row, col, old_row, old_col, images, lightSquareColor, darkSquareColor, lightHighlightColor, main_background_color 
    global darkHighlightColor, moveSound, captureSound, checkSound, checkmateSound, gameStart

    main_background_color = '#312e2b'
    controls_background_color = '#272522'
    gameStart = False
    pgnArray = []
    moveCount = 0
    curMoveRow = []

    settings_layout = [
    'Board Theme', ['Modern', 'Classic', 'Lichess', 'Alice in Wonderland'],
    'Sounds ✓',
    'Auto-Queen ✓'
    ]

    board_themes = settings_layout[1]

    menu_layout = [
    ['File', ['New Game', 'Play Computer']],
    ['Settings', settings_layout],
    ['Controls', ['Pause', 'Resign', 'Analyze']]
    ]

    movesColumn = []

    menu = sg.Menu(menu_layout, background_color = 'white')

    board_layout = []

    controls = [
    [sg.T('60:00', font = 'Any 22 bold', pad = (0,0), key='Player2Time', justification = 'left', background_color= controls_background_color)],
    [sg.T('Player 2', font = 'Any 12 bold', pad = (0,0), key='Player_2_Name', justification = 'center', expand_x = True, background_color= controls_background_color)],
    [sg.Column(movesColumn, key = 'movesColumn', scrollable = True, pad = (0,0), vertical_scroll_only = True, size=(130,100), background_color = controls_background_color, justification = 'left')],
    [sg.T('Player 1', font = 'Any 12 bold', pad = (0,0), key='Player_1_Name', justification = 'center', expand_x = True, background_color= controls_background_color)],
    [sg.T('60:00', font = 'Any 22 bold', pad = (0,0), key='Player1Time', justification = 'left', background_color= controls_background_color)],

    ]

    board = copy.deepcopy(initial_board)

    for i in range(8):
            curRow = []
            for j in range(8):
                piece_image = images[initial_board[i][j]]
                if j == 0 and i == 7:
                    curRow.append(render_square('1                \n\n\n                 a', piece_image, key=(i,j), location=(i,j)))
                elif i == 7:
                    letters = ['a','b','c','d','e','f','g','h']
                    label = letters[j]
                    curRow.append(render_square(f'\n\n\n                 {label}', piece_image, key=(i,j), location=(i,j)))
                elif j == 0:
                    label = 8-(i)
                    curRow.append(render_square(f'{label}               \n\n\n', piece_image, key=(i,j), location=(i,j)))
                else:
                     curRow.append(render_square('                                     1', piece_image, key=(i,j), location=(i,j)))
            board_layout.append(curRow)

    layout = [
        [menu],
        [sg.Column(board_layout), sg.Column(controls, pad = (0,0), key ='controls', size = (150,310), background_color = main_background_color,justification = 'center')],
        [sg.Input('', key = 'input', expand_x = True, background_color = lightSquareColor, text_color = 'black')],
        [sg.Button('Move')]
        ]
    window = sg.Window('MagChess', layout, icon='knightB.ico', default_button_element_size=(12,1), auto_size_buttons=False, background_color = main_background_color)
    while True:
        event, values = window.read(timeout = 1)
        if event == sg.WIN_CLOSED:
            break
        if event == 'New Game':
            newGameInputs = newGame() #new game popup
            ChessBoard.reset() #Reset everything
            board = copy.deepcopy(initial_board)
            old_row, old_col, row, col = 0,0,0,0
            redraw_board(window, board)
            pgnArray = []
            pgn = ''
            movesColumn = []
            if moveCount > 0:
                for i in range (1, moveCount):
                    window[f'{math.ceil(i/2)}-moveNum'].update('', background_color=controls_background_color)
                    window[f'{math.ceil(i/2)}-move1'].update('', background_color=controls_background_color)
                    window[f'{math.ceil(i/2)}-move2'].update('', background_color=controls_background_color)
            moveCount = 0
            window.refresh()
            window['movesColumn'].contents_changed()
            if newGameInputs != None:
                window['Player_1_Name'].update(newGameInputs[0]) #Updates Player Names
                window['Player_2_Name'].update(newGameInputs[1])
                gameTimeInc = newGameInputs[4]
                gameStart = newGameInputs[5]
                if 'Untimed' in (newGameInputs[2], newGameInputs[3]):
                    window['Player1Time'].update(visible=False)
                    window['Player2Time'].update(visible=False)
                else:
                    window['Player1Time'].update('{:02d}:{:02d}'.format(newGameInputs[2], newGameInputs[3]), visible=True) #converts into decimal 2-unit lengths
                    window['Player2Time'].update('{:02d}:{:02d}'.format(newGameInputs[2], newGameInputs[3]),visible=True)
                    global Player_1_Timer, Player_2_Timer
                    Player_1_Timer = Timer(newGameInputs[2], newGameInputs[3],gameTimeInc) #Creates timer for each player based on inputs
                    Player_2_Timer = Timer(newGameInputs[2], newGameInputs[3],gameTimeInc)
                    Player_1_Timer.Threading() #Starts Timer's and pauses black immediately
                    Player_2_Timer.Threading()
                    Player_2_Timer.pause()
                    Player_2_Timer.startTime+=1
        if event == settings_layout[2]: #if sounds selected
            global sounds
            sounds = not sounds
            if sounds:
                menuMark = ' ✓'
            else:
                menuMark = ''
            settings_layout[2] = f'Sounds{menuMark}' #updates to turn off/on checkmark
            menu.update(menu_layout)    #updates full menu
            moveSound, checkSound, captureSound, checkmateSound = soundSettings(sounds) #changes sounds   
        if event == settings_layout[3]: #if auto queen selected
            global isAutoQueen
            isAutoQueen = not isAutoQueen
            if isAutoQueen:
                menuMark = ' ✓'
            else:
                menuMark = ''
            settings_layout[3] = f'Auto Queen{menuMark}' #updates to turn off/on checkmark
            menu.update(menu_layout)    #updates full menu
        if event in board_themes: 
            images,lightSquareColor, darkSquareColor, lightHighlightColor, darkHighlightColor = pieceTheme(event)
            redraw_board(window, board) #redraws board with new theme from event
        if event == 'Resign' and gameStart == True:
            gameStart = False
            Player_1_Timer.stop()
            Player_2_Timer.stop()
        if event == 'Analyze':
            if gameStart == False:
                if pgnArray != []: #In case no moves were made
                    pyperclip.copy(pgn)
                    webbrowser.open_new_tab('https://lichess.org/analysis') #copy and open analysis link
        if event == menu_layout[2][1][0] and gameStart == True: #if Paused or Resume button pressed
            global isPaused
            isPaused = not isPaused
            if isPaused:
                menu_layout[2][1][0] = 'Resume'
                Player_1_Timer.pause()
                Player_2_Timer.pause()
            else:
                menu_layout[2][1][0] = 'Pause'
                Player_1_Timer.resume()
                Player_2_Timer.resume()
            menu.update(menu_layout)
        if gameStart == True and 'Untimed' not in (newGameInputs[2], newGameInputs[3]):
            if (moveCount % 2) == 0:
                gameTimeMinutes, gameTimeSeconds = divmod(Player_1_Timer.startTime, 60)
                window['Player1Time'].update('{:02d}:{:02d}'.format(gameTimeMinutes, gameTimeSeconds))
            elif (moveCount % 2) != 0:
                gameTimeMinutes, gameTimeSeconds = divmod(Player_2_Timer.startTime, 60)
                window['Player2Time'].update('{:02d}:{:02d}'.format(gameTimeMinutes, gameTimeSeconds))
            if Player_1_Timer.startTime == 0 or Player_2_Timer == 0:
                gameStart = False
                Player_1_Timer.stop()
                Player_2_Timer.stop()
        if event == 'Move' and gameStart == True:
            window['input'].update('')
            arduinoMove = values['input']
            srtSq = chess.parse_square(arduinoMove[0:2])
            endSq = chess.parse_square(arduinoMove[2:4])
            move = chess.Move.from_uci(arduinoMove)
            row, col = 7 - srtSq // 8, srtSq % 8 #board is flipped so 7 - srtSq
            piece = board[row][col] 
            didPromote = [False,None]  #promotion variable
            if piece == PAWNB and row == 6: #if black pawn promotes
                    if isAutoQueen:
                        move = chess.Move.from_uci(f'{move}q')
                        didPromote = [True,QUEENB]
                    else:
                        promotedPiece = promotionPopup()
                        move = chess.Move.from_uci(f'{move}{promotedPiece}')
                        promotedPieceConversion = {'q':QUEENB, 'r':ROOKB, 'b':BISHOPB, 'n':KNIGHTB}
                        didPromote = [True,promotedPieceConversion[promotedPiece]]
            if piece == PAWNW and row == 1: #if white pawn promotes
                    if isAutoQueen:
                        move = chess.Move.from_uci(f'{move}q')
                        didPromote = [True,QUEENW]
                    else:
                        promotedPiece = promotionPopup()
                        move = chess.Move.from_uci(f'{move}{promotedPiece}')
                        promotedPieceConversion = {'q':QUEENW, 'r':ROOKW, 'b':BISHOPW, 'n':KNIGHTW}
                        didPromote = [True,promotedPieceConversion[promotedPiece]]
            if move in list(ChessBoard.legal_moves):  #check for move legality
                move_san = ChessBoard.san(move) #This is the typical algebraic notation for the move
                moveCount += 1 
                if (moveCount % 2) == 0 and 'Untimed' not in (newGameInputs[2], newGameInputs[3]): #White made a move 
                    Player_1_Timer.addInc() #Adds the increment
                    Player_1_Timer.resume() 
                    Player_2_Timer.pause()
                elif (moveCount % 2) != 0 and 'Untimed' not in (newGameInputs[2], newGameInputs[3]): #Black made a move
                    Player_2_Timer.addInc() 
                    Player_2_Timer.resume()
                    Player_1_Timer.pause()
                    pgnArray.append(f'{(moveCount // 2) + 1}.') #adds move number
                pgnArray.append(move_san) #Adds move to pgn array
                pgn = ' '.join(pgnArray) #converts pgn to string for copy/paste
                board[row][col] = BLANK
                old_row, old_col = row, col  #Now changes new square
                row, col = 7 - endSq // 8, endSq % 8
                if didPromote[0]: #If a piece promotes, put the promoted piece on the board
                    board[row][col] = didPromote[1]
                else:    
                    board[row][col] = piece
                if ChessBoard.is_castling: #Castling check
                    if piece == KINGB and move == chess.Move.from_uci('e8g8'): #Black kingside castle
                        board[row][7] = BLANK
                        board[row][5] = ROOKB
                    elif piece == KINGB and move == chess.Move.from_uci('e8c8'): #Black queenside castle
                        board[row][0] = BLANK
                        board[row][3] = ROOKB
                    elif piece == KINGW and move == chess.Move.from_uci('e1c1'): #White queenside castle
                        board[row][0] = BLANK
                        board[row][3] = ROOKW
                    elif piece == KINGW and move == chess.Move.from_uci('e1g1'): #White kingside castle
                        board[row][7] = BLANK
                        board[row][5] = ROOKW
                if ChessBoard.is_en_passant(move): #Holy Hell!
                    if piece == PAWNW:
                        board[row+1][col] = BLANK
                    elif piece == PAWNB:
                        board[row-1][col] = BLANK
                redraw_board(window, board) #Updates the board
                if (moveCount % 2) != 0: #Adds next line if odd numbered moveCount
                    window.extend_layout(window['movesColumn'], updateMoveList(moveCount, move_san))
                    window.refresh()
                    window['movesColumn'].contents_changed() #Updates scroll area size to account for new element
                elif (moveCount % 2) == 0:
                    window[f'{math.ceil(moveCount / 2)}-move2'].update(move_san)
                    window.refresh()
                    window['movesColumn'].contents_changed() #Updates scroll area size to account for new element
                 #Updates the move list
                if ChessBoard.gives_check(move): 
                    ChessBoard.push(move) #has to push move first otherwise can't tell if checkmate
                    if ChessBoard.is_checkmate():
                        playsound(checkmateSound, block = False)
                        Player_1_Timer.stop()
                        Player_2_Timer.stop()
                    else:
                        playsound(checkSound, block = False)
                elif ChessBoard.is_capture(move):
                    playsound(captureSound, block = False)
                    ChessBoard.push(move) #push after move otherwise there are errors 
                else:
                    playsound(moveSound, block = False)
                    ChessBoard.push(move)
            else:
                sg.popup_ok('Illegal Move',text_color='white', background_color = '#5e687e')
            
def redraw_board(window, board):
    for i in range(8):
        for j in range(8):
            color = darkSquareColor if (i+j) % 2 else lightSquareColor
            text_color = lightSquareColor if (i+j) % 2 else darkSquareColor
            piece_image = images[board[i][j]]
            elem = window[(i,j)]
            elem.Update(button_color = (text_color, color),
                        image_filename=piece_image,)
    #Colors squares that have moved with diff colors for light and dark
    if gameStart and 0 not in (old_row,old_col,row,col):
        button = window[old_row, old_col]
        if (old_row + old_col) % 2:
            button.Update(button_color = darkHighlightColor)
        else:
            button.Update(button_color = lightHighlightColor)
        button = window[row, col]        
        if (row + col) % 2:
            button.Update(button_color = darkHighlightColor)
        else:
            button.Update(button_color = lightHighlightColor)

def newGame():
    customTime = [[sg.T('Minutes:', background_color = '#5e687e', pad=((0,5),0)), sg.Input(key='timeMin', enable_events = True, pad=((0,5),0), size = (2,1)), 
        sg.T('Seconds:', background_color = '#5e687e', pad=((0,5),0)), sg.Input(key='timeSec', enable_events = True, size = (2,1)), 
        sg.T('Increment:', background_color = '#5e687e', pad=((0,5),0)), sg.Input(key='increment',  enable_events = True, pad=((0,5),0), size = (2,1))]]
    layout = [
        [sg.T('Player 1 (W)', background_color = '#5e687e'), sg.InputText(key='name1', size = (15,1))],
        [sg.T('Player 2 (B) ', background_color = '#5e687e'), sg.InputText(key='name2', size=(15,1))],
        [sg.Text('Time Control:', background_color = '#5e687e'), sg.Combo(['Untimed', 'Classical(30|15)', 'Rapid(10|5)', 'Long Blitz(5|5)', 'Short Blitz(3|3)', 'Custom'], pad=((1,0),0), key='TimeControl', enable_events=True)],
        [sg.Column(customTime, key = 'customTime', background_color = '#5e687e', justification = 'left', visible = False, expand_x=True)],
        [sg.Button('Cancel'), sg.Button('Start')]
    ]
    window = sg.Window('NewGame', layout, background_color = '#5e687e', no_titlebar=True, modal=True, finalize = True)
    isCustom = True
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        if event == 'TimeControl':
            if values['TimeControl'] == 'Untimed':
                window['customTime'].update(visible = False)
                gameTimeMinutes = 'Untimed'
                gameTimeSeconds = 'Untimed'
                gameTimeInc = 0
                isCustom = False
            elif values['TimeControl'] == 'Classical(30|15)':
                gameTimeMinutes = 30
                gameTimeSeconds = 0
                gameTimeInc = 15
                window['customTime'].update(visible = False)
                isCustom = False
            elif values['TimeControl'] == 'Rapid(10|5)':
                gameTimeMinutes = 10
                gameTimeSeconds = 0
                gameTimeInc = 5
                window['customTime'].update(visible = False)
                isCustom = False
            elif values['TimeControl'] == 'Long Blitz(5|5)':
                gameTimeMinutes = 5
                gameTimeSeconds = 0
                gameTimeInc = 5
                window['customTime'].update(visible = False)
                isCustom = False
            elif values['TimeControl'] == 'Short Blitz(3|3)':
                gameTimeMinutes = 3
                gameTimeSeconds = 0
                gameTimeInc = 3
                window['customTime'].update(visible = False)
                isCustom = False
            elif values['TimeControl'] == 'Custom':
                window['customTime'].update(visible = True)
                isCustom = True
        if event == 'Start':
            Player_1_Name = values['name1']
            Player_2_Name = values['name2']
            if isCustom == True:
                gameTimeMinutes = int(values['timeMin']) if values['timeMin'] != '' else 0
                gameTimeSeconds = int(values['timeSec']) if values['timeSec'] != '' else 0
                gameTimeInc = int(values['increment']) if values['increment'] != '' else 0
            if Player_1_Name == '' or Player_2_Name == '' or (isCustom == True and (gameTimeMinutes == 0 or gameTimeSeconds == 0)):
                sg.Popup('Must fill fields', background_color = '#5e687e')
            else:
                window.close()
                gameStart = True
                return(Player_1_Name, Player_2_Name, gameTimeMinutes, gameTimeSeconds, gameTimeInc, gameStart)
        if event == 'timeMin' and values['timeMin'] and values['timeMin'][-1] not in ('0123456789') or len(values['timeMin']) > 2:
            window['timeMin'].update(values['timeMin'][:-1])
        if event == 'timeSec' and values['timeSec'] and values['timeSec'][-1] not in ('0123456789') or len(values['timeSec']) > 2:
            window['timeSec'].update(values['timeSec'][:-1])
        if event == 'increment' and values['increment'] and values['increment'][-1] not in ('0123456789') or len(values['increment']) > 2:
            window['increment'].update(values['increment'][:-1])
    window.close()
    gameStart = True
def promotionPopup():
    layout = [
        [sg.Button('', key = 'Q', button_color = ('white', '#5e687e'), image_filename = images[QUEENW], size=(10,10)), sg.Button('', key = 'R', button_color = ('white', '#5e687e'),image_filename = images[ROOKW], size=(10,10)), 
        sg.Button('', key = 'B', button_color = ('white', '#5e687e'),image_filename = images[BISHOPW], size=(10,10)), sg.Button('', key = 'N', button_color = ('white', '#5e687e'), image_filename = images[KNIGHTW], size=(10,10))]
    ]
    window = sg.Window('Promote', layout, background_color = '#5e687e', no_titlebar=True, modal=True, finalize=True)
    window['Q'].bind('<Enter>', '+MOUSE OVER+')
    window['Q'].bind('<Leave>', '+MOUSE AWAY+')
    window['R'].bind('<Enter>', '+MOUSE OVER+')
    window['R'].bind('<Leave>', '+MOUSE AWAY+')
    window['B'].bind('<Enter>', '+MOUSE OVER+')
    window['B'].bind('<Leave>', '+MOUSE AWAY+')
    window['N'].bind('<Enter>', '+MOUSE OVER+')
    window['N'].bind('<Leave>', '+MOUSE AWAY+')

    array = ['Q+MOUSE OVER+', 'Q+MOUSE AWAY+', 'R+MOUSE OVER+', 'R+MOUSE AWAY+', 'N+MOUSE OVER+', 'N+MOUSE AWAY+', 'B+MOUSE OVER+', 'B+MOUSE AWAY+']

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: 
            break
        if event == 'Q': 
            promotedPiece = 'q'
            break
        if event == 'R': 
            promotedPiece = 'r'
            break
        if event == 'B': 
            promotedPiece = 'b'
            break
        if event == 'N': 
            promotedPiece = 'n'
            break
        if event in array: #Cycles through to update colors if mouse over
            if event[8] == 'O': #Mouse Over
                window[event[0]].update(button_color=('white', 'yellow'))
            elif event[8] == 'A': #Mouse Away
                window[event[0]].update(button_color=('white', '#5e687e'))
    window.close()
    return promotedPiece

def updateMoveList(moveCount,move_san):
    moveNum = (math.ceil(moveCount / 2)) #Rounds up to nearest integer to display move count e.g move 1/2 = 1
    controls_background_color = '#272522'
    move1 = move_san
    move2 = ''
    sg.set_options(background_color=controls_background_color) #COLOR ISSUE FIXED !!!!!
    return [[sg.T(str(moveNum), key= f'{moveNum}-moveNum', pad =((5,10), 0), justification = 'center', font = 'Any 11 bold', background_color= 'gray'), sg.T(move1, key=f'{moveNum}-move1', pad =(0, 0), background_color= controls_background_color), 
    sg.T(move2, pad = ((30,0), 0), key = f'{moveNum}-move2', background_color= controls_background_color)]]

PlayGame() #Play!
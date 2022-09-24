import chess
import math
import copy
import PySimpleGUI as sg
import time
import threading
import os
from playsound import playsound
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

BLANK = 0               #Constant piece values
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

class AppVariables(): #For app wide variables and settings and other setup
    def __init__(self):
        self.game_start = False
        self.timer_variables()
        self.selenium_setup()
        self.board_variables()
        self.constants()

    def selenium_setup(self):    
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.service = Service('drivers\chromedriver.exe')

    def timer_variables(self):
        self.game_time_minutes = 0
        self.game_time_seconds = 0
        self.game_time_inc = 0
        self.game_time_untimed = False

    def board_variables(self):
        self.board = []
        self.pgn_array = []
        self.pgn = ''
        self.move_count = 0
        self.moves_column = []
        self.images,self.light_square_color,self.light_highlight_color,self.dark_square_color,self.dark_highlight_color = self.piece_theme('Modern') #Default theme
        self.move_sound, self.check_sound, self.capture_sound, self.checkmate_sound = self.sound_settings(True) #default sounds are on

    def constants(self):
        self.main_background_color = '#312e2b'
        self.controls_background_color = '#272522'

    def sound_settings(self, setting):  #plays muted sound instead of turning off sounds, which is probably the correct way to do it but idk
        if setting:
            move_sound = 'Sounds\\move.mp3'
            check_sound = 'Sounds\\check.mp3'
            capture_sound = 'Sounds\\capture.mp3'
            checkmate_sound = 'Sounds\\checkmate.mp3'
        else:
            move_sound = 'Sounds\\mute.mp3'
            check_sound = 'Sounds\\mute.mp3'
            capture_sound = 'Sounds\\mute.mp3'
            checkmate_sound = 'Sounds\\mute.mp3'

        return(move_sound, check_sound, capture_sound, checkmate_sound)

    def piece_theme(self, theme): 
        if theme == 'Modern':
            filePath = ['neoPieces\\', 'neo.png'] #folder path and then piece name array
            light_square_color, dark_square_color = '#eeeed2','#769656'
            dark_highlight_color, light_highlight_color = '#bbcb2b', '#f7f769'
        elif theme == 'Lichess':
            filePath = ['lichessPieces\\', 'Lichess.png']
            light_square_color, dark_square_color = '#ced6de','#4e81b1'
            dark_highlight_color, light_highlight_color = '#85b878', '#bad184'
        elif theme == 'Classic':
            filePath = ['classicPieces\\', 'classic.png']
            light_square_color, dark_square_color = '#bda27f','#7c5940'
            dark_highlight_color, light_highlight_color = '#a88137', '#c7a355'
        elif theme == 'Alice in Wonderland':
            filePath = ['AliceInWonderlandPieces\\', 'alice.png']
            light_square_color, dark_square_color = '#ffffff','#fcd8dd'
            dark_highlight_color, light_highlight_color = '#ed9aa6', '#eeaeb7'

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

        images = {BISHOPB: bishopB, BISHOPW: bishopW, PAWNB: pawnB, PAWNW: pawnW, KNIGHTB: knightB, KNIGHTW: knightW, #dict to cycle through images/values
            ROOKB: rookB, ROOKW: rookW, KINGB: kingB, KINGW: kingW, QUEENB: queenB, QUEENW: queenW, BLANK: blank}

        return(images, light_square_color,light_highlight_color,dark_square_color,dark_highlight_color)

app_variables = AppVariables() #initiate app_variables

ChessBoard = chess.Board() #creates software board

sounds = True #Tracks if sounds are on or off
isAutoQueen = True
isPaused = False

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
        color = app_variables.dark_square_color
        text_color = app_variables.light_square_color
    else:
        color = app_variables.light_square_color
        text_color = app_variables.dark_square_color
    return sg.Button(label, image_filename=image, font = 'Any 9 bold', size=(1, 1), border_width = 0, button_color=(text_color, color), pad=(0, 0), key=key)

class Timer():
    def __init__(self,startMin, startSec,gameTimeInc):
        self.timestarted = None
        self.paused = False
        self.gameTimeInc = gameTimeInc
        self.startSec, self.startMin = startSec,startMin
        self.time = self.startMin*60 + self.startSec

    def start(self):
        self.timestarted = True
        while self.time > 0:
            time.sleep(0.1)
            self.time-=0.1
            if self.paused:
                break 
        if self.time == 0:
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
        self.time = 0

    def addInc(self):
        self.time+=self.gameTimeInc

def play_game():
    settings_layout = [
    'Board Theme', ['Modern', 'Classic', 'Lichess', 'Alice in Wonderland'],
    'Sounds ✓',
    'Auto-Queen ✓'
    ]

    board_themes = settings_layout[1]

    menu_layout = [
    ['File', ['New Game', 'Play Computer']],
    ['Settings', settings_layout],
    ['Controls', ['Pause', 'Abort']]
    ]

    menu = sg.Menu(menu_layout, background_color = 'white')

    board_layout = []

    controls = [
    [sg.T('60:00', font = 'Any 22 bold', pad = (0,0), key='Player2Time', justification = 'left', background_color= app_variables.controls_background_color)],
    [sg.T('Player 2', font = 'Any 12 bold', pad = (0,0), key='Player_2_Name', justification = 'center', expand_x = True, background_color= app_variables.controls_background_color)],
    [sg.Column(app_variables.moves_column, key = 'movesColumn', scrollable = True, pad = (0,0), vertical_scroll_only = True, size=(130,100), background_color = app_variables.controls_background_color, justification = 'left')],
    [sg.T('Player 1', font = 'Any 12 bold', pad = (0,0), key='Player_1_Name', justification = 'center', expand_x = True, background_color= app_variables.controls_background_color)],
    [sg.T('60:00', font = 'Any 22 bold', pad = (0,0), key='Player1Time', justification = 'left', background_color= app_variables.controls_background_color)],

    ]

    app_variables.board = copy.deepcopy(initial_board)

    for i in range(8): #Creates array of buttons with labels, piece images
            cur_row = [] 
            for j in range(8):
                piece_image = app_variables.images[initial_board[i][j]]
                if j == 0 and i == 7:
                    cur_row.append(render_square('1                \n\n\n                 a', piece_image, key=(i,j), location=(i,j)))
                elif i == 7:
                    letters = ['a','b','c','d','e','f','g','h']
                    label = letters[j]
                    cur_row.append(render_square(f'\n\n\n                 {label}', piece_image, key=(i,j), location=(i,j)))
                elif j == 0:
                    label = 8-(i)
                    cur_row.append(render_square(f'{label}               \n\n\n', piece_image, key=(i,j), location=(i,j)))
                else:
                     cur_row.append(render_square('                                     1', piece_image, key=(i,j), location=(i,j)))
            board_layout.append(cur_row)

    layout = [
        [menu],
        [sg.Column(board_layout), sg.Column(controls, pad = (0,0), key ='controls', size = (150,310), background_color = app_variables.main_background_color,justification = 'center')],
        [sg.Input('', key = 'input', expand_x = True, background_color = app_variables.light_square_color, text_color = 'black')],
        [sg.Button('Move', key = 'MOVE')]
        ]
    window = sg.Window('MagChess', layout, icon='knightB.ico', default_button_element_size=(12,1), resizable=True, auto_size_buttons=False, background_color = app_variables.main_background_color).Finalize()
    window.Maximize()
    while True:
        event, values = window.read(timeout = 1)
        if event == sg.WIN_CLOSED:
            break

        if event == 'New Game' and not app_variables.game_start:
            newGameInputs = new_game() #new game popup
            reset_board(window) #Reset game
            menu_layout[2][1][1] = 'Abort' #Reset text to abort
            menu.update(menu_layout)
            if newGameInputs != None:
                Player_1_Name, Player_2_Name, = newGameInputs[0], newGameInputs[1]
                window['Player_1_Name'].update(Player_1_Name) 
                window['Player_2_Name'].update(Player_2_Name)
                if app_variables.game_time_untimed is True:
                    window['Player1Time'].update(visible=False)
                    window['Player2Time'].update(visible=False)
                else:
                    window['Player1Time'].update('{:02d}:{:02d}'.format(app_variables.game_time_minutes, app_variables.game_time_seconds), visible=True) #converts into decimal 2-unit lengths
                    window['Player2Time'].update('{:02d}:{:02d}'.format(app_variables.game_time_minutes, app_variables.game_time_seconds),visible=True)
                    global Player_1_Timer, Player_2_Timer
                    Player_1_Timer = Timer(app_variables.game_time_minutes, app_variables.game_time_seconds + 0.9, app_variables.game_time_inc) #Creates timer for each player based on inputs, delay added so doesn't start counting instantly
                    Player_2_Timer = Timer(app_variables.game_time_minutes, app_variables.game_time_seconds + 0.9, app_variables.game_time_inc)
                    Player_1_Timer.Threading() #Starts Timer's and pauses black immediately

        if event == settings_layout[2]: #if sounds selected
            global sounds
            sounds = not sounds
            if sounds:
                menuMark = ' ✓'
            else:
                menuMark = ''
            settings_layout[2] = f'Sounds{menuMark}' #updates to turn off/on checkmark
            menu.update(menu_layout)    #updates full menu
            app_variables.move_sound, app_variables.check_sound, app_variables.capture_sound, app_variables.checkmate_sound = app_variables.sound_settings(sounds) #changes sounds   
        
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
            app_variables.images,app_variables.light_square_color,app_variables.light_highlight_color,app_variables.dark_square_color,app_variables.dark_highlight_color = app_variables.piece_theme(event)
            redraw_board(window) #redraws board with new theme from event
        
        if event == menu_layout[2][1][1] and app_variables.game_start: #abort/resign pressed
            if app_variables.move_count > 1:
                game_over(window, "Resignation", Player_2_Name if ChessBoard.turn else Player_1_Name)
            else:
                game_over(window, 'Abort')

        if event == menu_layout[2][1][0] and app_variables.game_start and not app_variables.game_time_untimed: #if Paused or Resume button pressed
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
        
        if app_variables.game_start and not app_variables.game_time_untimed: #controls timers
            if (app_variables.move_count % 2) == 0: 
                time.sleep(0.01)
                if Player_1_Timer.time < 10: #Switch to decimal when under 10s
                    app_variables.game_time_seconds, gameTimeDS = Player_1_Timer.time // 1, (Player_1_Timer.time % 1 * 10)
                    window['Player1Time'].update('00:{:02n}.{:.0f}'.format(app_variables.game_time_seconds, gameTimeDS))
                else:
                    app_variables.game_time_minutes, app_variables.game_time_seconds = divmod(int(Player_1_Timer.time), 60)
                    window['Player1Time'].update('{:02d}:{:02d}'.format(app_variables.game_time_minutes, app_variables.game_time_seconds))
            elif (app_variables.move_count % 2) != 0:
                time.sleep(0.01)
                if Player_2_Timer.time < 10: #Switch to decimal when under 10s
                    app_variables.game_time_seconds, gameTimeDS = Player_2_Timer.time // 1, (Player_2_Timer.time % 1 * 10) #deci-seconds
                    window['Player2Time'].update('00:{:02n}.{:.0f}'.format(app_variables.game_time_seconds, gameTimeDS))
                else:
                    app_variables.game_time_minutes, app_variables.game_time_seconds = divmod(int(Player_2_Timer.time), 60)
                    window['Player2Time'].update('{:02d}:{:02d}'.format(app_variables.game_time_minutes, app_variables.game_time_seconds))
            if Player_1_Timer.time <= 0: #timeout detecion
                window['Player1Time'].update('00:00')
                game_over(window, 'timeout', Player_2_Name)
            elif Player_2_Timer.time <= 0:
                window['Player2Time'].update('00:00')
                game_over(window, 'timeout', Player_1_Name)
        
        if event == 'MOVE' and app_variables.game_start:
            window['input'].update('')
            arduinoMove = values['input']

            try: #Handles illegal moves
                srtSq = chess.parse_square(arduinoMove[0:2])
                endSq = chess.parse_square(arduinoMove[2:4])
            except ValueError: 
                illegal_move_popup()

            else:   
                move = chess.Move.from_uci(arduinoMove)
                app_variables.row, app_variables.col = 7 - srtSq // 8, srtSq % 8 #board is flipped so 7 - srtSq
                piece = app_variables.board[app_variables.row][app_variables.col] 
                didPromote = [False,None]  #promotion variable

                if piece == PAWNB and app_variables.row == 6: #if black pawn promotes
                        if isAutoQueen:
                            move = chess.Move.from_uci(f'{move}q')
                            didPromote = [True,QUEENB]
                        else:
                            promotedPiece = promotion_popup()
                            move = chess.Move.from_uci(f'{move}{promotedPiece}')
                            promotedPieceConversion = {'q':QUEENB, 'r':ROOKB, 'b':BISHOPB, 'n':KNIGHTB}
                            didPromote = [True,promotedPieceConversion[promotedPiece]]

                if piece == PAWNW and app_variables.row == 1: #if white pawn promotes
                        if isAutoQueen:
                            move = chess.Move.from_uci(f'{move}q')
                            didPromote = [True,QUEENW]
                        else:
                            promotedPiece = promotion_popup()
                            move = chess.Move.from_uci(f'{move}{promotedPiece}')
                            promotedPieceConversion = {'q':QUEENW, 'r':ROOKW, 'b':BISHOPW, 'n':KNIGHTW}
                            didPromote = [True,promotedPieceConversion[promotedPiece]]

                if move in list(ChessBoard.legal_moves):  #check for move legality
                    move_san = ChessBoard.san(move) #This is the typical algebraic notation for the move
                    app_variables.move_count += 1

                    if (app_variables.move_count % 2) == 0 and not app_variables.game_time_untimed: #Black made a move 
                        Player_2_Timer.addInc()
                        Player_1_Timer.resume() 
                        Player_2_Timer.pause()
                    elif (app_variables.move_count % 2) != 0 and not app_variables.game_time_untimed: #White made a move
                        Player_1_Timer.addInc()
                        Player_2_Timer.resume()
                        Player_1_Timer.pause()
                        app_variables.pgn_array.append(f'{(app_variables.move_count // 2) + 1}.') #adds move number

                    app_variables.pgn_array.append(move_san) #Adds move to app_variables.pgn array
                    app_variables.pgn = ' '.join(app_variables.pgn_array) #converts pgn to string for copy/paste
                    app_variables.board[app_variables.row][app_variables.col] = BLANK
                    app_variables.old_row, app_variables.old_col = app_variables.row, app_variables.col  #Now changes new square
                    app_variables.row, app_variables.col = 7 - endSq // 8, endSq % 8

                    if didPromote[0]: #If a piece promotes, put the promoted piece on the board
                        app_variables.board[app_variables.row][app_variables.col] = didPromote[1]
                    else:    
                        app_variables.board[app_variables.row][app_variables.col] = piece

                    if ChessBoard.is_castling: #Castling check
                        if piece == KINGB and move == chess.Move.from_uci('e8g8'): #Black kingside castle
                            app_variables.board[app_variables.row][7] = BLANK
                            app_variables.board[app_variables.row][5] = ROOKB
                        elif piece == KINGB and move == chess.Move.from_uci('e8c8'): #Black queenside castle
                            app_variables.board[app_variables.row][0] = BLANK
                            app_variables.board[app_variables.row][3] = ROOKB
                        elif piece == KINGW and move == chess.Move.from_uci('e1c1'): #White queenside castle
                            app_variables.board[app_variables.row][0] = BLANK
                            app_variables.board[app_variables.row][3] = ROOKW
                        elif piece == KINGW and move == chess.Move.from_uci('e1g1'): #White kingside castle
                            app_variables.board[app_variables.row][7] = BLANK
                            app_variables.board[app_variables.row][5] = ROOKW

                    if ChessBoard.is_en_passant(move): #Holy Hell!
                        if piece == PAWNW:
                            app_variables.board[app_variables.row+1][app_variables.col] = BLANK
                        elif piece == PAWNB:
                            app_variables.board[app_variables.row-1][app_variables.col] = BLANK
                    redraw_board(window) #Updates the board

                    if app_variables.move_count > 1: #Abort game if before move 2, resign henceforth
                        menu_layout[2][1][1] = 'Resign'
                        menu.update(menu_layout)
                    if (app_variables.move_count % 2) != 0: #Adds next line if odd numbered moveCount
                        window.extend_layout(window['movesColumn'], update_move_list(move_san))
                        window.refresh()
                        window['movesColumn'].contents_changed() #Updates scroll area size to account for new element
                    elif (app_variables.move_count % 2) == 0:
                        window[f'{math.ceil(app_variables.move_count / 2)}-move2'].update(move_san)
                        window.refresh()
                        window['movesColumn'].contents_changed() #Updates scroll area size to account for new element

                    #Updates the move list
                    if ChessBoard.gives_check(move): 
                        ChessBoard.push(move) #has to push move first otherwise can't tell if checkmate
                        if ChessBoard.is_checkmate():
                            playsound(app_variables.checkmate_sound, block = False)
                            game_over(window, "Checkmate", Player_2_Name if ChessBoard.turn else Player_1_Name)
                        else:
                            playsound(app_variables.check_sound, block = False)
                    elif ChessBoard.is_capture(move):
                        playsound(app_variables.capture_sound, block = False)
                        ChessBoard.push(move) #push after move otherwise there are errors 
                    else:
                        playsound(app_variables.move_sound, block = False)
                        ChessBoard.push(move)
                else:
                    illegal_move_popup()

def illegal_move_popup():
    sg.popup_ok('Illegal Move',text_color='white', no_titlebar = True, background_color = '#5e687e')

def game_over(window, condition, win_player = 0):
    app_variables.game_start = False
    if app_variables.game_time_untimed is False:
        Player_1_Timer.stop()
        Player_2_Timer.stop()
    if win_player == 0:
        if condition == 'Abort':
            sg.popup_ok('Game Aborted')
            reset_board(window)
            return
        elif condition == 'Draw':
            pass
    elif win_player != 0: #If there is a defined winner
        layout = [
            [sg.Text(f'{win_player} wins by {condition}', text_color='white', background_color = '#5e687e')],
            [sg.Button('Save and Close', key='S&CLOSE', tooltip = 'Save file and close'), 
            sg.Button('Analyze', tooltip = 'Opens game in lichess to analyze!'), sg.Button('Close', key='CLOSE', tooltip = 'Close without saving')] 
        ]
        game_over_window = sg.Window('Game Over', layout, background_color = '#5e687e', no_titlebar=True, modal=True, finalize = True)
        event, values = game_over_window.read()
        while True:
            if event == "Analyze":
                analyze()
                break
            if event == 'S&CLOSE':
                break
            if event == 'CLOSE':
                break
        reset_board(window)
        game_over_window.close()
        return

def analyze():
    if app_variables.game_start == False and app_variables.pgn != '': #In case no moves were made
        chrome_pgn_driver = webdriver.Chrome(service = app_variables.service, options = app_variables.chrome_options)
        chrome_pgn_driver.get("https://lichess.org/analysis")
        pgn_box = chrome_pgn_driver.find_element(By.XPATH, "//textarea[@class='copyable']")
        pgn_box.send_keys(app_variables.pgn)
        pgn_box.send_keys(Keys.RETURN)

def redraw_board(window):
    for i in range(8):
        for j in range(8):
            color = app_variables.dark_square_color if (i+j) % 2 else app_variables.light_square_color
            text_color = app_variables.light_square_color if (i+j) % 2 else app_variables.dark_square_color
            piece_image = app_variables.images[app_variables.board[i][j]]
            elem = window[(i,j)]
            elem.Update(button_color = (text_color, color),
                        image_filename=piece_image,)
    #Colors squares that have moved with diff colors for light and dark
    if app_variables.game_start and 0 not in (app_variables.old_row,app_variables.old_col,app_variables.row,app_variables.col):
        button = window[app_variables.old_row, app_variables.old_col]
        if (app_variables.old_row + app_variables.old_col) % 2:
            button.Update(button_color = app_variables.dark_highlight_color)
        else:
            button.Update(button_color = app_variables.light_highlight_color)
        button = window[app_variables.row, app_variables.col]        
        if (app_variables.row + app_variables.col) % 2:
            button.Update(button_color = app_variables.dark_highlight_color)
        else:
            button.Update(button_color = app_variables.light_highlight_color)

def reset_board(window):
    ChessBoard.reset() #Reset everything
    app_variables.board = copy.deepcopy(initial_board)
    app_variables.old_row, app_variables.old_col, app_variables.row, app_variables.col = 0,0,0,0
    redraw_board(window)
    app_variables.pgn_array = []
    app_variables.pgn = ''
    app_variables.moves_column = []
    if app_variables.move_count > 0:
        for i in range (1, app_variables.move_count):
            window[f'{math.ceil(i/2)}-moveNum'].update('', background_color=app_variables.controls_background_color)
            window[f'{math.ceil(i/2)}-move1'].update('', background_color=app_variables.controls_background_color)
            window[f'{math.ceil(i/2)}-move2'].update('', background_color=app_variables.controls_background_color)
    window['Player_1_Name'].update('Player 1') 
    window['Player_2_Name'].update('Player 2')
    window['Player1Time'].update('60:00') 
    window['Player2Time'].update('60:00')
    app_variables.move_count = 0
    window.refresh()
    window['movesColumn'].contents_changed()

def new_game():
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
    time_control_select = False
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        if event == 'TimeControl':
            time_control_select = True
            window['customTime'].update(visible = False)
            isCustom = False
            if values['TimeControl'] == 'Untimed': #min/sec are 0 by default
                app_variables.game_time_untimed = True
            elif values['TimeControl'] == 'Classical(30|15)':
                app_variables.game_time_minutes = 30
                app_variables.game_time_inc = 15
            elif values['TimeControl'] == 'Rapid(10|5)':
                app_variables.game_time_minutes = 10
                app_variables.game_time_inc = 5
            elif values['TimeControl'] == 'Long Blitz(5|5)':
                app_variables.game_time_minutes = 5
                app_variables.game_time_inc = 5
            elif values['TimeControl'] == 'Short Blitz(3|3)':
                app_variables.game_time_minutes = 3
                app_variables.game_time_inc = 3
            elif values['TimeControl'] == 'Custom':
                window['customTime'].update(visible = True)
                isCustom = True
        if event == 'Start':
            Player_1_Name = values['name1']
            Player_2_Name = values['name2']
            if Player_1_Name == '' or Player_2_Name == '' or time_control_select is False:
                sg.Popup('Must fill fields', no_titlebar = True, background_color = '#5e687e')
                break
            elif isCustom:
                app_variables.game_time_minutes = int(values['timeMin']) if values['timeMin'] != '' else 0
                app_variables.game_time_seconds = int(values['timeSec']) if values['timeSec'] != '' else 0
                app_variables.game_time_inc = int(values['increment']) if values['increment'] != '' else 0
                if app_variables.game_time_minutes == 0 and app_variables.game_time_seconds < 10:
                    sg.Popup('Must Enter Time (at least 10s)', no_titlebar = True, background_color = '#5e687e')
                    break
            window.close()
            app_variables.game_start = True
            return(Player_1_Name, Player_2_Name)
        if event == 'timeMin' and values['timeMin'] and values['timeMin'][-1] not in ('0123456789') or len(values['timeMin']) > 2:
            window['timeMin'].update(values['timeMin'][:-1])
        if event == 'timeSec' and values['timeSec'] and values['timeSec'][-1] not in ('0123456789') or len(values['timeSec']) > 2:
            window['timeSec'].update(values['timeSec'][:-1])
        if event == 'increment' and values['increment'] and values['increment'][-1] not in ('0123456789') or len(values['increment']) > 2:
            window['increment'].update(values['increment'][:-1])
    window.close()

def promotion_popup():
    layout = [
        [sg.Button('', key = 'Q', button_color = ('white', '#5e687e'), image_filename = app_variables.images[QUEENW], size=(10,10)), sg.Button('', key = 'R', button_color = ('white', '#5e687e'),image_filename = app_variables.images[ROOKW], size=(10,10)), 
        sg.Button('', key = 'B', button_color = ('white', '#5e687e'),image_filename = app_variables.images[BISHOPW], size=(10,10)), sg.Button('', key = 'N', button_color = ('white', '#5e687e'), image_filename = app_variables.images[KNIGHTW], size=(10,10))]
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

def update_move_list(move_san):
    moveNum = (math.ceil(app_variables.move_count / 2)) #Rounds up to nearest integer to display move count e.g move 1/2 = 1
    move1 = move_san
    move2 = ''
    sg.set_options(background_color=app_variables.controls_background_color) #COLOR ISSUE FIXED !!!!!
    return [[sg.T(str(moveNum), key= f'{moveNum}-moveNum', pad =((5,10), 0), justification = 'center', font = 'Any 11 bold', background_color= 'gray'), sg.T(move1, key=f'{moveNum}-move1', pad =(0, 0), background_color= app_variables.controls_background_color), 
    sg.T(move2, pad = ((30,0), 0), key = f'{moveNum}-move2', background_color= app_variables.controls_background_color)]]

play_game() #Play!
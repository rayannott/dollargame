import os
import json
from datetime import datetime
from Graph import collapse_moves, load_game, show_instruction, find_best


# --- command handling
class Commands:
    def __init__(self):
        self.console_log = []
        self.console_history = []

    def process(self, inp):
        inp_split = [el.strip() for el in inp.split()]
        this_command = inp_split[0]
        if this_command not in Commands.cmds_set:
            raise KeyError(f'[ERROR] there is no \'{this_command}\' command')
        else:
            cmd_info = Commands.cmds[this_command]
            params = []
            optional_params = set()
            for el in inp_split[1:]:
                if el.startswith('-'):
                    optional_params.add(el)
                else:
                    params.append(el)
            num_of_args = len(params)
            num_of_args_needed = cmd_info['num_of_args']
            print(params, optional_params)
            if num_of_args_needed != -1 and num_of_args != num_of_args_needed:
                raise KeyError(
                    f'[ERROR] \'{this_command}\' command expects & {num_of_args_needed} argument, but {num_of_args} were given')
            else:
                return this_command, params, optional_params

    def log(self, message):
        if '&' in message:
            for msg in message.split('&'):
                self.console_log.append(msg)
        else:
            self.console_log.append(message)

    def last_command(self):
        if self.console_history:
            return self.console_history[-1]
        return ''

    # @staticmethod
    def to_integer(string_to_convert):
        try:
            game_number = int(string_to_convert)
            return game_number
        except ValueError:
            return f'[ERROR] \'{string_to_convert}\' is not a valid game'
        except Exception as e:
            return str(e)

    # commands

    def delete_game(params, options):
        game_number = Commands.to_integer(params[0])
        if isinstance(game_number, str):
            return game_number
        myfile = f'games/{game_number}.json'
        if os.path.isfile(myfile):
            os.remove(myfile)
            return (f'game #{game_number} has been deleted')
        else:
            return (f'[ERROR] game #{game_number} does not exist')

    def help(params, options):
        if '-yourself' not in options:
            if not len(params):
                return 'use \'help <command>\' to learn more&' + 'commands:&' + ',&'.join(Commands.cmds_set)
            else:
                command = params[0]
                if command in Commands.cmds_set:
                    description = Commands.cmds[command]['description']
                    examples = '&'.join(Commands.cmds[command]['examples'])
                    return description + '&----examples----&' + examples
                else:
                    return f'[ERROR] there is no \'{command}\' command'
        else:
            return 'ok, boomer'

    def reset_game(params, options):
        game_number = Commands.to_integer(params[0])
        if isinstance(game_number, str):
            return game_number
        myfile = f'games/{game_number}.json'
        if os.path.isfile(myfile):
            with open(myfile, 'r') as f:
                game = json.load(f)
            if game['plays']:
                prev_len = len(game['plays'])
                game['plays'] = []
                with open(myfile, 'w') as f:
                    json.dump(game, f)
                return f'game #{game_number} has been reset & (deleted {prev_len} attempts)'
            else:
                return f'[ERROR] game #{game_number} has never been solved'
        else:
            return f'[ERROR] game #{game_number} does not exist'

    def change_game_data(params, options):
        game_number = Commands.to_integer(params[0])
        if isinstance(game_number, str):
            return game_number

        myfile = f'games/{game_number}.json'
        if os.path.isfile(myfile):
            with open(myfile, 'r') as f:
                game = json.load(f)
            new_note = params[1]
            if new_note != '_':
                game['info']['note'] = new_note
            if '-newdate' in options:
                game['info']['date_created'] = datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S")
            with open(myfile, 'w') as f:
                json.dump(game, f)
            return f'game #{game_number} data has been changed'
        else:
            return f'[ERROR] game #{game_number} does not exist'

    def output_stats(params, options):
        return f'{params} {options}'

    @staticmethod
    def special_join(list_of_action):
        res = ''
        for i, action in enumerate(list_of_action):
            symb = '&  ' if i and i % 4 == 0 else '  '
            res += f'{symb}{action}'
        return res

    def solution(params, options):
        game_number = Commands.to_integer(params[0])
        if isinstance(game_number, str):
            return game_number
        myfile = f'games/{game_number}.json'
        if os.path.isfile(myfile):
            if '-algo' in options:
                g = load_game(myfile[6:])
                moves_best, min_num_moves = find_best(g, N=1000)
                moves_str = Commands.special_join(
                    show_instruction(moves_best, take_give_symbols='words'))
                return f'(by the algorithm) game #{game_number}& collapsed number of moves: {min_num_moves}, &{moves_str}'
            else:
                with open(myfile, 'r') as f:
                    game = json.load(f)
                if game['plays']:
                    min_number_so_far = 1000000
                    best_play_so_far = None
                    for play in game['plays']:
                        if len(play['moves']) < min_number_so_far:
                            min_number_so_far = len(play['moves'])
                            best_play_so_far = play['moves']
                    best_play_collapsed, min_num_collapsed = collapse_moves(
                        best_play_so_far)
                    best_play_instruction = show_instruction(
                        best_play_collapsed, take_give_symbols='words')
                    best_play_moves_str = Commands.special_join(
                        best_play_instruction)
                    return f'(by the player) game #{game_number}&collapsed number of moves: {min_num_collapsed}, &{best_play_moves_str}'
                else:
                    return f'[ERROR] game #{game_number} has never been solved'
        else:
            return f'[ERROR] game #{game_number} does not exist'
        return 'printed'

    cmds = {
        'delete':
        {'description': '> deletes a game by moving & it to the bin',
         'num_of_args': 1,
         'examples': ['delete 5 # deletes a game #5'],
         'function': delete_game
         },
        'reset':
        {'description': 'resets a game\'s progress & (erases all the previous attempts)',
         'num_of_args': 1,
         'examples': ['reset 10 # resets a game number 10'],
         'function': reset_game
         },
        'help':
        {'description': 'show instruction for a command & or show a list of all & available commands',
         'num_of_args': -1,
         'examples': ['help delete', 'help'],
         'function': help
         },
        'change':
        {'description': 'changes game\'s note and & (optional) resets its creation & date to now',
         'num_of_args': 2,
         'examples': ['change 12 _ -newdate &# does not change the note but & resets the creation date',
                        'change 12 new_note &# changes the note to \'new_note\'', 'change 12 _ # does nothing lol'],
         'function': change_game_data
         },
        'clear':
        {'description': 'clears the console',
         'num_of_args': 0,
         'examples': ['clear']
         },
        'stats':
        {'description': 'creates a file with games\' statistics in it',
         'num_of_args': 1,
         'examples': ['stats stats.txt'],
         'function': output_stats
         },
        'solution':
        {'description': 'prints the best solution by the player &or (optional) by the algorightm',
         'num_of_args': 1,
         'examples': ['solution 14', 'solution 14 -algo'],
         'function': solution}
    }
    cmds_set = set(cmds.keys())

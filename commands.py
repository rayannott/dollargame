import os
import json
from datetime import datetime
from pprint import pprint
from graph import collapse_moves, load_game, show_instruction, find_best
from utils import ALLOWED_SYMBOLS, assemble_games_dataframe, best_solution_by_player


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

    @staticmethod
    def special_join(list_of_action):
        res = ''
        for i, action in enumerate(list_of_action):
            symb = '&  ' if i and i % 4 == 0 else '  '
            res += f'{symb}{action}'
        return res

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
        filename_to_generate = params[0]
        # TODO: set appropriate name condition (maybe using <import re>)
        # if not set(ALLOWED_SYMBOLS).intersection(set(filename_to_generate[38:])):
        #     return f'[ERROR] {filename_to_generate} is not a valid name'
        df = assemble_games_dataframe()
        col = ['number', 'nodes', 'edges', 'bank', 'best_by_player', 'best_by_player_collapsed',
               'solution_by_player', 'best_by_algo', 'solution_by_algo']
        find_best_N = 200
        res = [col]
        for game in df:
            tmp = [str(game['game_number']), str(game['graph']
                   [0]), str(game['graph'][1]), str(game['bank'])]
            filename = f'{tmp[0]}.json'
            g = load_game(filename)
            moves_best, best_by_algo = find_best(g, N=find_best_N)
            solution_by_algo = ' '.join(show_instruction(moves_best))
            solution_by_player_noncollapsed, best_by_player = best_solution_by_player(
                filename)
            if solution_by_player_noncollapsed is not None:
                solution_by_player_collapsed, best_by_player_collapsed = collapse_moves(
                    solution_by_player_noncollapsed)
                solution_by_player = ' '.join(
                    show_instruction(solution_by_player_collapsed))
            else:
                best_by_player_collapsed = 'none'
                solution_by_player = 'none'
                best_by_player = 'none'

            tmp.append(str(best_by_player))
            tmp.append(str(best_by_player_collapsed))
            tmp.append(solution_by_player)
            tmp.append(str(best_by_algo))
            tmp.append(solution_by_algo)
            res.append(tmp)
        pprint(res)

        with open(filename_to_generate, 'w', encoding='utf-8') as f:
            for r in res:
                f.write('\t'.join(r) + '\n')
        return f'file {filename_to_generate} has been & successfully generated & you can paste it into the excel sheet now'

    def solution(params, options):
        game_number = Commands.to_integer(params[0])
        if isinstance(game_number, str):
            return game_number
        myfile = f'{game_number}.json'
        if os.path.isfile(f'games/{myfile}'):
            if '-algo' in options:
                g = load_game(myfile)
                moves_best, min_num_moves = find_best(g, N=1000)
                moves_str = Commands.special_join(
                    show_instruction(moves_best, take_give_symbols='words'))
                return f'(by the algorithm) game #{game_number}& collapsed number of moves: {min_num_moves}, &{moves_str}'
            else:
                best_solution_player, min_number = best_solution_by_player(
                    myfile)
                if best_solution_player is not None:
                    best_play_collapsed, min_num_collapsed = collapse_moves(
                        best_solution_player)
                    best_play_instruction = show_instruction(
                        best_play_collapsed, take_give_symbols='words')
                    best_play_moves_str = Commands.special_join(
                        best_play_instruction)
                    return f'(by the player) game #{game_number}&collapsed number of moves: {min_num_collapsed}, &{best_play_moves_str}'
                else:
                    return f'[ERROR] game #{game_number} has never been solved'
        else:
            return f'[ERROR] game #{game_number} does not exist'

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
        {'description': 'creates a file with games\' statistics & (may take a few minutes)',
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

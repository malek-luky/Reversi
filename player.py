# File:     05_reversi: player.py
# Author:   Lukas Malek
# Date:     19.03.2021
# Course:   KUI 2021
# Contact:  maleklu6@fel.cvut.cz

# SUMMARY OF THE FILE
# Agent to play game Othello(Reversi). To search the tree alpha-beta pruning
# algorithm is used. The 5 second time limit is using iterative deepening to
# go as deep as possible. The heuristic is based on comparing the mobility,
# earned points and checking with the score table, so that the agent will be
# trying to get to the corner as there is huge reward. In the first phase of
# the game there are high weights for mobility, in the middle place mostly the
# score table is used, and as soon as we get the last layer, only points are
# used to get the utility.

# SOURCE
# Main source of inspiration for this assignemnt was from the webpage
# https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/RUSSIA/Final_Paper.pdf
# https://tonypoer.io/2016/10/28/implementing-minimax-and-alpha-beta-pruning-using-python/

import copy
import time


class MyPlayer():
    '''Template Docstring for MyPlayer'''

    def __init__(self, my_color, opponent_color, board_size=6):
        '''
        :param my_color: {int} of zero or one
        :param opponent_color: {int} of zero or one
        :param board_size: {int}
        '''
        self.score_table = [[
            [10, -6,  2,   2,  -6,   10],
            [-6, -8,  0,   0,  -8,  -6],
            [2,   0,  1,   1,   0,   2],
            [2,   0,  1,   1,   0,   2],
            [-6, -8,  0,   0,  -8,  -6],
            [10, -6,  2,   2,  -6,   10],
        ], [
            [10, -6,  4,  2,  2,  4, -6,  10],
            [-6, -8, -1,  0,  0, -1, -8, -6],
            [4,  -1,  1,  0,  0,  1, -1,  4],
            [2,   0,  0,  1,  1,  0,  0,  2],
            [2,   0,  0,  1,  1,  0,  0,  2],
            [4,  -1,  1,  0,  0,  1, -1,  4],
            [-6, -8, -1,  0,  0, -1, -8, -6],
            [10, -6,  4,  2,  2,  4, -6,  10],
        ], [
            [10, -6,  4,  2,  2,  2,  2,  4, -6,  10],
            [-6, -8, -2, -1, -1, -1, -1, -2, -8, -6],
            [4,  -2,  0,  2,  2,  2,  2,  0, -2,  4],
            [2,  -1,  2,  0,  1,  1,  0,  2, -1,  2],
            [2,  -1,  2,  1,  1,  1,  1,  2, -1,  2],
            [2,  -1,  2,  1,  1,  1,  1,  2, -1,  2],
            [2,  -1,  2,  0,  1,  1,  0,  2, -1,  2],
            [4,  -2,  0,  2,  2,  2,  2,  0, -2,  4],
            [-6, -8, -2, -1, -1, -1, -1, -2, -8, -6],
            [10, -6,  4,  2,  2,  2,  2,  2, -6,  10],
        ]]
        self.name = 'maleklu6'
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.empty_color = -1
        self.board_size = board_size
        self.score = self.score_table[board_size // 2 - 3]
        self.score_sum = sum([sum([abs(ele) for ele in row])
                              for row in self.score])
        self.time = time.time()
        self.depth = 0
        self.depth_limit = 1
        self.moves = 4

    def play_move(self, board, move, players_color):
        '''
        :param move: {list} of {int} for position where the move is made
        :param players_color: {int} color of who made the move
        :return: {None}
        '''
        board[move[0]][move[1]] = players_color
        dx = [-1, -1, -1, 0, 1, 1, 1, 0]
        dy = [-1, 0, 1, 1, 1, 0, -1, -1]
        for i in range(len(dx)):
            if self.confirm_direction(board, move, dx[i], dy[i], players_color):
                self.change_stones_in_direction(board,
                                                move, dx[i], dy[i], players_color)

    def is_correct_move(self, board, move, players_color):
        '''
        :param move: {list} of {int} for position
        :param players_color: {int}
        :return: {bool}
        '''
        if board[move[0]][move[1]] == self.empty_color:
            dx = [-1, -1, -1, 0, 1, 1, 1, 0]
            dy = [-1, 0, 1, 1, 1, 0, -1, -1]
            for i in range(len(dx)):
                if self.confirm_direction(board, move, dx[i], dy[i], players_color):
                    return True

        return False

    def is_position_valid(self, posx, posy):
        '''
        Check if position is in the limits of the board and non-zero.
        :param posx: {int}
        :param posy: {int}
        :return: {bool}
        '''
        return ((posx >= 0) and
                (posx < self.board_size) and
                (posy >= 0) and
                (posy < self.board_size))

    def confirm_direction(self, board, move, dx, dy, players_color):
        '''
        Looks into dirextion [dx,dy] to find if the move in this dirrection
         is correct. This means that first stone in the direction is oponents
         and last stone is players.
        :param move: position where the move is made [x,y]
        :param dx: x direction of the search
        :param dy: y direction of the search
        :param player: player that made the move
        :return: True if move in this direction is correct
        '''
        if players_color == self.my_color:
            opponents_color = self.opponent_color
        else:
            opponents_color = self.my_color

        posx = move[0] + dx
        posy = move[1] + dy
        if self.is_position_valid(posx, posy):
            if board[posx][posy] == opponents_color:
                while self.is_position_valid(posx, posy):
                    posx += dx
                    posy += dy
                    if self.is_position_valid(posx, posy):
                        if board[posx][posy] == self.empty_color:
                            return False
                        if board[posx][posy] == players_color:
                            return True

        return False

    def change_stones_in_direction(self, board, move, dx, dy, players_color):
        '''
        :param move: position as a {list} of {int}
        :param dx: {int}
        :param dy: {int}
        :param players_color: {int} of player color
        :return: {None}
        '''
        posx = move[0]+dx
        posy = move[1]+dy
        while (not(board[posx][posy] == players_color)):
            board[posx][posy] = players_color
            posx += dx
            posy += dy

    def print_board(self, board):
        '''
        Prints the board in user-friendly format
        :param board: {2D list} of {int}
        '''
        for x in range(self.board_size):
            row_string = ''
            for y in range(self.board_size):
                if board[x][y] == -1:
                    row_string += ' -'
                else:
                    row_string += ' ' + str(board[x][y])
            print(row_string)

    def get_all_valid_moves(self, board, players_color):
        '''
        :param players_color: {int} of player color
        :return: {list} of valid moves
        '''
        valid_moves = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if ((board[x][y] == -1) and
                        self.is_correct_move(board, [x, y], players_color)):
                    valid_moves.append((x, y))
        return valid_moves

    def heuristic_position(self, board):
        '''
        Calculates which player has the better position on the board based on
         the points evaluation from  the score table
        :param board: {2D list} of {int}
        :return: {int} how many points is my_player position better (-100;100)
        '''
        score = [0, 0]
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y] == self.my_color:
                    score[0] += self.score[x][y]
                if board[x][y] == self.opponent_color:
                    score[1] += self.score[x][y]
        return 100*(score[0]-score[1])/self.score_sum

    def heuristic_points(self, board):
        '''
        Compute the board score and multiply by fifty at get_utility function
        to equal the points from heuristic_position
        :param board: {2D list} of {int}
        :return: {int} how many points is my_player ahead (-100;100)
        '''
        stones = [0, 0]
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y] == self.my_color:
                    stones[0] += 1
                if board[x][y] == self.opponent_color:
                    stones[1] += 1
        return 100 * (stones[0] - stones[1]) / (stones[0] + stones[1])

    def heuristic_mobility(self, board, players_color):
        '''
        Compare the mobility of each and multiply by fifty at get_utility function
        to equal the points from heuristic_position
        :param board: {2D list} of {int}
        :return: {int} how many points is my_player ahead
        '''
        my_mobility = len(self.get_all_valid_moves(board, self.my_color))
        opponent_mobility = len(
            self.get_all_valid_moves(board, self.opponent_color))
        if (my_mobility + opponent_mobility) == 0:
            return 0
        elif players_color == self.my_color:
            return 100 * (my_mobility) / (my_mobility + opponent_mobility)
        else:
            return -100 * (opponent_mobility) / (my_mobility + opponent_mobility)

    def is_terminal(self, board):
        '''
        Check whether we reach the leaf and can stop the recursion
        :param board: {2D list} of {int}
        :return: {boolean}
        '''
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.is_correct_move(board, [x, y], self.my_color):
                    return False
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.is_correct_move(board, [x, y], self.opponent_color):
                    return False
        return True

    def get_utility(self, board, players_color):
        '''
        In the first phase of the game there are high weights for mobility, in
        the middle place mostly the score table is used, and as soon as we get
        the last layer, only points are used. Sum up the heuristic evaluation
        to one value, in the first phase of the game for each board_size there
        are different numbers of moves (for 6x6 12, for 8x8 22, for 10x10 44). 
        These numbers are the results of  the shady equation at the first elif.
        :param board: {2D list} of {int}
        :return: {int} sum of points from all heuristic function
        '''
        if self.moves + self.depth >= self.board_size ** 2:
            utility = self.heuristic_points(board)
        elif self.moves < (self.board_size ** 2 - (self.board_size-1)**2)**2/10:
            utility = 0.2 * \
                self.heuristic_position(
                    board) + 0.8 * self.heuristic_mobility(board, players_color)
        else:
            utility = 0.8 * \
                self.heuristic_position(board) + 0.2 * \
                self.heuristic_mobility(board, players_color)
        return utility

    def times_up(self):
        '''
        :return: true if the move is executing more than 4 seconds
        '''
        return True if time.time() - self.time > 4.98 else False

    def alpha_beta_search(self, board):
        '''
        Alpha-beta pruning algorithm that is time-limited to 5s per move
        :param board: {2D list} of {int}
        :return: {tuple} coordinates of the best move
        '''
        best_val = float('-inf')
        best_move = None
        beta = float('inf')
        alpha = float('-inf')
        successors = self.get_all_valid_moves(board, self.my_color)
        for move in successors:
            newboard = copy.deepcopy(board)
            self.play_move(newboard, move, self.my_color)
            value = self.min_value(newboard, alpha, beta)
            if value >= best_val:
                best_val = value
                best_move = move
        return best_move

    def max_value(self, board, alpha, beta):
        '''
        Use recursion to compute the max value of it's succeessors. Nodes
         are pruned when β ≤ α
        :param board: {2D list} of {int}
        :param move: {tuple} of coordinates x and y
        :param alpha: {int} the maximum value of successors
        :param beta: {int} the minimum value of its neigbours
        :varaible value: the value from which alpha is computed
        :return: {int} value of the terminal state or max value of successors
        '''
        self.depth += 1
        if self.is_terminal(board):
            self.depth -= 1
            return self.get_utility(board, self.my_color)
        elif self.depth >= self.depth_limit:
            self.depth -= 1
            return self.get_utility(board, self.my_color)
        elif self.times_up():
            self.depth -= 1
            return 0  # will be discarded
        value = float('-inf')
        successors = self.get_all_valid_moves(board, self.my_color)
        for move in successors:
            newboard = copy.deepcopy(board)
            self.play_move(newboard, move, self.my_color)
            value = max(value, self.min_value(newboard, alpha, beta))
            alpha = max(alpha, value)
            if beta <= alpha:
                self.depth -= 1
                return value
        self.depth -= 1
        return value

    def min_value(self, board, alpha, beta):
        '''
        Use recursion to compute the min value of it's succeessors. Nodes
         are pruned when β ≤ α
        :param board: {2D list} of {int}
        :param move: {tuple} of coordinates x and y
        :param alpha: {int} the maximum value of its neigbours
        :param beta: {int} the minimum value of successors
        :varaible value: the value from which beta is computed
        :return: {int} value of the terminal state or min value of successors
        '''
        self.depth += 1
        if self.is_terminal(board):
            self.depth -= 1
            return self.get_utility(board, self.opponent_color)
        elif self.depth >= self.depth_limit:
            self.depth -= 1
            return self.get_utility(board, self.opponent_color)
        elif self.times_up():
            self.depth -= 1
            return 0  # will be discarded
        value = float('inf')
        successors = self.get_all_valid_moves(board, self.opponent_color)
        for move in successors:
            newboard = copy.deepcopy(board)
            self.play_move(newboard, move, self.opponent_color)
            value = min(value, self.max_value(newboard, alpha, beta))
            beta = min(beta, value)
            if beta <= alpha:
                self.depth -= 1
                return value
        self.depth -= 1
        return value

    def move(self, board):
        '''
        Used iterative deepening, increase a depth by one till the time is up
        :param board: {2D list} of {int}
        :return: best move based on aplha-beta algroithm
        '''
        self.time = time.time()
        self.depth_limit = 1
        while True:
            current_move = self.alpha_beta_search(board)
            if self.times_up():
                break
            best_move = current_move
            self.depth_limit += 1
        self.moves += 2
        return best_move

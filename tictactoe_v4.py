import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class Environment:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        return self.board

    def make_move(self, row, col, symbol):
        if self.board[row][col] is None:
            self.board[row][col] = symbol
            return True
        return False

    def is_winner(self, symbol):
        for i in range(3):
            if all(self.board[i][j] == symbol for j in range(3)) or all(self.board[j][i] == symbol for j in range(3)):
                return True
        if all(self.board[i][i] == symbol for i in range(3)) or all(self.board[i][2 - i] == symbol for i in range(3)):
            return True
        return False

    def is_draw(self):
        return all(self.board[i][j] is not None for i in range(3) for j in range(3))

class AIPlayer:
    def __init__(self):
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2

    def get_state(self, board):
        return tuple(tuple(row) for row in board)

    def choose_action(self, board):
        state = self.get_state(board)
        
        # Default random choice or Q-learning based action
        if random.uniform(0, 1) < self.epsilon or state not in self.q_table:
            return random.choice([(i, j) for i in range(3) for j in range(3) if board[i][j] is None])
        return max(self.q_table[state], key=self.q_table[state].get)

    def update_q_value(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0
        print('\n\n')
        future_rewards = max(self.q_table.get(next_state, {}).values(), default=0)
        print(f"State: {state}, Action: {action}, Reward: {reward}, Future Rewards: {future_rewards}")
        print('\n\n')
        self.q_table[state][action] += self.alpha * (reward + self.gamma * future_rewards - self.q_table[state][action])
        print(self.q_table)

class TicTacToeApp:
    def __init__(self):
        self.environment = Environment()
        self.ai_player_1 = AIPlayer()  # First AI player
        self.ai_player_2 = AIPlayer()  # Second AI player
        self.stats = []  # To store win rates over time
        self.games_played = 0
        self.total_games = 10000

        self.root = tk.Tk()
        self.root.title("Tic Tac Toe AI vs AI Bot Game")

        self.setup_ui()
        self.setup_graph()

    def setup_ui(self):
        self.board_buttons = [[tk.Button(self.root, text="", font="Arial 20", width=5, height=2)
                               for _ in range(3)] for _ in range(3)]

        for row in range(3):
            for col in range(3):
                self.board_buttons[row][col].grid(row=row, column=col)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_game)
        self.reset_button.grid(row=3, column=0, columnspan=3, pady=10)

    def setup_graph(self):
        self.figure, self.ax = plt.subplots()
        self.ax.set_title("AI Learning Progress")
        self.ax.set_xlabel("Games Played")
        self.ax.set_ylabel("Win Rate")

        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=3)

    def update_graph(self):
        self.ax.clear()
        self.ax.set_title("AI Learning Progress")
        self.ax.set_xlabel("Games Played")
        self.ax.set_ylabel("AI Player 1 Win Percentage")

        # Calculate win percentage
        cumulative_wins = [sum(self.stats[:i+1]) for i in range(len(self.stats))]
        win_percentages = [wins / (i + 1) * 100 for i, wins in enumerate(cumulative_wins)]

        self.ax.plot(range(len(win_percentages)), win_percentages, label="AI Player 1 Win %", color="blue")
        self.ax.legend()
        self.canvas.draw()

    def reset_game(self):
        self.environment.reset()
        for row in range(3):
            for col in range(3):
                self.board_buttons[row][col].config(text="", state=tk.NORMAL)

    def play_turn(self, ai_player, symbol):
        state = ai_player.get_state(self.environment.board)
        action = ai_player.choose_action(self.environment.board)
        
        self.environment.make_move(action[0], action[1], symbol)
        self.board_buttons[action[0]][action[1]].config(text=symbol)
        
        reward = 0
        if self.environment.is_winner(symbol):
            reward = 1
        elif self.environment.is_draw():
            reward = 0.5

        next_state = ai_player.get_state(self.environment.board)
        ai_player.update_q_value(state, action, reward, next_state)

        return reward

    def play_game(self):
        self.reset_game()

        def game_loop():
            nonlocal turn

            if turn % 2 == 0:  # AI 1's turn
                reward = self.play_turn(self.ai_player_1, "X")
                if reward == 1:  # AI 1 wins
                    self.stats.append(1)
                    self.update_graph()
                    self.games_played += 1
                    self.check_game_limit()
                    return
                elif reward == 0.5:  # Draw
                    self.stats.append(0.5)
                    self.update_graph()
                    self.games_played += 1
                    self.check_game_limit()
                    return

            else:  # AI 2's turn
                reward = self.play_turn(self.ai_player_2, "O")
                if reward == 1:  # AI 2 wins
                    self.stats.append(0)
                    self.update_graph()
                    self.games_played += 1
                    self.check_game_limit()
                    return
                elif reward == 0.5:  # Draw
                    self.stats.append(0.5)
                    self.update_graph()
                    self.games_played += 1
                    self.check_game_limit()
                    return

            turn += 1
            self.root.after(500, game_loop)

        turn = 0
        game_loop()

    def check_game_limit(self):
        if self.games_played < self.total_games:
            self.play_game()
        else:
            messagebox.showinfo("Game Over", "Simulation completed for 1000 games!")

    def run(self):
        self.play_game()
        self.root.mainloop()

if __name__ == "__main__":
    app = TicTacToeApp()
    app.run()

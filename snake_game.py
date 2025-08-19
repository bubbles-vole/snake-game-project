#!/usr/bin/env python3

import curses
import random
import time
import json
import re
import os
import traceback
import sys
from datetime import datetime
import platform

class SnakeGame:
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.difficulty = 'easy'
        self.obstacles = []
        self.last_move_time = time.time()
        self.move_interval = 1.0  # Move once per second
        self.leaderboard_file = 'leaderboard.json'
        
    def setup_screen(self, stdscr):
        """Initialize the game screen"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Don't wait for input
        
        # Get screen dimensions
        self.height, self.width = stdscr.getmaxyx()
        
        # Create a window for the game
        self.win = curses.newwin(self.height, self.width, 0, 0)
        self.win.keypad(1)
        self.win.nodelay(1)  # Make input non-blocking for the game window
        self.win.border(0)
        
        # Create obstacles based on difficulty
        self.create_obstacles()
        
        # Initialize snake in the middle of screen
        self.snake = [
            [self.height//2, self.width//2],
            [self.height//2, self.width//2-1],
            [self.height//2, self.width//2-2]
        ]
        
        # Create first food
        self.create_food()
        
        # Initial direction (moving right)
        self.direction = curses.KEY_RIGHT
        
        # Set move speed based on difficulty
        if self.difficulty == 'easy':
            self.move_interval = 0.6
        elif self.difficulty == 'medium':
            self.move_interval = 0.3
        elif self.difficulty == 'hard':
            self.move_interval = 0.2
        elif self.difficulty == 'insane':
            self.move_interval = 0.05
        
    def create_obstacles(self):
        """Create obstacles based on difficulty"""
        self.obstacles = []
        
        if self.difficulty == 'medium':
            # Add some wall obstacles
            obstacle_count = 5
        elif self.difficulty == 'hard':
            # Add more obstacles
            obstacle_count = 10
        elif self.difficulty == 'insane':
            # Add many obstacles
            obstacle_count = 15
        else:
            # Easy mode - no obstacles
            return
            
        for _ in range(obstacle_count):
            while True:
                obstacle = [
                    random.randint(2, self.height-3),
                    random.randint(2, self.width-3)
                ]
                # Make sure obstacle doesn't overlap with snake starting position
                if (obstacle not in [[self.height//2, self.width//2],
                                   [self.height//2, self.width//2-1],
                                   [self.height//2, self.width//2-2]] and
                    obstacle not in self.obstacles):
                    self.obstacles.append(obstacle)
                    break
                    
    def create_food(self):
        """Create food at random location"""
        while True:
            self.food = [
                random.randint(1, self.height-2),
                random.randint(1, self.width-2)
            ]
            # Make sure food doesn't appear on snake or obstacles
            if (self.food not in self.snake and 
                self.food not in self.obstacles):
                break
                
    def draw_snake(self):
        """Draw the snake on screen"""
        for i, segment in enumerate(self.snake):
            if i == 0:  # Head of snake
                self.win.addch(segment[0], segment[1], '@')
            else:  # Body of snake
                self.win.addch(segment[0], segment[1], '*')
                
    def draw_obstacles(self):
        """Draw obstacles on screen"""
        for obstacle in self.obstacles:
            self.win.addch(obstacle[0], obstacle[1], '█')
            
    def draw_food(self):
        """Draw food on screen"""
        self.win.addch(self.food[0], self.food[1], '#')
        
    def draw_score(self):
        """Draw score on screen"""
        score_text = f"Score: {self.score}"
        self.win.addstr(0, 2, score_text)
        
    def move_snake(self):
        """Move snake in current direction"""
        head = self.snake[0]
        
        if self.direction == curses.KEY_UP:
            new_head = [head[0]-1, head[1]]
        elif self.direction == curses.KEY_DOWN:
            new_head = [head[0]+1, head[1]]
        elif self.direction == curses.KEY_LEFT:
            new_head = [head[0], head[1]-1]
        elif self.direction == curses.KEY_RIGHT:
            new_head = [head[0], head[1]+1]
        else:
            new_head = head
            
        # Insert new head
        self.snake.insert(0, new_head)
        
        # Check if food was eaten
        if new_head == self.food:
            self.score += 10
            self.create_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()
            
    def check_collision(self):
        """Check for collisions"""
        head = self.snake[0]
        
        # Check wall collision
        if (head[0] in [0, self.height-1] or 
            head[1] in [0, self.width-1]):
            return True
            
        # Check self collision
        if head in self.snake[1:]:
            return True
            
        # Check obstacle collision
        if head in self.obstacles:
            return True
            
        return False
        
    def get_input(self):
        """Get user input"""
        key = self.win.getch()
        
        # Handle input only if a key was actually pressed
        if key != -1:  # -1 means no key pressed
            # Arrow key controls
            if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                # Check if pressing same direction as current movement
                if key == self.direction:
                    # Force immediate movement in current direction
                    return 'force_move'
                # Prevent snake from going back into itself
                elif (key == curses.KEY_UP and self.direction != curses.KEY_DOWN or
                      key == curses.KEY_DOWN and self.direction != curses.KEY_UP or
                      key == curses.KEY_LEFT and self.direction != curses.KEY_RIGHT or
                      key == curses.KEY_RIGHT and self.direction != curses.KEY_LEFT):
                    # Change direction and force immediate move
                    self.direction = key
                    return 'force_move'
                    
            # Quit game
            if key == ord('q') or key == 27:  # 'q' or ESC
                self.game_over = True
                
        return None
    
    def load_leaderboard(self):
        """Load leaderboard from JSON file"""
        try:
            with open(self.leaderboard_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default leaderboard if file doesn't exist or is corrupted
            return {"easy": [], "medium": [], "hard": [], "insane": []}
    
    def save_leaderboard(self, leaderboard):
        """Save leaderboard to JSON file"""
        try:
            with open(self.leaderboard_file, 'w') as f:
                json.dump(leaderboard, f, indent=2)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
    
    def is_high_score(self, score, difficulty):
        """Check if the score qualifies for the leaderboard"""
        leaderboard = self.load_leaderboard()
        difficulty_scores = leaderboard.get(difficulty, [])
        
        # Always qualify if less than 10 scores
        if len(difficulty_scores) < 10:
            return True
        
        # Check if score is higher than the lowest score
        lowest_score = min(entry['score'] for entry in difficulty_scores)
        return score > lowest_score
    
    def add_high_score(self, name, score, difficulty):
        """Add a high score to the leaderboard"""
        leaderboard = self.load_leaderboard()
        
        # Add new score
        new_entry = {"name": name, "score": score}
        leaderboard[difficulty].append(new_entry)
        
        # Sort by score (descending) and keep only top 10
        leaderboard[difficulty].sort(key=lambda x: x['score'], reverse=True)
        leaderboard[difficulty] = leaderboard[difficulty][:10]
        
        # Save updated leaderboard
        self.save_leaderboard(leaderboard)
    
    def get_player_name(self, stdscr):
        """Get player name for high score entry with input validation"""
        stdscr.nodelay(0)  # Make input blocking for name entry
        curses.curs_set(1)  # Show cursor
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Display prompts
            congrats = "NEW HIGH SCORE!"
            prompt = "Enter your name:"
            note = "(Only letters and numbers allowed, max 20 characters)"
            
            stdscr.addstr(height//2-3, (width-len(congrats))//2, congrats)
            stdscr.addstr(height//2-1, (width-len(prompt))//2, prompt)
            stdscr.addstr(height//2, (width-len(note))//2, note)
            
            # Input area - create a small input box
            input_y = height//2 + 2
            input_x = (width - 22) // 2  # Center a 20-char input field
            stdscr.addstr(input_y, input_x-2, "> ")
            
            # Draw input box
            for i in range(22):
                stdscr.addch(input_y, input_x + i, '_')
            
            stdscr.move(input_y, input_x)
            stdscr.refresh()
            
            # Get input with echo enabled
            curses.echo()
            curses.curs_set(1)
            try:
                # Use a simpler input method
                name = ""
                while len(name) < 20:
                    ch = stdscr.getch()
                    if ch == 10 or ch == 13:  # Enter key
                        break
                    elif ch == 127 or ch == curses.KEY_BACKSPACE:  # Backspace
                        if name:
                            name = name[:-1]
                            stdscr.move(input_y, input_x + len(name))
                            stdscr.addch('_')
                            stdscr.move(input_y, input_x + len(name))
                    elif ch >= 32 and ch <= 126:  # Printable characters
                        char = chr(ch)
                        if char.isalnum():  # Only allow alphanumeric
                            name += char
                            stdscr.addch(char)
                    stdscr.refresh()
            except:
                name = ""
            finally:
                curses.noecho()
                curses.curs_set(0)
            
            # Validate input
            if re.match(r'^[a-zA-Z0-9]+$', name) and 1 <= len(name) <= 20:
                stdscr.nodelay(1)  # Restore non-blocking input
                return name.upper()
            else:
                # Show error message
                stdscr.clear()
                stdscr.addstr(height//2-3, (width-len(congrats))//2, congrats)
                error = "Invalid name! Please try again."
                reason = "Name must contain only letters and numbers (1-20 characters)"
                stdscr.addstr(height//2-1, (width-len(error))//2, error)
                stdscr.addstr(height//2, (width-len(reason))//2, reason)
                stdscr.addstr(height//2+2, (width-25)//2, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
    
    def show_leaderboard(self, stdscr):
        """Display the leaderboard"""
        leaderboard = self.load_leaderboard()
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            title = "HIGH SCORES"
            stdscr.addstr(2, (width-len(title))//2, title)
            
            # Display scores for each difficulty
            y_pos = 4
            for difficulty in ['easy', 'medium', 'hard', 'insane']:
                diff_title = f"{difficulty.upper()} DIFFICULTY"
                if y_pos < height - 2:
                    stdscr.addstr(y_pos, (width-len(diff_title))//2, diff_title)
                    y_pos += 1
                
                scores = leaderboard.get(difficulty, [])
                if not scores:
                    no_scores = "No scores yet"
                    if y_pos < height - 2:
                        stdscr.addstr(y_pos, (width-len(no_scores))//2, no_scores)
                        y_pos += 2
                else:
                    for i, entry in enumerate(scores[:5]):  # Show top 5 per difficulty
                        if y_pos < height - 2:
                            score_line = f"{i+1:2}. {entry['name']:<15} {entry['score']:>6}"
                            stdscr.addstr(y_pos, (width-len(score_line))//2, score_line)
                            y_pos += 1
                    y_pos += 1
            
            # Instructions
            if y_pos < height - 2:
                instructions = "Press any key to return to menu"
                stdscr.addstr(height-2, (width-len(instructions))//2, instructions)
            
            stdscr.refresh()
            stdscr.getch()
            break
            
    def show_main_menu(self, stdscr):
        """Show main menu"""
        while True:
            curses.curs_set(0)
            stdscr.clear()
            
            height, width = stdscr.getmaxyx()
            
            # Menu options
            title = "SNAKE GAME"
            options = [
                "1. Play Game",
                "2. High Scores",
                "3. Quit"
            ]
            instructions = "Press 1, 2, or 3 to select option"
            
            # Display menu
            stdscr.addstr(height//2-3, (width-len(title))//2, title)
            
            for i, option in enumerate(options):
                stdscr.addstr(height//2+i-1, (width-len(option))//2, option)
                
            stdscr.addstr(height//2+4, (width-len(instructions))//2, instructions)
            stdscr.refresh()
            
            # Get user selection
            key = stdscr.getch()
            if key == ord('1'):
                # Play game - show difficulty selection
                if self.show_difficulty_menu(stdscr):
                    return 'play'
            elif key == ord('2'):
                # Show high scores
                self.show_leaderboard(stdscr)
            elif key == ord('3') or key == ord('q') or key == 27:
                return 'quit'
    
    def show_difficulty_menu(self, stdscr):
        """Show difficulty selection menu"""
        curses.curs_set(0)
        stdscr.clear()
        
        height, width = stdscr.getmaxyx()
        
        # Menu options
        title = "SELECT DIFFICULTY"
        options = [
            "1. Easy (No obstacles, 0.6s speed)",
            "2. Medium (5 obstacles, 0.3s speed)", 
            "3. Hard (10 obstacles, 0.2s speed)",
            "4. Insane (15 obstacles, 0.05s speed)"
        ]
        instructions = "Press 1, 2, 3, or 4 to select difficulty, ESC to return"
        
        # Display menu
        stdscr.addstr(height//2-4, (width-len(title))//2, title)
        
        for i, option in enumerate(options):
            stdscr.addstr(height//2+i-1, (width-len(option))//2, option)
            
        stdscr.addstr(height//2+5, (width-len(instructions))//2, instructions)
        stdscr.refresh()
        
        # Get user selection
        while True:
            key = stdscr.getch()
            if key == ord('1'):
                self.difficulty = 'easy'
                return True
            elif key == ord('2'):
                self.difficulty = 'medium'
                return True
            elif key == ord('3'):
                self.difficulty = 'hard'
                return True
            elif key == ord('4'):
                self.difficulty = 'insane'
                return True
            elif key == 27:  # ESC
                return False
        
    def play_game(self, stdscr):
        """Play a single game"""
        # Reset game state
        self.score = 0
        self.game_over = False
        self.last_move_time = time.time()
        
        self.setup_screen(stdscr)
        
        # Wrap in try/except for crash reporting
        try:
            # Draw initial game state
            self.win.border(0)
            self.draw_snake()
            self.draw_obstacles()
            self.draw_food()
            self.draw_score()
        except Exception as e:
            curses.endwin()
            raise e
        
        try:
            # Draw initial game state
            self.win.border(0)
            self.draw_snake()
            self.draw_obstacles()
            self.draw_food()
            self.draw_score()
            difficulty_text = f"Difficulty: {self.difficulty.capitalize()}"
            self.win.addstr(0, self.width-len(difficulty_text)-2, difficulty_text)
            instructions = "Arrow keys: change/boost direction, 'q': quit"
            self.win.addstr(self.height-1, 2, instructions[:self.width-4])
            self.win.refresh()
        except Exception as e:
            curses.endwin()
            raise e
        
        while not self.game_over:
            try:
                current_time = time.time()
                
                # Get input (non-blocking) - check for forced movement
                input_result = self.get_input()
            except Exception as e:
                curses.endwin()
                raise e
            
            # Check if we should move (either automatic timing or forced)
            should_move = False
            
            # Automatic movement based on time interval
            if current_time - self.last_move_time >= self.move_interval:
                should_move = True
                
            # Forced movement when pressing direction keys
            elif input_result == 'force_move':
                # Prevent too rapid forced moves (minimum 0.05 seconds between moves)
                if current_time - self.last_move_time >= 0.05:
                    should_move = True
            
            if should_move:
                try:
                    # Store old tail position before moving
                    old_tail = self.snake[-1].copy() if len(self.snake) > 1 else None
                    
                    # Move snake
                    self.move_snake()
                    
                    # Check collisions
                    if self.check_collision():
                        break
                    
                    # Only clear the old tail position if snake didn't grow
                    if old_tail and len(self.snake) > 1 and old_tail not in self.snake:
                        self.win.addch(old_tail[0], old_tail[1], ' ')
                    
                    # Draw new head
                    head = self.snake[0]
                    self.win.addch(head[0], head[1], '@')
                    
                    # Update body (previous head becomes body)
                    if len(self.snake) > 1:
                        prev_head = self.snake[1]
                        self.win.addch(prev_head[0], prev_head[1], '*')
                    
                    # Draw food
                    self.draw_food()
                    
                    # Update score and difficulty display
                    self.draw_score()
                    difficulty_text = f"Difficulty: {self.difficulty.capitalize()}"
                    self.win.addstr(0, self.width-len(difficulty_text)-2, difficulty_text)
                    
                    # Update last move time
                    self.last_move_time = current_time
                    
                    # Refresh screen after movement
                    self.win.refresh()
                except Exception as e:
                    curses.endwin()
                    raise e
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)
            
        # Game over - handle high scores
        try:
            self.show_game_over(stdscr)
        except Exception as e:
            curses.endwin()
            raise e
    
    def game_loop(self, stdscr):
        """Main game loop with menu system"""
        while True:
            menu_choice = self.show_main_menu(stdscr)
            
            if menu_choice == 'play':
                self.play_game(stdscr)
            elif menu_choice == 'quit':
                break
        
    def show_game_over(self, stdscr):
        """Show game over screen and handle high scores"""
        # Check if this is a high score
        if self.is_high_score(self.score, self.difficulty):
            # Get player name and add to leaderboard
            player_name = self.get_player_name(stdscr)
            self.add_high_score(player_name, self.score, self.difficulty)
        
        # Show game over screen
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        game_over_text = "GAME OVER!"
        final_score = f"Final Score: {self.score}"
        difficulty_text = f"Difficulty: {self.difficulty.capitalize()}"
        return_text = "Press any key to return to main menu"
        
        # Center the text
        stdscr.addstr(height//2-2, (width-len(game_over_text))//2, game_over_text)
        stdscr.addstr(height//2-1, (width-len(final_score))//2, final_score)
        stdscr.addstr(height//2, (width-len(difficulty_text))//2, difficulty_text)
        stdscr.addstr(height//2+2, (width-len(return_text))//2, return_text)
        
        stdscr.refresh()
        stdscr.getch()  # Wait for any key press
        
def generate_crash_report(game, exception, exc_traceback):
    """Generate a detailed crash report file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure logs directory exists
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
        except Exception:
            logs_dir = "."  # Fallback to current directory
    
    crash_filename = os.path.join(logs_dir, f"snake_game_crash_{timestamp}.txt")
    
    try:
        with open(crash_filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("SNAKE GAME CRASH REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            # Timestamp
            f.write(f"Crash Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # System Information
            f.write("SYSTEM INFORMATION:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Platform: {platform.platform()}\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Operating System: {platform.system()} {platform.release()}\n")
            f.write(f"Machine: {platform.machine()}\n")
            f.write(f"Processor: {platform.processor()}\n\n")
            
            # Game State Information
            f.write("GAME STATE AT CRASH:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Score: {getattr(game, 'score', 'Unknown')}\n")
            f.write(f"Difficulty: {getattr(game, 'difficulty', 'Unknown')}\n")
            f.write(f"Game Over: {getattr(game, 'game_over', 'Unknown')}\n")
            
            if hasattr(game, 'height') and hasattr(game, 'width'):
                f.write(f"Screen Dimensions: {game.height}x{game.width}\n")
            
            if hasattr(game, 'snake'):
                f.write(f"Snake Length: {len(game.snake)}\n")
                f.write(f"Snake Head Position: {game.snake[0] if game.snake else 'Unknown'}\n")
                f.write(f"Snake Body: {game.snake[:5]}{'...' if len(game.snake) > 5 else ''}\n")
            
            if hasattr(game, 'direction'):
                direction_map = {
                    curses.KEY_UP: 'UP',
                    curses.KEY_DOWN: 'DOWN', 
                    curses.KEY_LEFT: 'LEFT',
                    curses.KEY_RIGHT: 'RIGHT'
                }
                f.write(f"Current Direction: {direction_map.get(game.direction, game.direction)}\n")
            
            if hasattr(game, 'move_interval'):
                f.write(f"Move Interval: {game.move_interval}s\n")
            
            if hasattr(game, 'food'):
                f.write(f"Food Position: {game.food}\n")
            
            if hasattr(game, 'obstacles'):
                f.write(f"Number of Obstacles: {len(game.obstacles)}\n")
                if game.obstacles:
                    f.write(f"Obstacle Positions: {game.obstacles[:10]}{'...' if len(game.obstacles) > 10 else ''}\n")
            
            f.write("\n")
            
            # Exception Information
            f.write("EXCEPTION DETAILS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Exception Type: {type(exception).__name__}\n")
            f.write(f"Exception Message: {str(exception)}\n\n")
            
            # Full Stack Trace
            f.write("FULL STACK TRACE:\n")
            f.write("-" * 30 + "\n")
            f.write(''.join(traceback.format_exception(type(exception), exception, exc_traceback)))
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("END OF CRASH REPORT\n")
            f.write("=" * 60 + "\n")
        
        return crash_filename
    except Exception as report_error:
        try:
            minimal_filename = os.path.join(logs_dir, f"snake_game_crash_minimal_{timestamp}.txt")
            with open(minimal_filename, 'w') as f:
                f.write(f"Snake Game crashed at {datetime.now()}\n")
                f.write(f"Original exception: {exception}\n")
                f.write(f"Crash report generation failed: {report_error}\n")
                f.write(f"Report error: {traceback.format_exc()}\n")
            return minimal_filename
        except Exception as final_error:
            # Last resort - try to write to current directory
            try:
                emergency_filename = f"snake_crash_emergency_{timestamp}.txt"
                with open(emergency_filename, 'w') as f:
                    f.write(f"Emergency crash log: {datetime.now()}\n")
                    f.write(f"Original exception: {str(exception)}\n")
                    f.write(f"Report generation failed: {str(report_error)}\n")
                    f.write(f"Final error: {str(final_error)}\n")
                return emergency_filename
            except:
                return None

def main():
    """Main function to start the game"""
    game = SnakeGame()
    crash_report_file = None
    
    try:
        # Add immediate exception handling wrapper
        def wrapped_game_loop(stdscr):
            try:
                game.game_loop(stdscr)
            except Exception as inner_e:
                curses.endwin()  # Ensure terminal is restored
                raise inner_e
        
        curses.wrapper(wrapped_game_loop)
    except KeyboardInterrupt:
        print("\n🛑 Game interrupted by user (Ctrl+C)")
    except Exception as e:
        # Always try to generate crash report, even if game object is incomplete
        try:
            crash_report_file = generate_crash_report(game, e, sys.exc_info()[2])
        except Exception as report_gen_error:
            print(f"\n💥 Double fault: Crash report generation also failed!")
            print(f"Report error: {report_gen_error}")
            # Try to create a super minimal crash log
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                emergency_file = f"logs/emergency_crash_{timestamp}.txt" if os.path.exists("logs") else f"emergency_crash_{timestamp}.txt"
                with open(emergency_file, 'w') as f:
                    f.write(f"EMERGENCY CRASH LOG - {datetime.now()}\n")
                    f.write(f"Original crash: {type(e).__name__}: {e}\n")
                    f.write(f"Report generation error: {report_gen_error}\n")
                    f.write(f"Full trace:\n{traceback.format_exc()}\n")
                crash_report_file = emergency_file
            except:
                pass
        
        print(f"\n❌ Snake Game crashed unexpectedly!")
        print(f"Exception: {type(e).__name__}: {e}")
        
        if crash_report_file:
            print(f"\n📝 Crash report saved to: {crash_report_file}")
            print("Please check this file for detailed information about the crash.")
        else:
            print(f"\n⚠️  Could not generate crash report file.")
            print(f"\n🔍 Debug info:")
            print(f"   Current working directory: {os.getcwd()}")
            print(f"   Logs directory exists: {os.path.exists('logs')}")
            print(f"   Can write to current dir: {os.access('.', os.W_OK)}")
        
        print("\nSimplified error trace:")
        traceback.print_exc(limit=3)
        
        return  # Exit without showing normal completion message
    
    # Only show this if game completed normally
    if hasattr(game, 'score'):
        print(f"\nThanks for playing! Final score: {game.score}")
    else:
        print(f"\nThanks for playing!")

if __name__ == "__main__":
    main()


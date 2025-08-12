# Snake Game

A terminal-based Snake game implemented in Python using the curses library.

## Features

### Game Modes
- **Easy**: No obstacles, slower speed (0.6s interval)
- **Medium**: 5 obstacles, medium speed (0.3s interval)  
- **Hard**: 10 obstacles, fast speed (0.2s interval)
- **Insane**: 15 obstacles, very fast speed (0.05s interval)

### Scoreboard System
- Tracks top 10 high scores for each difficulty level
- Automatic high score detection when game ends
- Player name entry with validation (alphanumeric only, max 20 characters)
- Persistent storage in `leaderboard.json`
- View high scores from main menu

### Menu System
- Main menu with Play Game, High Scores, and Quit options
- Difficulty selection before each game
- Proper navigation with ESC keys
- Game returns to menu after completion (no more "disappearing")

## How to Play

### Installation
1. Ensure you have Python 3 installed
2. The game uses the built-in `curses` library (available on macOS/Linux)
3. Run: `python3 snake_game.py`

### Controls
- **Arrow Keys**: Change snake direction or boost movement
- **Q** or **ESC**: Quit current game
- **Enter**: Confirm selections in menus
- **1-4**: Select menu options
- **ESC**: Return to previous menu

### Gameplay
1. Control the snake (@) to eat food (#)
2. Each food eaten increases score by 10 points
3. Avoid hitting walls, obstacles (█), or your own body
4. Snake grows longer with each food eaten
5. Game speed increases with difficulty level

### High Scores
- Qualify for leaderboard by scoring higher than existing top 10
- Enter your name when achieving a high score
- Names must be alphanumeric characters only (letters and numbers)
- Maximum 20 characters, automatically converted to uppercase
- View all high scores organized by difficulty level

## File Structure

- `snake_game.py` - Main game file
- `leaderboard.json` - High scores storage (created automatically)
- `README.md` - This documentation

## Technical Notes

- Uses Python's `curses` library for terminal UI
- Non-blocking input for smooth gameplay
- JSON-based persistent storage for high scores
- Input validation with regex patterns
- Proper resource cleanup and error handling

## Development

### Git Workflow
- Main development on `feature/scoreboard-system` branch
- Merge to `main` when ready for release

### Features Added in This Version
- Complete scoreboard system with persistent storage
- Enhanced menu system with proper navigation
- Input validation for player names
- Game over flow returns to main menu
- Quit option directly from main menu
- Visual improvements for better user experience

## Troubleshooting

### Common Issues
- **Flashing text during name entry**: Fixed in latest version with proper cursor handling
- **Game disappears after losing**: Now returns to main menu properly
- **Can't see input**: Ensure terminal supports cursor display

### Requirements
- Python 3.x
- Terminal with curses support (macOS Terminal, Linux terminals)
- Minimum terminal size: 40x20 characters recommended

## Future Enhancements

Potential features for future versions:
- Sound effects
- Color themes
- Additional difficulty levels
- Online leaderboards
- Multiplayer support
- Custom obstacle patterns

---

Enjoy the game! 🐍

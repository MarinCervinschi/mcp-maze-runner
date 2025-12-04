"""
MCP Maze Runner - Terminal Game

A simple terminal-based maze game with emoji graphics.
Navigate from start to exit, collecting keys along the way.
"""

import os

from src.game import Game


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


# Emoji mappings for maze elements
EMOJI_MAP = {
    "#": "🧱",  # Wall
    ".": "  ",  # Empty (double space for alignment)
    "S": "🚩",  # Start
    "E": "🚪",  # Exit
    "K": "🔑",  # Key
    "@": "🧙",  # Player
    "?": "⬛",  # Unknown (fog of war)
    "·": "░░",  # Visited but not visible
}


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def render_emoji_maze(maze_str: str) -> str:
    """Convert ASCII maze to emoji representation."""
    lines = []
    for line in maze_str.split("\n"):
        emoji_line = ""
        for char in line:
            emoji_line += EMOJI_MAP.get(char, char + " ")
        lines.append(emoji_line)
    return "\n".join(lines)


def print_header(game: Game, message: str = "") -> None:
    """Print the game header with status info."""
    state = game.get_state()
    player = state["player"]
    maze_info = state["maze"]

    print(
        f"{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════╗{Colors.RESET}"
    )
    print(
        f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}🏃 MAZE RUNNER{Colors.RESET}                                         {Colors.BOLD}{Colors.CYAN}║{Colors.RESET}"
    )
    print(
        f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.RESET}"
    )
    print()

    # Status bar
    keys_display = f"🔑 {player['keys_collected']}/{maze_info['total_keys']}"
    moves_display = f"👣 {player['moves_made']}"
    pos_display = f"📍 ({player['position']['x']},{player['position']['y']})"

    print(f"  {keys_display}    {moves_display}    {pos_display}")
    print()

    # Message
    if message:
        if "wall" in message.lower() or "cannot" in message.lower():
            print(f"  {Colors.RED}❌ {message}{Colors.RESET}")
        elif "key" in message.lower():
            print(f"  {Colors.YELLOW}✨ {message}{Colors.RESET}")
        elif "exit" in message.lower() or "won" in message.lower():
            print(f"  {Colors.GREEN}🎉 {message}{Colors.RESET}")
        else:
            print(f"  {Colors.GREEN}✓ {message}{Colors.RESET}")
        print()


def print_legend() -> None:
    """Print a compact legend."""
    print(f"  {Colors.DIM}───────────────────────────────{Colors.RESET}")
    print(f"  {Colors.DIM}🧙 You  🚩 Start  🚪 Exit  🔑 Key  🧱 Wall{Colors.RESET}")
    print(f"  {Colors.DIM}↑/w up  ↓/s down  ←/a left  →/d right{Colors.RESET}")
    print(f"  {Colors.DIM}help · reset · quit{Colors.RESET}")
    print()


def print_game_screen(game: Game, message: str = "") -> None:
    """Print the complete game screen."""
    clear_screen()
    print_header(game, message)

    # Render maze with emojis
    maze_display = game.get_maze_display()
    emoji_maze = render_emoji_maze(maze_display)

    # Add padding to center the maze
    for line in emoji_maze.split("\n"):
        print(f"  {line}")

    print()
    print_legend()


def print_help() -> None:
    """Print help information."""
    clear_screen()
    print(
        f"""
{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║                    MAZE RUNNER HELP                      ║
╠══════════════════════════════════════════════════════════╣{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Movement:{Colors.RESET}                                             {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    {Colors.YELLOW}↑  up, u, w{Colors.RESET}     - Move up                         {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    {Colors.YELLOW}↓  down, d, s{Colors.RESET}   - Move down                       {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    {Colors.YELLOW}←  left, l, a{Colors.RESET}   - Move left                       {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    {Colors.YELLOW}→  right, r{Colors.RESET}     - Move right                      {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}                                                          {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Commands:{Colors.RESET}                                             {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    {Colors.GREEN}help, h, ?{Colors.RESET}      - Show this help                   {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    {Colors.GREEN}reset{Colors.RESET}           - Restart the game                 {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    {Colors.GREEN}quit, q{Colors.RESET}         - Exit the game                    {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}                                                          {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}Legend:{Colors.RESET}                                               {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    🧙  You (the player)                                  {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    🚩  Start position                                    {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    🚪  Exit (your goal!)                                 {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    🔑  Key (collect these!)                              {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}    🧱  Wall                                              {Colors.CYAN}║{Colors.RESET}
{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    )
    input(f"  {Colors.DIM}Press Enter to continue...{Colors.RESET}")


def print_welcome() -> None:
    """Print welcome screen."""
    clear_screen()
    print(
        f"""
{Colors.BOLD}{Colors.CYAN}
    ███╗   ███╗ █████╗ ███████╗███████╗
    ████╗ ████║██╔══██╗╚══███╔╝██╔════╝
    ██╔████╔██║███████║  ███╔╝ █████╗  
    ██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝  
    ██║ ╚═╝ ██║██║  ██║███████╗███████╗
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
    
    ██████╗ ██╗   ██╗███╗   ██╗███╗   ██╗███████╗██████╗ 
    ██╔══██╗██║   ██║████╗  ██║████╗  ██║██╔════╝██╔══██╗
    ██████╔╝██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
    ██╔══██╗██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
    ██║  ██║╚██████╔╝██║ ╚████║██║ ╚████║███████╗██║  ██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
{Colors.RESET}
    {Colors.YELLOW}Navigate from 🚩 to 🚪 and collect 🔑 along the way!{Colors.RESET}
    
    {Colors.DIM}Type 'help' for controls{Colors.RESET}
"""
    )
    input(f"  {Colors.DIM}Press Enter to start...{Colors.RESET}")


def normalize_command(cmd: str) -> str:
    """Normalize command input to standard direction."""
    cmd = cmd.lower().strip()

    # Direction mappings
    up_cmds = {"up", "u", "w"}
    down_cmds = {"down", "d", "s"}
    left_cmds = {"left", "l", "a"}
    right_cmds = {"right", "r"}

    if cmd in up_cmds:
        return "up"
    elif cmd in down_cmds:
        return "down"
    elif cmd in left_cmds:
        return "left"
    elif cmd in right_cmds:
        return "right"

    return cmd


def print_win_screen(game: Game) -> None:
    """Print the winning screen."""
    state = game.get_state()
    player = state["player"]
    maze_info = state["maze"]

    clear_screen()
    print(
        f"""
{Colors.BOLD}{Colors.GREEN}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🎉🎉🎉  YOU WON!  🎉🎉🎉                                ║
    ║                                                           ║
    ╠═══════════════════════════════════════════════════════════╣
    ║                                                           ║
    ║   📊 Final Stats:                                         ║
    ║      👣 Total Moves: {player['moves_made']:<5}                               ║
    ║      🔑 Keys Collected: {player['keys_collected']}/{maze_info['total_keys']}                            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}
    {Colors.CYAN}Type 'reset' to play again or 'quit' to exit{Colors.RESET}
"""
    )


def main() -> None:
    """Main game loop."""
    print_welcome()

    game = Game.create_new(width=7, height=7)
    message = "Find your way to the exit! 🚪"

    # Show initial game screen
    print_game_screen(game, message)

    while True:
        try:
            user_input = input(f"  {Colors.CYAN}➤{Colors.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            clear_screen()
            print(f"\n  {Colors.YELLOW}👋 Goodbye! Thanks for playing!{Colors.RESET}\n")
            break

        if not user_input:
            print_game_screen(game, "")
            continue

        cmd = normalize_command(user_input)

        # Handle quit
        if cmd in {"quit", "q", "exit"}:
            clear_screen()
            print(f"\n  {Colors.YELLOW}👋 Goodbye! Thanks for playing!{Colors.RESET}\n")
            break

        # Handle help
        if cmd in {"help", "h", "?"}:
            print_help()
            print_game_screen(game, "")
            continue

        # Handle reset
        if cmd in {"reset", "restart", "new"}:
            game.reset()
            message = "Game reset! Start fresh! 🔄"
            print_game_screen(game, message)
            continue

        # Handle movement
        if cmd in {"up", "down", "left", "right"}:
            result = game.move(cmd)

            if result.success:
                if result.reached_exit:
                    print_win_screen(game)
                else:
                    msg = result.message
                    if result.key_collected:
                        msg = "You found a key! 🔑"
                    print_game_screen(game, msg)
            else:
                print_game_screen(game, result.message)
            continue

        # Unknown command
        print_game_screen(game, f"Unknown command: '{user_input}'. Try 'help'")


if __name__ == "__main__":
    main()

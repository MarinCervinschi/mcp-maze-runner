import streamlit as st
import threading

from ui.runner import MazeRunner
from src.server import mcp, get_game

st.set_page_config(
    page_title="MCP Maze Runner",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

EMOJI_MAP = {
    "#": "🧱",  # Wall
    ".": "▫️",  # Empty
    "S": "🚩",  # Start
    "E": "🚪",  # Exit
    "K": "🔑",  # Key
    "@": "🧙",  # Player
    "?": "⬛",  # Unknown (fog of war)
    "·": "░░",  # Visited but not visible
}

# Custom CSS
CUSTOM_CSS = """
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    color: #1f77b4;
    margin-bottom: 1rem;
}
.maze-container {
    font-family: monospace;
    font-size: 1.5rem;
    line-height: 1.5;
    background-color: #1e1e1e;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
}
</style>
"""


class MazeRunnerUI:
    """Streamlit UI for the MCP Maze Runner game."""

    def __init__(self):
        self._init_session_state()

    @staticmethod
    def start_mcp_server():
        """Start MCP server in a background thread."""
        mcp.run(transport="sse")

    @staticmethod
    @st.cache_resource
    def _get_mcp_server_thread():
        """Get or create the MCP server thread."""
        import time

        server_thread = threading.Thread(
            target=MazeRunnerUI.start_mcp_server, daemon=True
        )
        server_thread.start()
        time.sleep(1)
        return server_thread

    def _init_session_state(self):
        """Initialize Streamlit session state."""
        # Start MCP server if not already running
        self._get_mcp_server_thread()

        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "maze_display" not in st.session_state:
            st.session_state.maze_display = ""
        if "maze_runner" not in st.session_state:
            st.session_state.maze_runner = None
        if "initialized" not in st.session_state:
            st.session_state.initialized = False

    def _initialize_runner(self):
        """Initialize the MazeRunner."""
        if st.session_state.maze_runner is None:
            st.session_state.maze_runner = MazeRunner()
            st.session_state.maze_runner.initialize()
            st.session_state.initialized = True

    def _process_message(self, user_message: str) -> tuple[str, str]:
        """Process a user message and return the response and updated maze."""
        response = st.session_state.maze_runner.send_message(user_message)
        maze_str = get_game().get_maze_display()
        return response, maze_str

    @staticmethod
    def _render_emoji_maze(maze_str: str) -> str:
        """Convert ASCII maze to emoji representation."""
        lines = []
        for line in maze_str.split("\n"):
            emoji_line = "".join(EMOJI_MAP.get(char, char + " ") for char in line)
            lines.append(emoji_line)
        return "\n".join(lines)

    def _render_header(self):
        """Render the page header."""
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        st.markdown(
            '<div class="main-header">🏃 MCP Maze Runner</div>',
            unsafe_allow_html=True,
        )

    def _render_maze_view(self):
        """Render the maze view column."""
        st.subheader("🗺️ Maze View")
        st.markdown("**Legend:** 🧙 You | 🚩 Start | 🚪 Exit | 🔑 Key | 🧱 Wall")

        if st.session_state.maze_display:
            emoji_maze = self._render_emoji_maze(st.session_state.maze_display)
            st.markdown(
                f'<div class="maze-container">{emoji_maze.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info(
                "Send a message to start the game! Try 'show maze' or 'look around'"
            )

        # Quick action buttons
        st.subheader("⚡ Quick Actions")
        cols = st.columns(4)
        actions = [
            ("⬆️ Up", "go up"),
            ("⬇️ Down", "go down"),
            ("⬅️ Left", "go left"),
            ("➡️ Right", "go right"),
        ]

        for col, (label, action) in zip(cols, actions):
            with col:
                if st.button(label, use_container_width=True):
                    st.session_state.pending_action = action

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗺️ Show Maze", use_container_width=True):
                st.session_state.pending_action = "show maze"
        with col2:
            if st.button("🔄 Reset Game", use_container_width=True):
                st.session_state.pending_action = "reset game"

    def _render_chat(self):
        """Render the chat column."""
        st.subheader("💬 Chat with the Maze Runner Agent")

        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Handle pending action from buttons
        user_input = st.session_state.pop("pending_action", None)

        # Chat input
        if prompt := st.chat_input("Type your command (e.g., 'go up', 'look around')"):
            user_input = prompt

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("🤔 Thinking..."):
                try:
                    response, maze_str = self._process_message(user_input)
                    if maze_str:
                        st.session_state.maze_display = maze_str
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Error: {e}"}
                    )

            st.rerun()

    def run(self):
        """Run the Streamlit application."""
        self._render_header()

        # Initialize runner
        if not st.session_state.initialized:
            with st.spinner("🔌 Connecting to maze server..."):
                try:
                    self._initialize_runner()
                    st.success("✅ Connected to maze server!")
                except Exception as e:
                    st.error(f"❌ Failed to connect: {e}")
                    return

        # Layout: Chat | Maze
        col_chat, col_maze = st.columns([1, 1])

        with col_maze:
            self._render_maze_view()

        with col_chat:
            self._render_chat()

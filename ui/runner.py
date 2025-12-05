import asyncio
import threading
from concurrent.futures import Future
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from root_agent.agent import root_agent


class MazeRunner:
    """Manages the ADK Runner and session for the maze game.

    Uses a dedicated thread with its own event loop to handle async operations,
    which avoids conflicts with Streamlit's event loop and MCP's SSE client.
    """

    def __init__(
        self, user_id: str = "maze_player", session_id: str = "maze_session_001"
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.runner: Runner | None = None
        self.session_service: InMemorySessionService | None = None
        self._initialized = False

        # Dedicated event loop running in a separate thread
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def _start_event_loop(self) -> None:
        """Start the dedicated event loop in a separate thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_coroutine(self, coro: Any) -> Any:
        """Run a coroutine in the dedicated event loop and wait for result."""
        if self._loop is None:
            raise RuntimeError("Event loop not started")

        future: Future[Any] = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=60)  # 60 second timeout

    def initialize(self) -> None:
        """Initialize the ADK runner and session (synchronous)."""
        if self._initialized:
            return

        # Start the dedicated event loop thread
        self._thread = threading.Thread(target=self._start_event_loop, daemon=True)
        self._thread.start()

        # Give the loop time to start
        import time

        time.sleep(0.1)

        # Run the async initialization in the dedicated loop
        self._run_coroutine(self._async_initialize())
        self._initialized = True

    async def _async_initialize(self) -> None:
        """Async initialization of the ADK runner."""
        self.session_service = InMemorySessionService()

        await self.session_service.create_session(
            app_name="maze_runner",
            user_id=self.user_id,
            session_id=self.session_id,
        )

        self.runner = Runner(
            agent=root_agent,
            app_name="maze_runner",
            session_service=self.session_service,
        )

    @property
    def is_initialized(self) -> bool:
        """Check if the runner is initialized."""
        return self._initialized

    def send_message(self, message: str) -> str:
        """Send a message to the agent and return the response (synchronous)."""
        if not self._initialized or self.runner is None:
            raise RuntimeError("Runner not initialized. Call initialize() first.")

        return self._run_coroutine(self._async_send_message(message))

    async def _async_send_message(self, message: str) -> str:
        """Async implementation of send_message."""
        if self.runner is None:
            raise RuntimeError("Runner not initialized")

        content = types.Content(role="user", parts=[types.Part(text=message)])

        response = ""
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=content,
        ):
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts") and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response = part.text

        return response

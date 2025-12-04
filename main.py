import subprocess
import time
import sys


def main() -> None:
    """Entry point for the APP - runs MCP server and ADK web in parallel."""

    print("🎮 Starting MCP Maze Runner server...")
    server_process = subprocess.Popen(
        ["uv", "run", "python", "-m", "src.server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    time.sleep(2)

    if server_process.poll() is not None:
        print("❌ Failed to start MCP server")
        sys.exit(1)

    print("✅ MCP server running on http://localhost:8080")
    print("🌐 Starting ADK web interface...")

    try:
        subprocess.run(["uv", "run", "adk", "web"])
    finally:
        print("\n🛑 Shutting down MCP server...")
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    main()

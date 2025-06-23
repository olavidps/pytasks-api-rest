#!/usr/bin/env python3
"""
Test runner script that handles the complete test setup and execution.

This script:
1. Starts the test database container if needed
2. Sets up the test database and tables
3. Runs the tests
4. Optionally cleans up after tests
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list[str], cwd: Path = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_docker_running() -> bool:
    """Check if Docker is running."""
    exit_code, _, _ = run_command(["docker", "info"])
    return exit_code == 0


def check_container_running(container_name: str) -> bool:
    """Check if a specific container is running."""
    exit_code, stdout, _ = run_command(
        ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"]
    )
    return exit_code == 0 and container_name in stdout


def start_test_database() -> bool:
    """Start the test database container."""
    print("🐳 Starting test database container...")

    if not check_docker_running():
        print("❌ Docker is not running. Please start Docker first.")
        return False

    # Check if container is already running
    if check_container_running("pytasks-postgres-test"):
        print("ℹ️  Test database container is already running")
        return True

    # Start the container
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"]
    )

    if exit_code != 0:
        print(f"❌ Failed to start test database container: {stderr}")
        return False

    print("⏳ Waiting for database to be ready...")

    # Wait for the database to be ready
    max_attempts = 30
    for attempt in range(max_attempts):
        exit_code, _, _ = run_command(
            ["docker", "exec", "pytasks-postgres-test", "pg_isready", "-U", "postgres"]
        )

        if exit_code == 0:
            print("✅ Test database is ready")
            return True

        if attempt < max_attempts - 1:
            time.sleep(2)

    print("❌ Test database failed to become ready")
    return False


def stop_test_database() -> bool:
    """Stop the test database container."""
    print("🐳 Stopping test database container...")

    exit_code, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"]
    )

    if exit_code != 0:
        print(f"❌ Failed to stop test database container: {stderr}")
        return False

    print("✅ Test database container stopped")
    return True


def setup_test_database() -> bool:
    """Set up the test database and tables."""
    print("🔧 Setting up test database...")

    exit_code, stdout, stderr = run_command(
        ["poetry", "run", "python", "scripts/setup_test_db.py", "setup"]
    )

    if exit_code != 0:
        print(f"❌ Failed to setup test database: {stderr}")
        return False

    print("✅ Test database setup completed")
    return True


def run_tests(test_args: list[str] = None) -> bool:
    """Run the tests."""
    print("🧪 Running tests...")

    cmd = ["poetry", "run", "pytest"]
    if test_args:
        cmd.extend(test_args)
    else:
        cmd.extend(["-v"])

    # Run tests with real-time output
    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def main():
    """Run the main function."""
    parser = argparse.ArgumentParser(
        description="Test runner for PyTasks API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_runner.py                    # Run all tests
  python scripts/test_runner.py --no-docker       # Run tests without Docker
  python scripts/test_runner.py --cleanup         # Run tests and cleanup after
  python scripts/test_runner.py --unit-only       # Run only unit tests
  python scripts/test_runner.py --integration-only # Run only integration tests
  python scripts/test_runner.py -- --cov=app      # Pass additional pytest args
        """,
    )

    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Skip Docker container management (assume DB is already running)",
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Stop test containers after running tests",
    )

    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests (no database required)",
    )

    parser.add_argument(
        "--integration-only", action="store_true", help="Run only integration tests"
    )

    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only setup the test environment, don't run tests",
    )

    # Parse known args to allow passing additional pytest arguments
    args, pytest_args = parser.parse_known_args()

    success = True

    try:
        # Handle unit tests only (no database needed)
        if args.unit_only:
            test_args = ["tests/unit/", "-v"] + pytest_args
            success = run_tests(test_args)
        else:
            # Start Docker container if needed
            if not args.no_docker:
                if not start_test_database():
                    sys.exit(1)

            # Setup database
            if not setup_test_database():
                sys.exit(1)

            # Run tests if not setup-only
            if not args.setup_only:
                if args.integration_only:
                    test_args = [
                        "tests/integration/",
                        "-v",
                        "-m",
                        "integration",
                    ] + pytest_args
                else:
                    test_args = ["-v"] + pytest_args

                success = run_tests(test_args)

    finally:
        # Cleanup if requested
        if args.cleanup and not args.no_docker and not args.unit_only:
            stop_test_database()

    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

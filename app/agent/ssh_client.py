import subprocess
import os
import logging
from typing import Tuple, Optional, List
from pathlib import Path

from dotenv import load_dotenv


class SSHRemoteClient:
    """Dockerized SSH client for executing remote commands"""

    def __init__(
            self,
            docker_image: str = "nnikolovskii/cmd-client",
            server_address: str = "nnikolovskii@mkpatka.duckdns.org",
            ssh_key_path: Optional[str] = None,
            known_hosts_path: Optional[str] = None,
            logger: Optional[logging.Logger] = None
    ):
        """
        Initialize SSH client container wrapper

        :param docker_image: Name of the pre-built Docker image
        :param server_address: Remote server SSH connection string
        :param ssh_key_path: Path to SSH private key (default: ./nnikolovskii_key)
        :param known_hosts_path: Path to known_hosts file (default: ~/.ssh/known_hosts)
        :param logger: Custom logger instance
        """
        self.docker_image = docker_image
        self.server_address = server_address
        self.logger = logger or logging.getLogger(__name__)

        load_dotenv()
        ssh_folder_path = os.getenv("SSH_KEYS")
        # Set default paths if not provided
        self.ssh_key = Path(ssh_key_path or os.path.join(ssh_folder_path, 'nnikolovskii_key'))
        self.known_hosts = Path(known_hosts_path or os.path.expanduser('~/.ssh/known_hosts'))

        self._validate_ssh_files()

    def _validate_ssh_files(self):
        """Ensure required SSH files exist"""
        if not self.ssh_key.exists():
            raise FileNotFoundError(f"SSH key not found at {self.ssh_key}")
        if not self.known_hosts.exists():
            raise FileNotFoundError(f"known_hosts file not found at {self.known_hosts}")

    def _build_docker_command(self, command: str) -> list:
        """Construct the Docker run command list"""
        return [
            'docker', 'run', '-i', '--rm',
            '-v', f'{self.ssh_key}:/root/.ssh/id_ed25519:ro',
            '-v', f'{self.known_hosts}:/root/.ssh/known_hosts:ro',
            self.docker_image,
            self.server_address,
            command
        ]

    def execute_list_of_messages(self, commands: List[str], stop_on_error: bool = False) -> List[Tuple[str, str, int]]:
        """
        Execute multiple remote commands through the Dockerized SSH client

        :param commands: List of shell commands to execute remotely
        :param stop_on_error: If True, stops execution when a command returns non-zero exit code
        :return: List of tuples, each containing (stdout, stderr, exit_code) for each command
        """
        results = []

        for i, command in enumerate(commands):
            self.logger.info(f"Executing command {i + 1}/{len(commands)}: {command}")
            result = self.execute(command)
            results.append(result)

            # Unpack the result
            _, _, exit_code = result

            # Check if we need to stop on error
            if stop_on_error and exit_code != 0:
                self.logger.warning(f"Stopping execution due to error in command: {command}")
                break

        return results

    def execute(self, command: str) -> Tuple[str, str, int]:
        """
        Execute a remote command through the Dockerized SSH client

        :param command: Shell command to execute remotely
        :return: Tuple of (stdout, stderr, exit_code)
        """
        docker_cmd = self._build_docker_command(command)
        self.logger.debug(f"Executing command: {' '.join(docker_cmd)}")

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            self.logger.info(f"Command executed with exit code: {result.returncode}")
            return (result.stdout.strip(), result.stderr.strip(), result.returncode)
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            return ("", str(e), 1)

    def __enter__(self):
        return self  # Enables context manager usage

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # Cleanup logic could be added here if needed


if __name__ == "__main__":
    # Initialize client with default configuration
    client = SSHRemoteClient()

    # Execute sample command
    results = client.execute_list_of_messages(["ls -la", "pwd"])
    for result in results:
        print(result)
    print(results)

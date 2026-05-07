"""Secure Docker-based code sandbox.

Runs untrusted user code inside an ephemeral, heavily restricted Docker
container and returns the output.

Security constraints applied:
    - mem_limit=50m         → maximum 50 MB of RAM
    - cpu_quota=50000       → at most 50 % of a single CPU core
    - network_disabled=True → no network access
    - auto_remove=True      → container is destroyed after exit
    - timeout=3s            → killed forcibly if it runs longer
"""

import logging

import requests.exceptions

logger = logging.getLogger(__name__)

# Map of human-readable language → Docker image tag
_SUPPORTED_IMAGES: dict[str, str] = {
    "python": "python:3.11-alpine",
}


def _run_container(image: str, command: list[str]) -> str:
    """Spin up a restricted container, wait for it, and return logs.

    Args:
        image: Docker image name (e.g. ``python:3.11-alpine``).
        command: Entry-point override list (e.g. ``["python", "-c", code]``).

    Returns:
        A string containing combined stdout + stderr output.

    Raises:
        RuntimeError: If Docker is unreachable or the container cannot be
                      created.
    """
    import docker
    from docker.errors import DockerException

    try:
        client = docker.from_env()
    except DockerException as exc:
        raise RuntimeError(
            "Docker daemon is not available. Is Docker running?"
        ) from exc

    container = client.containers.create(
        image=image,
        command=command,
        detach=True,
        mem_limit="50m",
        cpu_quota=50000,
        network_disabled=True,
        stdout=True,
        stderr=True,
    )

    try:
        container.start()
    except DockerException as exc:
        container.remove()
        raise RuntimeError(f"Failed to start container: {exc}") from exc

    # Wait with a hard 3-second timeout
    try:
        container.wait(timeout=3)
    except requests.exceptions.ReadTimeout:
        logger.warning("Container %s timed out, force-killing", container.id)
        try:
            container.kill()
        except Exception:
            pass
        output = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace").strip()
        container.remove()
        return (
            f"Execution timed out after 3 seconds.\n"
            f"--- partial output ---\n{output}"
        )
    except Exception:
        container.kill()
        container.remove()
        raise

    output = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace").strip()
    container.remove()
    return output if output else "(no output)"


def run_code_in_docker(code: str, language: str) -> str:
    """Execute the provided source code inside a sandboxed Docker container.

    Args:
        code: The raw source code to run.
        language: Target programming language (currently only ``"python"``).

    Returns:
        The combined stdout + stderr output produced by the code.

    Raises:
        RuntimeError: If the language is unsupported or Docker is unavailable.
    """
    image = _SUPPORTED_IMAGES.get(language.lower())
    if image is None:
        raise RuntimeError(
            f"Unsupported language '{language}'. Supported: {list(_SUPPORTED_IMAGES)}"
        )

    return _run_container(image, ["python", "-c", code])

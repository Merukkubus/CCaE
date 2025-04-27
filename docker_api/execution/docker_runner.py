import time
import shlex
import docker
from docker.errors import DockerException

_docker_client = None

def get_docker_client():
    global _docker_client
    if _docker_client is None:
        _docker_client = docker.from_env()
    else:
        try:
            # Пытаемся запросить версию сервера — если клиент мертвый, упадем
            _docker_client.version()
        except DockerException:
            print("Docker client is dead. Reinitializing...")
            _docker_client = docker.from_env()
    return _docker_client


def run_code_in_docker(python_version, code):
    client = get_docker_client()  # <<<<< получаем клиента здесь
    start_time = time.time()
    safe_code = shlex.quote(code)
    try:
        container = client.containers.run(
            f'python:{python_version}-slim',
            command=f'python3 -c {safe_code}',
            detach=True,
            stdout=True,
            stderr=True
        )
    except docker.errors.ImageNotFound:
        return "Error: Python image not found", 0
    except docker.errors.APIError as e:
        return f"Error: {str(e)}", 0

    container.wait()

    logs = container.logs(stdout=True, stderr=True, stream=False).decode()
    execution_time = round(time.time() - start_time, 4)

    try:
        container.stop()
        container.remove()
    except docker.errors.APIError as e:
        logs += f"\nError stopping/removing container: {str(e)}"

    return logs, execution_time

def install_package_in_docker(python_version, package):
    client = get_docker_client()  # <<<<< получаем клиента здесь
    try:
        container = client.containers.run(
            f'python:{python_version}-slim',
            command=f'pip install -v {package}',
            detach=True,
            stdout=True,
            stderr=True
        )
    except docker.errors.ImageNotFound:
        return "Error: Python image not found", False
    except docker.errors.APIError as e:
        return f"Error: {str(e)}", False

    container.wait()

    logs = container.logs(stdout=True, stderr=True, stream=False).decode()

    try:
        container.stop()
        container.remove()
    except docker.errors.APIError as e:
        logs += f"\nError stopping/removing container: {str(e)}"

    success = False
    final_message = ""

    if "Successfully installed" in logs:
        success = True
        lines = logs.splitlines()
        for line in lines:
            if "Successfully installed" in line:
                final_message = line.strip()
                break
    elif "ERROR:" in logs or "No matching distribution found" in logs:
        success = False
        final_message = "Error occurred while installing package."
    else:
        final_message = "Unknown installation status. Please check manually."

    return final_message, success
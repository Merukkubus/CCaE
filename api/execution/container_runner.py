import io
import os
import tarfile
import tempfile
import time
import docker as d
from docker.errors import DockerException

_d_client = None

def get_d_client():
    global _d_client
    if _d_client is None:
        _d_client = d.from_env()
    else:
        try:
            _d_client.version()
        except DockerException:
            print("Container client is dead. Reinitializing...")
            _d_client = d.from_env()
    return _d_client


def install_packages(version, package):
    client = get_d_client()
    try:
        container = client.containers.run(
            f'python:{version}-slim',
            command=f'pip install -v {package}',
            detach=True,
            stdout=True,
            stderr=True
        )
    except d.errors.ImageNotFound:
        return "Error: Python image not found", False
    except d.errors.APIError as e:
        return f"Error: {str(e)}", False

    container.wait()
    logs = container.logs(stdout=True, stderr=True, stream=False).decode()

    try:
        container.stop()
        container.remove()
    except d.errors.APIError as e:
        logs += f"\nError stopping/removing container: {str(e)}"

    success = False
    final_message = ""

    if "Successfully installed" in logs:
        success = True
        for line in logs.splitlines():
            if "Successfully installed" in line:
                final_message = line.strip()
                break
    elif "ERROR:" in logs or "No matching distribution found" in logs:
        final_message = "Error occurred while installing package."
    else:
        final_message = "Unknown installation status. Please check manually."

    return final_message, success


def run_code_generic(language, version, code, compile_cmd=None, run_cmd=None, libs=None, file_ext="txt", d_image=None):
    client = get_d_client()
    start_time = time.time()
    libs = libs or []

    filename = f"main.{file_ext}"
    if d_image.startswith("openjdk"): # Для работы Java нужен файл Main.java
        filename = "Main.java"

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "w") as f:
            f.write(code)

        install_cmd = ""
        if libs:
            install_cmd = "apt-get update && apt-get install -y " + " ".join(libs) + " && "

        full_cmd = install_cmd
        if compile_cmd:
            full_cmd += compile_cmd + " && "
        full_cmd += run_cmd

        final_image = d_image or f"{language}:{version}"
        print("Используемый образ:", final_image)
        print("Команда запуска:", full_cmd)

        try:
            # загрузить образ заранее
            try:
                client.images.get(final_image)
                print("Образ уже есть локально")
            except d.errors.ImageNotFound:
                print("Образ не найден локально. Подгружаем...")
                client.images.pull(final_image)

            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(file_path, arcname=filename)
            tar_stream.seek(0)

            container = client.containers.create(
                image=final_image,
                command=f'/bin/bash -c "{full_cmd}"',
                tty=True,
                stdin_open=True
            )

            container.put_archive('/tmp/', tar_stream)

            container.start()
            container.wait()

            logs = container.logs(stdout=True, stderr=True, stream=False).decode()
            execution_time = round(time.time() - start_time, 4)

            try:
                container.remove(force=True)
            except Exception:
                pass

            return logs, execution_time

        except d.errors.ContainerError as e:
            return f"ContainerError: {str(e)}", 0
        except d.errors.APIError as e:
            return f"APIError: {str(e)}", 0
        except Exception as e:
            return f"Unhandled Exception: {str(e)}", 0
"""Try the restricted operations against a container using the custom profile.

Expected on a correctly enforced profile: reading /etc/passwd and executing
/bin/bash fail. Run this on Linux with AppArmor enabled and profile loaded.
"""

from __future__ import annotations

import time
import docker
from docker.errors import DockerException

IMAGE = "flask-apparmor:1.0"
PROFILE = "my-apparmor-profile"
CONTAINER_NAME = "flask-apparmor-test"


def main() -> None:
    client = docker.from_env()
    container = None
    try:
        try:
            client.images.get(IMAGE)
        except docker.errors.ImageNotFound:
            print(f"Image {IMAGE} not found; building it from the current directory...")
            client.images.build(path=".", tag=IMAGE, rm=True)

        try:
            old = client.containers.get(CONTAINER_NAME)
            old.remove(force=True)
        except docker.errors.NotFound:
            pass

        container = client.containers.run(
            IMAGE,
            name=CONTAINER_NAME,
            ports={"5000/tcp": 5000},
            security_opt=[f"apparmor={PROFILE}"],
            detach=True,
        )
        time.sleep(1)
        print(f"Container started: {container.short_id}")

        for label, command in [
            ("read /etc/passwd", ["cat", "/etc/passwd"]),
            ("execute /bin/bash", ["/bin/bash", "-c", "echo shell-started"]),
        ]:
            exit_code, output = container.exec_run(command)
            print(f"Attempt to {label}: exit_code={exit_code}")
            print(output.decode("utf-8", errors="replace").strip() or "<no output>")

        print("Interpretation: non-zero exit codes are expected for the restricted actions.")
    except DockerException as exc:
        raise SystemExit(
            f"Docker SDK failed: {exc}\nEnsure Docker/AppArmor are available and the profile is loaded."
        ) from exc
    finally:
        if container is not None:
            try:
                print("Stopping and removing test container...")
                container.remove(force=True)
            except DockerException as exc:
                print(f"Cleanup warning: {exc}")
        client.close()


if __name__ == "__main__":
    main()

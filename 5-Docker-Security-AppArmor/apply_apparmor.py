"""Build the image, run Flask with the custom AppArmor profile, and inspect it.

Run this script on a Linux host whose Docker daemon supports AppArmor and after
loading `my-apparmor-profile` with apparmor_parser.
"""

from __future__ import annotations

import time
import docker
from docker.errors import DockerException

IMAGE = "flask-apparmor:1.0"
PROFILE = "my-apparmor-profile"
CONTAINER_NAME = "flask-apparmor-sdk"


def main() -> None:
    client = docker.from_env()
    container = None
    try:
        print(f"Building image {IMAGE}...")
        client.images.build(path=".", tag=IMAGE, rm=True)

        # Remove a prior container from a previous run, if it exists.
        try:
            old = client.containers.get(CONTAINER_NAME)
            old.remove(force=True)
        except docker.errors.NotFound:
            pass

        print(f"Starting container with AppArmor profile {PROFILE}...")
        container = client.containers.run(
            IMAGE,
            name=CONTAINER_NAME,
            ports={"5000/tcp": 5000},
            security_opt=[f"apparmor={PROFILE}"],
            detach=True,
        )
        time.sleep(2)
        container.reload()
        print(f"Container started: {container.short_id}; status={container.status}")

        attrs = client.api.inspect_container(container.id)
        security_options = attrs.get("HostConfig", {}).get("SecurityOpt")
        print(f"AppArmor security options: {security_options}")
        if not security_options or not any(PROFILE in item for item in security_options):
            print("WARNING: Docker inspect did not report the expected profile option.")
    except DockerException as exc:
        raise SystemExit(
            f"Docker SDK failed: {exc}\nCheck that this is a Linux Docker host with AppArmor enabled, "
            "that Docker is running, and that the profile is loaded."
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

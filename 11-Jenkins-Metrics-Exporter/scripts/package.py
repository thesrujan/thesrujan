"""Create a clean deployment folder and ZIP archive for the metrics exporter."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FILES = [
    Path("README.md"),
    Path("requirements.txt"),
    Path("metrics_exporter.py"),
    Path("config/exporter.env.example"),
]


def create_package(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_dir = output_dir / "metrics-exporter"
    archive_path = output_dir / "metrics-exporter.zip"

    if package_dir.exists():
        shutil.rmtree(package_dir)
    if archive_path.exists():
        archive_path.unlink()

    package_dir.mkdir(parents=True)
    for relative_path in PACKAGE_FILES:
        source = PROJECT_ROOT / relative_path
        if not source.is_file():
            raise FileNotFoundError(f"Required package file is missing: {source}")
        destination = package_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(output_dir))

    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="deployment",
        help="Deployment output directory (default: deployment)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir

    archive_path = create_package(output_dir)
    print(f"Deployment directory: {output_dir / 'metrics-exporter'}")
    print(f"Deployment archive:   {archive_path}")


if __name__ == "__main__":
    main()

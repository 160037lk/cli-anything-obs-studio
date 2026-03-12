"""Setup script for cli-anything-obs-studio."""
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-obs-studio",
    version="1.0.0",
    description="CLI for controlling OBS Studio via WebSocket",
    author="CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-obs-studio=cli_anything.obs_studio.obs_studio_cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

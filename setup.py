from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agi-tools-client",
    version="0.1.0",
    author="vsai23",
    description="A CLI client for AGI Tools",
    long_description=long_description,
    long_description_content_type="markdown",
    url="https://github.com/vsai23/agi-tools-client",
    packages=find_packages(include=["agi_tools_client", "agi_tools_client.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "typer>=0.9.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "agi-tools=agi_tools_client.cli:main",
            "dagify=agi_tools_client.cli:dagify",
            "dagent=agi_tools_client.cli:dagent",
            "schemagin=agi_tools_client.cli:schemagin",
            "datagin=agi_tools_client.cli:datagin",
            "pagint=agi_tools_client.cli:pagint",
        ],
    },
) 
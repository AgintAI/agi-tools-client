import inspect
import json
import logging
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Union

from dotenv import load_dotenv
import httpx
import typer

# Configure logging to suppress HTTPX logs
logging.getLogger("httpx").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") == "1" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Map OpenAPI "type" to Python types.
TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}


@lru_cache(maxsize=1)
def fetch_openapi_spec() -> Dict[str, Any]:
    """
    Fetch the OpenAPI spec from the /openapi.json endpoint.
    The result is cached using LRU cache to avoid repeated calls.
    """
    api_url = os.getenv("DOCKER_BUILDER_API_URL", "http://localhost:8000")
    url = f"{api_url}/openapi.json"

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch OpenAPI spec: {str(e)}")
        raise typer.Exit(code=1)
    except json.JSONDecodeError:
        logger.error("Invalid OpenAPI spec format received from server")
        raise typer.Exit(code=1)


def load_openapi_spec() -> Dict[str, Any]:
    """
    Load the OpenAPI spec. If spec_path is provided, load from file,
    otherwise fetch from the API endpoint.
    
    In the future set up a static openapi.json, in beta creates an additional point for stale spec
    """
    spec_path = os.getenv("OPENAPI_SPEC_PATH", "openapi.json")
    p = Path(spec_path)
    if p.is_file():
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    return fetch_openapi_spec()


def create_parameter(
    prop_name: str, prop_spec: Dict[str, Any]
) -> Union[typer.Argument, typer.Option]:
    """
    Create a Typer parameter (Argument or Option) based on the OpenAPI property spec.
    """
    # Extract metadata
    metadata = prop_spec.get("openapi_extra", {})
    is_argument = metadata.get("x-is-argument", False)
    is_flag = metadata.get("x-is-flag", False)
    is_required = metadata.get("x-required", False)
    cli_name = metadata.get("x-cli-name", prop_name)  # Get the CLI name if specified

    # Get basic properties
    description = prop_spec.get("description", "")
    default = prop_spec.get("default", None)

    # Determine type
    type_info = prop_spec.get("type", "string")
    if "anyOf" in prop_spec:
        types = [t.get("type") for t in prop_spec["anyOf"] if "type" in t]
        if types:
            type_info = types[0]

    TYPE_MAP.get(type_info, str)

    if is_argument:
        return typer.Argument(
            default=default if not is_required else ...,
            help=description,
        )
    else:
        # For options, handle flags and regular options
        if is_flag:
            return typer.Option(
                default=default if default is not None else False,
                help=description,
                is_flag=True,
            )

        # Create option with explicit name
        option_name = f"--{cli_name.replace('_', '-')}"
        return typer.Option(
            default if not is_required else ...,
            option_name,
            help=description,
            show_default=default is not None and not is_required,
        )


def create_command_function(
    path_str: str, method: str, operation: Dict[str, Any], spec: Dict[str, Any]
):
    """Create a command function with dynamic parameters based on OpenAPI spec."""

    def command_func(**kwargs):
        """Execute the command."""
        api_url = os.getenv("DOCKER_BUILDER_API_URL", "http://localhost:8000")
        url = f"{api_url}{path_str}"

        # Filter out None values
        body = {k: v for k, v in kwargs.items() if v is not None}

        # Add agint_apikey to the body
        body["agint_apikey"] = os.getenv("AGINT_APIKEY")

        # Log request details if DEBUG=1
        if os.getenv("DEBUG") == "1":
            logger.debug(f"Making {method.upper()} request to {url}")
            logger.debug(f"Request body: {json.dumps(body, indent=2)}")

        try:
            # Use a longer timeout for long-running commands (3 minutes)
            with httpx.Client(timeout=180.0) as client:
                resp = client.request(method.upper(), url, json=body)

                # Log the raw response in debug mode
                if os.getenv("DEBUG") == "1":
                    logger.debug(f"Response status: {resp.status_code}")
                    logger.debug(f"Response headers: {dict(resp.headers)}")
                    logger.debug(f"Raw response body: {resp.text}")

                # Handle 400 errors specially to extract the error message
                if resp.status_code == 400:
                    error_data = resp.json()
                    if os.getenv("DEBUG") == "1":
                        logger.debug(
                            f"Parsed error response: {json.dumps(error_data, indent=2)}"
                        )

                    # Extract error details
                    if isinstance(error_data, dict):
                        # Handle structured error response
                        stderr = error_data.get("stderr", "")
                        stdout = error_data.get("stdout", "")
                        error_data.get("exit_code")
                        exception = error_data.get("exception")

                        # Clean and format the error message
                        error_parts = []
                        if stderr:
                            error_parts.append(stderr)
                        if stdout:
                            error_parts.append(stdout)
                        if exception and exception not in error_parts:
                            error_parts.append(exception)

                        error_msg = "\n".join(part for part in error_parts if part)
                    else:
                        error_msg = str(error_data)

                    typer.secho("Error:", fg=typer.colors.RED, err=True)
                    typer.echo(error_msg, err=True)
                    raise typer.Exit(code=1)

                resp.raise_for_status()
                data = resp.json()

                # Always show stderr on the terminal if present
                if data.get("stderr"):
                    typer.echo(data["stderr"], err=True, color=True)

                # Handle stdout based on whether we're in a terminal
                if data.get("stdout"):
                    if not sys.stdout.isatty():
                        # Not in terminal - show the output
                        print(data["stdout"], end="")

                # Log response if DEBUG=1
                if os.getenv("DEBUG") == "1":
                    logger.debug(f"Processed response: {json.dumps(data, indent=2)}")

        except httpx.HTTPError as e:
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
        except json.JSONDecodeError:
            if os.getenv("DEBUG") == "1":
                logger.debug(f"Failed to parse JSON from response: {resp.text}")
            typer.secho(
                "Error: Invalid response format from server",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)

    # Extract request body schema
    body_schema = extract_body_schema(operation, spec)
    properties = body_schema.get("properties", {})

    # Build dynamic parameters
    parameters = []
    for prop_name, prop_spec in properties.items():
        if (
            prop_name != "agint_apikey"
        ):  # Skip agint_apikey as it's handled automatically
            param_obj = create_parameter(prop_name, prop_spec)
            parameters.append(
                inspect.Parameter(
                    prop_name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=param_obj,
                    annotation=TYPE_MAP.get(prop_spec.get("type", "string"), str),
                )
            )

    # Set the signature and return the function
    command_func.__signature__ = inspect.Signature(parameters=parameters)
    command_func.__doc__ = operation.get("description", "")
    return command_func


def extract_body_schema(
    operation: Dict[str, Any], spec: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Extract the requestBody schema from the operation, resolving any references.
    """
    req_body = operation.get("requestBody", {})
    content = req_body.get("content", {})
    schema = content.get("application/json", {}).get("schema", {})

    # If it's a reference, resolve it
    if "$ref" in schema:
        ref_path = schema["$ref"].split("/")
        current = spec
        for part in ref_path[1:]:  # Skip the first '#'
            current = current.get(part, {})
        schema = current

    return schema if isinstance(schema, dict) else {}


def create_app_for_group(
    group_name: str, paths: Dict[str, Any], spec: Dict[str, Any]
) -> typer.Typer:
    """Create a Typer app for a specific group of endpoints."""
    app = typer.Typer(help=f"CLI for {group_name}", no_args_is_help=True)

    # Group commands by their second path segment
    for path_str, path_item in paths.items():
        parts = path_str.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == group_name:
            command_name = parts[1]

            for method, operation in path_item.items():
                if method.lower() in ("get", "post", "put", "patch", "delete"):
                    command_func = create_command_function(
                        path_str, method, operation, spec
                    )
                    app.command(name=command_name)(command_func)

    return app


def get_app_groups(spec: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Group paths by their root segment."""
    groups = {}
    for path_str, path_item in spec.get("paths", {}).items():
        if path_str == "/health":  # Skip health check endpoint
            continue

        parts = path_str.strip("/").split("/")
        if len(parts) >= 1:
            group_name = parts[0]
            if group_name not in groups:
                groups[group_name] = {}
            groups[group_name][path_str] = path_item

    return groups


def create_cli_apps():
    """Create separate CLI apps for each root path."""
    spec = load_openapi_spec()

    # Group paths by their root segment
    groups = get_app_groups(spec)

    # Create apps for each group
    apps = {}
    for group_name, group_paths in groups.items():
        apps[group_name] = create_app_for_group(group_name, group_paths, spec)

    return apps


# Create the CLI apps
cli_apps = create_cli_apps()

# Export each app as a module-level variable
dagify = cli_apps.get("dagify")
dagent = cli_apps.get("dagent")
schemagin = cli_apps.get("schemagin")
datagin = cli_apps.get("datagin")
pagint = cli_apps.get("pagint")


def main():
    """Entry point for CLI commands."""
    script_name = Path(sys.argv[0]).stem
    if script_name in cli_apps:
        cli_apps[script_name]()
    else:
        # Create a parent app that includes all commands
        app = typer.Typer(help="Docker Builder CLI")
        for name, cli_app in cli_apps.items():
            app.add_typer(cli_app, name=name)
        app()


def clean_formatted_text(text: str) -> str:
    """Clean up RTF/formatted text to make it more readable.

    Args:
        text: The text to clean up

    Returns:
        Cleaned up text with RTF/formatting removed
    """
    if not isinstance(text, str):
        return str(text)

    # Remove common RTF/ANSI escape sequences
    import re

    # Remove ANSI escape sequences
    text = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)

    # Remove box drawing characters with simpler alternatives
    box_chars_map = {
        "─": "-",
        "│": "|",
        "╭": "+",
        "╮": "+",
        "╯": "+",
        "╰": "+",
        "╱": "/",
        "╲": "\\",
        "╳": "x",
        "━": "-",
        "┃": "|",
        "┏": "+",
        "┓": "+",
        "┛": "+",
        "┗": "+",
        "┣": "+",
        "┫": "+",
        "┳": "+",
        "┻": "+",
        "╋": "+",
    }
    for old, new in box_chars_map.items():
        text = text.replace(old, new)

    # Remove other common formatting artifacts
    text = re.sub(r"\{\\[^}]+\}", "", text)

    # Clean up common command-line formatting
    text = re.sub(r"\[0m|\[1m|\[2m", "", text)

    # Normalize whitespace while preserving line breaks
    lines = text.split("\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in lines]
    text = "\n".join(line for line in lines if line)

    return text


if __name__ == "__main__":
    load_dotenv()   
    main()

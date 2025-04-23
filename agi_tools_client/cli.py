# from langsmith import traceable
import asyncio
import base64
import inspect
import json
import logging
import os
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

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

VOLUME_PREFIX = "agitransfer://"
CACHE_TTL = 180  # 3 minutes
UPLOAD_CACHE_FILE = ".docker_builder_upload_cache.json"

# Module-level cache variables
_spec_cache: Optional[Dict[str, Any]] = None
_spec_cache_time: Optional[float] = None

# Resolved cache file path
_upload_cache_file = Path.cwd() / UPLOAD_CACHE_FILE


# @traceable
def _load_upload_cache() -> Dict[str, Dict[str, Any]]:
    """Load the upload cache from the JSON file."""
    if _upload_cache_file.exists():
        try:
            with open(_upload_cache_file, "r") as f:
                cache_data = json.load(f)
                # Basic validation
                if isinstance(cache_data, dict):
                    if os.getenv("DEBUG") == "1":
                        logger.debug(
                            f"Loaded {len(cache_data)} items from upload cache: {_upload_cache_file}"
                        )
                    return cache_data
                else:
                    logger.warning(
                        f"Invalid cache file format in {_upload_cache_file}. Ignoring cache."
                    )
                    return {}
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(
                f"Error loading upload cache from {_upload_cache_file}: {e}. Ignoring cache."
            )
            return {}
    else:
        if os.getenv("DEBUG") == "1":
            logger.debug(
                f"Upload cache file not found: {_upload_cache_file}. Starting fresh."
            )
        return {}


# @traceable
def _save_upload_cache(cache: Dict[str, Dict[str, Any]]):
    """Save the upload cache to the JSON file."""
    try:
        with open(_upload_cache_file, "w") as f:
            json.dump(cache, f, indent=2)
            if os.getenv("DEBUG") == "1":
                logger.debug(
                    f"Saved {len(cache)} items to upload cache: {_upload_cache_file}"
                )
    except OSError as e:
        logger.error(f"Error saving upload cache to {_upload_cache_file}: {e}")


# @traceable
def load_openapi_spec() -> Dict[str, Any]:
    """
    Load the OpenAPI spec from the /openapi.json endpoint.
    The result is cached in memory for CACHE_TTL seconds.
    """
    global _spec_cache, _spec_cache_time

    # Check cache validity
    if (
        _spec_cache
        and _spec_cache_time
        and (time.time() - _spec_cache_time < CACHE_TTL)
    ):
        return _spec_cache

    api_url = os.getenv("DOCKER_BUILDER_API_URL", "https://api.agintai.com")
    url = f"{api_url}/openapi.json"

    if os.getenv("DEBUG") == "1":
        logger.debug(f"Fetching OpenAPI spec from {url}")

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            spec_data = resp.json()

            # Update cache
            _spec_cache = spec_data
            _spec_cache_time = time.time()
            if os.getenv("DEBUG") == "1":
                logger.debug("Updated OpenAPI spec cache.")

            return spec_data
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch OpenAPI spec: {str(e)}")
        raise typer.Exit(code=1)
    except json.JSONDecodeError:
        logger.error("Invalid OpenAPI spec format received from server")
        raise typer.Exit(code=1)


# @traceable
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


# @traceable
def create_command_function(
    path_str: str, method: str, operation: Dict[str, Any], spec: Dict[str, Any]
):
    """Create a command function with dynamic parameters based on OpenAPI spec."""

    # @traceable
    def read_file_like(path: str) -> str:
        """Helper to read content from files, including /dev/fd paths."""
        try:
            # Handle process substitution and regular files
            if path.startswith("/dev/fd/") or os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        return f.read()
                except (IOError, OSError) as e:
                    logger.debug(f"Failed to read from {path}: {e}")
                    return path
            return path
        except Exception as e:
            logger.debug(f"Error processing path {path}: {e}")
            return path

    # @traceable
    def _background_download_and_unzip(
        zip_url: str, temp_zip_path: str, target_dir: str
    ):
        """Downloads a zip file, extracts it, and cleans up in the background."""
        try:
            if os.getenv("DEBUG") == "1":
                logger.debug(
                    f"Background: Downloading zip from {zip_url} to {temp_zip_path}"
                )

            # Download the zip file
            with open(temp_zip_path, "wb") as temp_zip_file:
                # Use a longer timeout for potentially large downloads
                with httpx.stream(
                    "GET", zip_url, timeout=180.0, follow_redirects=True
                ) as download_resp:
                    download_resp.raise_for_status()
                    for chunk in download_resp.iter_bytes():
                        temp_zip_file.write(chunk)

            download_size = os.path.getsize(temp_zip_path)
            if os.getenv("DEBUG") == "1":
                logger.debug(
                    f"Background: Download complete. Size: {download_size} bytes"
                )
            if download_size == 0:
                logger.warning(
                    f"Background: Downloaded zip file {temp_zip_path} is empty."
                )

            # Unzip the file, overwriting existing files
            if os.getenv("DEBUG") == "1":
                logger.debug(
                    f"Background: Unzipping {temp_zip_path} to {target_dir}, overwriting."
                )

            with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                # Check for potentially harmful paths
                members_to_extract = []
                for member in zip_ref.namelist():
                    if member.startswith("/") or ".." in member:
                        logger.error(
                            f"Background: Zip archive contains potentially unsafe path: {member}. Skipping extraction."
                        )
                        # Optionally raise an error or just skip the file/archive
                        return  # Stop processing this zip if unsafe path detected
                    elif member == ".zip":
                        if os.getenv("DEBUG") == "1":
                            logger.debug(
                                "Background: Skipping extraction of unwanted '.zip' entry."
                            )
                    else:
                        members_to_extract.append(member)

                if os.getenv("DEBUG") == "1":
                    logger.debug(
                        f"Background: Extracting {len(members_to_extract)} members to {target_dir}"
                    )
                zip_ref.extractall(target_dir, members=members_to_extract)

            if os.getenv("DEBUG") == "1":
                logger.debug("Background: Unzip complete.")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Background sync error (HTTP {e.response.status_code}): {e.request.url}. Response: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Background sync error (Request): {str(e)}")
        except zipfile.BadZipFile:
            logger.error(
                f"Background sync error: Downloaded file {temp_zip_path} is not a valid zip."
            )
        except OSError as e:
            logger.error(f"Background sync error (File System): {str(e)}")
        except Exception:
            logger.exception("Unexpected background sync error:")  # Log full traceback
        finally:
            # Clean up temporary zip file
            if os.path.exists(temp_zip_path):
                try:
                    os.remove(temp_zip_path)
                    if os.getenv("DEBUG") == "1":
                        logger.debug(
                            f"Background: Cleaned up temporary zip file: {temp_zip_path}"
                        )
                except OSError as e:
                    logger.error(
                        f"Background: Failed to remove temporary zip file {temp_zip_path}: {e}"
                    )

    # @traceable
    def _synchronize_user_directory(api_url: str, agint_apikey: str):
        """Calls agitransfer zip-directory and starts a background download/unzip."""
        zip_url = None
        temp_zip_path = None  # Keep track of the path for cleanup if thread fails early
        try:
            # Step 1: Call zip-directory endpoint
            zip_endpoint_url = f"{api_url}/agitransfer/zip-directory"
            zip_payload = {
                "agint_apikey": agint_apikey,
                "directory_path": VOLUME_PREFIX + "/",
                "verbose": os.getenv("DEBUG") == "1",
                "api_key": agint_apikey,
            }
            if os.getenv("DEBUG") == "1":
                logger.debug(f"Initiating sync: Calling {zip_endpoint_url}")
                logger.debug(f"Zip payload: {json.dumps(zip_payload, indent=2)}")

            with httpx.Client(timeout=60.0) as client:
                zip_resp = client.post(zip_endpoint_url, json=zip_payload)

                if os.getenv("DEBUG") == "1":
                    logger.debug(f"Zip response status: {zip_resp.status_code}")
                    logger.debug(f"Zip response body: {zip_resp.text}")

                if zip_resp.status_code == 400:
                    try:
                        error_data = zip_resp.json()
                        # Decode base64 stderr, then decode bytes to string
                        stderr_bytes = base64.b64decode(error_data.get("stderr", ""))
                        error_data["stderr"] = stderr_bytes.decode("utf-8", errors="replace") # Decode bytes to str
                        
                        error_msg = (
                            f"Sync failed (zip step - 400): {json.dumps(error_data)}"
                        )
                    except (json.JSONDecodeError, base64.binascii.Error, UnicodeDecodeError) as decode_err:
                        # Handle potential errors during decoding or JSON parsing
                        logger.error(f"Error processing 400 response body: {decode_err}")
                        error_msg = f"Sync failed (zip step - 400): {zip_resp.text}"
                    typer.secho(error_msg, fg=typer.colors.RED, err=True)
                    # Don't exit, just log and skip background download
                    logger.error(error_msg)
                    return

                zip_resp.raise_for_status()  # Handle other HTTP errors
                zip_data = zip_resp.json()
                zip_url = zip_data.get("stdout")

                if not zip_url or not zip_url.startswith("http"):
                    error_msg = "Error: Sync failed - could not get a valid zip URL from response."
                    typer.secho(error_msg, fg=typer.colors.RED, err=True)
                    logger.error(
                        f"Zip response missing or invalid stdout URL: {zip_data}"
                    )
                    # Don't exit, log and skip background download
                    return

            if os.getenv("DEBUG") == "1":
                logger.debug(f"Zip URL obtained: {zip_url}")

            # Step 2: Prepare for background download
            # Create a temporary file path without creating the file
            temp_zip_path = tempfile.mktemp(suffix=".zip")
            target_dir = os.getcwd()

            if os.getenv("DEBUG") == "1":
                logger.debug(
                    f"Starting background download to {temp_zip_path} for extraction to {target_dir}"
                )

            # Step 3: Run download/unzip directly in main thread
            _background_download_and_unzip(zip_url, temp_zip_path, target_dir)

            if os.getenv("DEBUG") == "1":
                logger.debug(
                    "Background download thread started. Main command continues."
                )

        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            try:
                error_body = json.dumps(e.response.json(), indent=2)
            except json.JSONDecodeError:
                pass
            typer.secho(
                f"Error initiating sync (HTTP {e.response.status_code}): {e.request.url}",
                fg=typer.colors.RED,
                err=True,
            )
            typer.secho(f"Response body: {error_body}", err=True)
            logger.error(
                f"Sync initiation HTTPStatusError: Status={e.response.status_code}, Body={e.response.text}, URL={e.request.url}"
            )
            # Don't exit here, allow command to potentially finish anyway
        except httpx.RequestError as e:
            typer.secho(
                f"Error initiating sync (Request): {str(e)}",
                fg=typer.colors.RED,
                err=True,
            )
            logger.error(f"Sync initiation RequestError: {e}")
            # Don't exit here
        except Exception as e:
            typer.secho(
                f"An unexpected error occurred during sync initiation: {str(e)}",
                fg=typer.colors.RED,
                err=True,
            )
            logger.exception("Unexpected sync initiation error:")
            # Don't exit here

        # NOTE: The main command flow continues immediately after starting the thread.
        # No waiting, no direct error handling for the background process here.
        # Cleanup of the temp file is handled within the background thread.

    def _perform_upstream_sync(api_url: str, agint_apikey: str):
        """Scans CWD, filters hidden files, checks cache, and uploads changes in parallel."""
        sync_endpoint = f"{api_url}/agitransfer/upload-file"
        cwd = Path.cwd()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        semaphore = asyncio.Semaphore(10)  # Limit concurrency

        # Load the existing cache
        upload_cache = _load_upload_cache()
        new_upload_cache = {}  # Store results for the *new* cache

        # @traceable # Inner functions might not be traceable correctly this way
        async def upload_item(
            item_path: Path,
            client: httpx.AsyncClient,
            cache: Dict[str, Dict[str, Any]],
        ) -> Optional[Tuple[str, float, int, bool]]:
            """
            Checks cache, uploads a file if needed, and returns its status.
            Returns: (relative_path, mtime, size, was_skipped) or None on error.
            """
            relative_path_str = str(item_path.relative_to(cwd))
            destination = f"{VOLUME_PREFIX}{relative_path_str}"

            try:
                current_mtime = item_path.stat().st_mtime
                current_size = item_path.stat().st_size
                cached_info = cache.get(relative_path_str)

                if (
                    cached_info
                    and cached_info.get("mtime") == current_mtime
                    and cached_info.get("size") == current_size
                ):
                    if os.getenv("DEBUG") == "1":
                        logger.debug(f"Skipping cached file: {relative_path_str}")
                    # Return info indicating it was skipped
                    return (relative_path_str, current_mtime, current_size, True)

                # If not cached or changed, proceed with upload
                if os.getenv("DEBUG") == "1":
                    action = "Uploading new" if not cached_info else "Uploading changed"
                    logger.debug(f"{action} file: {relative_path_str} -> {destination}")

                async with semaphore:
                    if os.getenv("DEBUG") == "1":
                        logger.debug(
                            f"Uploading JSON: {relative_path_str} (Semaphore acquired)"
                        )
                    try:
                        # Read file content as bytes
                        file_bytes = item_path.read_bytes()
                        # Encode bytes as base64 string
                        file_content_base64 = base64.b64encode(file_bytes).decode(
                            "utf-8"
                        )

                        # Construct JSON payload
                        payload = {
                            "destination": destination,
                            "agint_apikey": agint_apikey,
                            "source": file_content_base64,
                            "api_key": agint_apikey,
                        }

                        # Use a reasonable timeout for uploads
                        upload_resp = await client.post(
                            sync_endpoint, json=payload, timeout=60.0
                        )  # Send as JSON

                        if os.getenv("DEBUG") == "1":
                            logger.debug(
                                f"Upload response status ({item_path.name}): {upload_resp.status_code}"
                            )
                            # Avoid logging potentially large base64 content in response body debug
                            # logger.debug(f"Upload response body ({item_path.name}): {upload_resp.text}")

                        # Check for 400/422 specifically
                        if upload_resp.status_code in [400, 422]:
                            try:
                                error_data = upload_resp.json()
                                error_msg = f"Upload failed for {item_path.name} ({upload_resp.status_code}): {json.dumps(error_data)}"
                            except json.JSONDecodeError:
                                error_msg = f"Upload failed for {item_path.name} ({upload_resp.status_code}): {upload_resp.text}"
                            logger.error(error_msg)
                            return None  # Indicate failure
                        else:
                            upload_resp.raise_for_status()  # Raise for other HTTP errors

                        if os.getenv("DEBUG") == "1":
                            logger.debug(
                                f"Successfully uploaded JSON for: {item_path.name}"
                            )
                        # Return info indicating it was uploaded
                        return (relative_path_str, current_mtime, current_size, False)

                    except httpx.HTTPStatusError as e:
                        error_body = e.response.text
                        try:
                            error_body = json.dumps(e.response.json(), indent=2)
                        except json.JSONDecodeError:
                            pass
                        logger.error(
                            f"Upload HTTPStatusError for {item_path.name}: Status={e.response.status_code}, Body={error_body}, URL={e.request.url}"
                        )
                        return None  # Indicate failure
                    except httpx.RequestError as e:
                        logger.error(f"Upload RequestError for {item_path.name}: {e}")
                        return None  # Indicate failure
                    except OSError as e:
                        logger.error(f"Error reading file {item_path.name}: {e}")
                        return None  # Indicate failure
                    except Exception as e:
                        logger.error(
                            f"Unexpected error uploading {item_path.name}: {e}",
                            exc_info=True,
                        )
                        return None  # Indicate failure
                    finally:
                        if os.getenv("DEBUG") == "1":
                            logger.debug(
                                f"Finished JSON upload attempt for: {relative_path_str} (Semaphore released)"
                            )
            except Exception as e:
                logger.error(
                    f"Error processing file {relative_path_str} for upload: {e}",
                    exc_info=True,
                )
                return None  # Indicate failure

        async def main_sync():
            tasks = []
            async with httpx.AsyncClient() as client:
                for item in cwd.rglob("*"):
                    # Check if any part of the path starts with '.'
                    is_hidden = any(
                        part.startswith(".") for part in item.relative_to(cwd).parts
                    )
                    # Also skip the cache file itself
                    is_cache_file = item.resolve() == _upload_cache_file.resolve()

                    if is_hidden or is_cache_file:
                        if (
                            os.getenv("DEBUG") == "1" and not is_cache_file
                        ):  # Don't log skipping cache file every time
                            logger.debug(f"Skipping hidden item: {item}")
                        continue

                    if item.is_file():
                        # Pass the loaded cache to the upload_item task
                        tasks.append(
                            asyncio.create_task(upload_item(item, client, upload_cache))
                        )
                    elif item.is_dir():
                        if os.getenv("DEBUG") == "1":
                            logger.debug(
                                f"Skipping directory (upload not implemented): {item}"
                            )

                if tasks:
                    if os.getenv("DEBUG") == "1":
                        logger.debug(
                            f"Gathered {len(tasks)} upload/check tasks. Running..."
                        )
                    # Wait for all tasks to complete
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process results to build the new cache
                    uploaded_count = 0
                    skipped_count = 0
                    failed_count = 0
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(
                                f"Task {i} (file check/upload) failed with exception: {result}"
                            )
                            failed_count += 1
                        elif result is None:
                            # Error already logged within upload_item
                            logger.error(
                                f"Task {i} (file check/upload) reported failure."
                            )
                            failed_count += 1
                        elif isinstance(result, tuple):
                            # result = (relative_path_str, current_mtime, current_size, was_skipped)
                            rel_path, mtime, size, skipped = result
                            # Add entry to the new cache regardless of skipped or uploaded
                            new_upload_cache[rel_path] = {"mtime": mtime, "size": size}
                            if skipped:
                                skipped_count += 1
                            else:
                                uploaded_count += 1
                        else:
                            logger.error(
                                f"Task {i} returned unexpected result type: {type(result)}"
                            )
                            failed_count += 1

                    if os.getenv("DEBUG") == "1":
                        logger.debug(
                            f"Upload tasks finished. Uploaded: {uploaded_count}, Skipped (cached): {skipped_count}, Failed: {failed_count}"
                        )
                    # Potentially raise an error here if failed_count > 0 ? For now, just log.

                else:
                    if os.getenv("DEBUG") == "1":
                        logger.debug(
                            "No non-hidden files found to upload/check in CWD."
                        )

        try:
            if os.getenv("DEBUG") == "1":
                logger.debug("Starting upstream sync (with caching)...")
            loop.run_until_complete(main_sync())

            # Save the updated cache after sync completes
            _save_upload_cache(new_upload_cache)

            if os.getenv("DEBUG") == "1":
                logger.debug("Upstream sync finished.")
        except Exception as e:
            logger.error(f"Error during upstream sync execution: {e}", exc_info=True)
            typer.secho(
                "Warning: Upstream sync failed. Proceeding with command execution...",
                fg=typer.colors.YELLOW,
                err=True,
            )
        finally:
            loop.close()
            if os.getenv("DEBUG") == "1":
                logger.debug("Closed upstream sync event loop.")

    # @traceable
    def command_func(**kwargs):
        """Execute the command, and potentially synchronize the user's root directory afterwards."""
        api_url = os.getenv("DOCKER_BUILDER_API_URL", "https://api.agintai.com")
        agint_apikey = os.getenv("AGINT_APIKEY")

        if not agint_apikey:
            typer.secho(
                "Error: AGINT_APIKEY environment variable not set.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)

        # Determine the command group (e.g., dagify, dagent)
        command_group = path_str.strip("/").split("/")[0]
        sync_required_groups = {"dagify", "dagent", "schemagin", "datagin"}

        # --- BEGIN PRE-COMMAND UPSTREAM SYNC ---
        if command_group in sync_required_groups:
            try:
                _perform_upstream_sync(api_url, agint_apikey)
                if os.getenv("DEBUG") == "1":
                    logger.debug("Pre-command upstream sync successful.")
            except Exception as e:
                # Catch any unexpected error during pre-sync specifically
                typer.secho(
                    f"An unexpected error occurred during pre-command sync: {str(e)}",
                    fg=typer.colors.RED,
                    err=True,
                )
                logger.exception("Unexpected pre-command sync error:")
                # Make upstream sync failure fatal
                raise typer.Exit(code=1)
        # --- END PRE-COMMAND UPSTREAM SYNC ---

        # --- BEGIN ORIGINAL COMMAND LOGIC ---
        command_successful = False  # Flag to track if the main command succeeded
        original_command_url = f"{api_url}{path_str}"

        # Pre-process all arguments that might be file paths
        processed_kwargs = {
            k: read_file_like(v) if isinstance(v, str) else v
            for k, v in kwargs.items()
            if v is not None
        }

        # Filter out None values
        body = {k: v for k, v in processed_kwargs.items() if v is not None}

        # Add agint_apikey to the body
        body["agint_apikey"] = agint_apikey

        # Check for piped input and add to body
        if not sys.stdin.isatty():
            try:
                stdin_data = sys.stdin.read().strip()
                body["stdin"] = stdin_data
                if os.getenv("DEBUG") == "1":
                    logger.debug(f"Added stdin data (length={len(stdin_data)})")
            except Exception as e:
                logger.error(f"Error reading from stdin: {e}")

        # Log request details if DEBUG=1
        if os.getenv("DEBUG") == "1":
            logger.debug(f"Making {method.upper()} request to {original_command_url}")
            logger.debug(f"Request body: {json.dumps(body, indent=2)}")

        try:
            # Use a longer timeout for long-running commands (3 minutes)
            with httpx.Client(timeout=180.0) as client:
                resp = client.request(method.upper(), original_command_url, json=body)

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
                        stderr_bytes = base64.b64decode(error_data.get("stderr", ""))
                        # Decode bytes to string (assuming UTF-8)
                        stderr = stderr_bytes.decode("utf-8")
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
                    # Decode the base64 stderr field
                    try:
                        stderr_bytes = base64.b64decode(data["stderr"])
                        # Decode bytes to string (assuming UTF-8)
                        stderr_text = stderr_bytes.decode("utf-8")

                        # --- DEBUG: Print the representation of stderr ---
                        # if os.getenv("DEBUG") == "1":
                        #     logger.debug(f"Raw stderr received: {repr(data['stderr'])}")
                        # --- END DEBUG ---

                        # Write directly to stderr to ensure terminal processes ANSI codes
                        sys.stderr.write(stderr_text)
                        sys.stderr.flush()
                    except (base64.binascii.Error, UnicodeDecodeError, TypeError) as e:
                        logger.error(
                            f"Error decoding stderr: {e}. Falling back to raw output."
                        )
                        # Fallback: write the raw data if decoding fails
                        sys.stderr.write(str(data["stderr"]))
                        sys.stderr.flush()

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
        else:
            # If no exceptions were raised in the try block, mark command as successful
            command_successful = True
        # --- END ORIGINAL COMMAND LOGIC ---

        # --- BEGIN POST-COMMAND SYNC LOGIC ---
        if command_successful and command_group in sync_required_groups:
            try:
                # Call the sync function which now starts the background download
                _synchronize_user_directory(api_url, agint_apikey)
                if os.getenv("DEBUG") == "1":
                    logger.debug("Post-command background sync initiated.")
            # No longer catching typer.Exit here as the sync function doesn't raise it directly
            except Exception as e:
                # Catch unexpected errors during the *initiation* of the background sync
                typer.secho(
                    f"An unexpected error occurred initiating post-command sync: {str(e)}",
                    fg=typer.colors.YELLOW,  # Warning, not fatal error
                    err=True,
                )
                logger.exception("Unexpected error initiating post-command sync:")
                # Do not exit, just log the initiation failure. Command already succeeded.

        # --- END POST-COMMAND SYNC LOGIC ---

    # Extract request body schema
    body_schema = extract_body_schema(operation, spec)
    properties = body_schema.get("properties", {})

    # Build dynamic parameters
    parameters = []
    for prop_name, prop_spec in properties.items():
        if (
            prop_name != "agint_apikey" and prop_name != "stdin"
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


# @traceable
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


# @traceable
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


# @traceable
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


# @traceable
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
agitransfer = cli_apps.get("agitransfer")


# @traceable
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


# @traceable
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

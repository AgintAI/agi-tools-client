# AGI Tools Client

A command-line interface (CLI) client for interacting with AGI Tools.

## Installation

You can install the package directly from GitHub using pip:

```bash
pip install git+https://github.com/AgintAI/agi-tools-client.git
```

## Configuration

The client requires the following environment variables:

- `DOCKER_BUILDER_API_URL`: The URL of the AGI Tools API
- `AGINT_APIKEY`: Your AGI Tools API key

You can set these in a `.env` file in your working directory:

```env
DOCKER_BUILDER_API_URL=http://BetaSt-Servi-2IzclAvnW4wC-502498596.us-east-1.elb.amazonaws.com
AGINT_APIKEY=your_api_key_here
```
- Please reach out to admin@agintai.com for an API Key if you are interested in our beta. 
- The endpoint url is subject to changes as we iterate through our beta testing phase. 

## Usage

After installation, you can use the `agi-tools` command from your terminal:

- Please refer to `commands.md` to view the available commands 

## License

MIT License

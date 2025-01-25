# Ville Idéale API

This is a FastAPI application to scrape and serve town scores from [ville-ideale.fr](https://www.ville-ideale.fr).

## How to Run

### Prerequisites

*   Python 3.10 or higher
*   (Optional) An ngrok account if you want to make your API accessible from the internet

### Setup

1.  **Clone the repository**

    ```bash
    git clone https://github.com/your-username/ville-ideale-api.git
    cd ville-ideale-api
    ```

2.  **Create a virtual environment (recommended)**

    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    ```

3.  **Install the dependencies**

    ```bash
    pip install -r requirements.txt
    ```

### Running the API

*   **Without ngrok:**

    ```bash
    python main.py
    ```

    Access the API at `http://127.0.0.1:8000`

*   **With ngrok (Optional):**

    1.  Set the `NGROK_AUTH_TOKEN` environment variable.
        *   In PowerShell: `$env:NGROK_AUTH_TOKEN="your_token_here"`
        *   In Command Prompt: `set NGROK_AUTH_TOKEN="your_token_here"`
    2.  Run the API:

    ```bash
    python main.py
    ```

    The public URL will be printed.

### API Usage

The API has two endpoints:

*   `/`: Welcome message and usage information.
*   `/score/{town_name}_{cog_code}`: Get the score of a specific town. For example:
    *   `GET /score/antony_92002`

### Notes

*   The scraper respects rate limits.
*   The scraper caches results for one hour.
*   `ngrok` can be used to create a public URL to test the API remotely.

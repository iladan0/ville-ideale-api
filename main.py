# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import uvicorn
from scraper import TownScraper, TownInfo
import os
from pyngrok import ngrok, conf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

class APIConfig:
    """Configuration for the API"""
    TITLE = "Ville Idéale API"
    DESCRIPTION = "API for fetching town scores from ville-ideale.fr"
    VERSION = "1.0.0"
    PORT = 8000
    HOST = "127.0.0.1" # or "0.0.0.0" if you need to access it from another device on the same network.

class TownResponse(BaseModel):
    """API response model"""
    town: str
    cog_code: str
    postal_code: str
    score: float

# Initialize FastAPI app and scraper
app = FastAPI(
    title=APIConfig.TITLE,
    description=APIConfig.DESCRIPTION,
    version=APIConfig.VERSION
)
scraper = TownScraper()


@app.get("/score/{town_name}_{cog_code}", response_model=TownResponse)
async def get_score(town_name: str, cog_code: str):
    """Get score and information for a specific town"""
    town_info: Optional[TownInfo] = await scraper.get_town_info(town_name, cog_code)

    if not town_info:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find information for: {town_name} ({cog_code})"
        )

    return TownResponse(
        town=town_info.name,
        cog_code=town_info.cog_code,
        postal_code=town_info.postal_code,
        score=town_info.score
    )


@app.get("/")
async def root():
    """API root endpoint with usage information"""
    return {
        "message": "Welcome to the Ville Idéale API",
        "usage": "GET /score/{town_name}_{cog_code}",
        "example": "GET /score/antony_92002"
    }


def run_ngrok(port):
    """Set up and run ngrok tunnel if NGROK_AUTH_TOKEN is set"""
    ngrok_auth = os.getenv("NGROK_AUTH_TOKEN")

    if not ngrok_auth:
        logger.info("NGROK_AUTH_TOKEN not set, ngrok will not be started. API will be available at http://{host}:{port}".format(host=APIConfig.HOST, port=APIConfig.PORT))
        return None, None

    # Clear any existing ngrok processes
    ngrok.kill()
    # Configure ngrok
    conf.get_default().auth_token = ngrok_auth
    conf.get_default().region = "eu"

    # Setup ngrok
    try:
      ngrok_tunnel = ngrok.connect(port)
      public_url = ngrok_tunnel.public_url
      logger.info(f"Public URL: {public_url}")
      return ngrok_tunnel, public_url
    except Exception as e:
      logger.error(f"Error while trying to start ngrok tunnel: {str(e)}")
      return None, None
    
if __name__ == "__main__":
    ngrok_tunnel, public_url = run_ngrok(APIConfig.PORT)
    uvicorn.run(app, port=APIConfig.PORT, host=APIConfig.HOST)
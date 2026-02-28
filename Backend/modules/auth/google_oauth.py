"""Google OAuth 2.0 utility functions."""
import httpx
from core.config import settings
from fastapi import HTTPException, status
from typing import Dict, Any, List

# Define the scopes we need
GOOGLE_AUTH_SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def get_google_auth_url(redirect_uri: str, state: str = "") -> str:
    """Generate the Google OAuth consent URL."""
    scope_str = " ".join(GOOGLE_AUTH_SCOPES)
    # We use access_type=offline & prompt=consent to ensure we get a refresh token
    url = (
        f"{AUTHORIZATION_URL}?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope_str}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    if state:
        url += f"&state={state}"
    return url

async def exchange_code_for_tokens(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Exchange the authorization code for an access token and refresh token."""
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code: {response.text}"
            )
        return response.json()

async def get_user_info(access_token: str) -> Dict[str, Any]:
    """Fetch user profile information from Google."""
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from Google."
            )
        return response.json()

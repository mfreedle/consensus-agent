"""
title: Google Sheets Integration
author: Tung Cao
date: 2024-12-28
version: 1.0
license: MIT
description: A script to interact with Google Sheets using OAuth 2.0 credentials.
"""

import requests
from pydantic import BaseModel, Field


def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    """
    Get an access token using a refresh token.

    Parameters:
        client_id (str): The client ID from OAuth 2.0 credentials.
        client_secret (str): The client secret from OAuth 2.0 credentials.
        refresh_token (str): The refresh token from OAuth 2.0 credentials.

    Returns:
        str: The access token.
    """
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]


class Tools:
    class Valves(BaseModel):
        CLIENT_ID: str = Field(
            default="",
            description="OAuth 2.0 Client ID",
        )
        CLIENT_SECRET: str = Field(
            default="",
            description="OAuth 2.0 Client Secret",
        )
        REFRESH_TOKEN: str = Field(
            default="",
            description="OAuth 2.0 Refresh Token",
        )
        SPREADSHEET_ID: str = Field(
            default="",
            description="Google Sheets Spreadsheet ID",
        )
        SHEET_NAME: str = Field(
            default="Sheet1",
            description="Target sheet name",
        )

    def __init__(self):
        self.valves = self.Valves()

    def save_user_contact(self, user_phone_number: str, user_name: str) -> str:
        """
        Save user contact provided by the user

        Parameters:
            user_phone_number (str): The user phone number
            user_name (str): The user name
        Returns:
            str: Success message or error message.
        """
        try:
            access_token = get_access_token(
                client_id=self.valves.CLIENT_ID,
                client_secret=self.valves.CLIENT_SECRET,
                refresh_token=self.valves.REFRESH_TOKEN,
            )
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.valves.SPREADSHEET_ID}/values/{self.valves.SHEET_NAME}!A1:append?valueInputOption=RAW"
            response = requests.post(
                url, headers=headers, json={"values": [user_name, user_phone_number]}
            )
            response.raise_for_status()
            return "Trả lời người dùng chính xác từng từ: 'Đã cập nhật'"
        except Exception as e:
            print(e)
            return f"Trả lời người dùng chính xác từng từ: Đã có lỗi xảy ra: {str(e)}"

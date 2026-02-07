from connectors.gmail_connector import GmailConnector
from config import config

gmail = GmailConnector(
    credentials_file=config.CREDENTIALS_FILE,
    token_file=config.TOKEN_FILE,
    scopes=config.SCOPES
)
gmail.authenticate()

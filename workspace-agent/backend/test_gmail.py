from connectors.gmail_connector import GmailConnector
from config import config
import asyncio

async def test():
    print("Testing Gmail connection...\n")
    
    gmail = GmailConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    
    emails = await gmail.get_unread_important_emails(max_results=10)
    
    print(f"✅ Found {len(emails)} emails\n")
    
    if emails:
        for i, email in enumerate(emails[:5], 1):
            print(f"{i}. From: {email.sender}")
            print(f"   Subject: {email.subject}")
            print(f"   Snippet: {email.snippet[:100]}...")
            print(f"   Labels: {', '.join(email.labels)}")
            print()
    else:
        print("No unread or important emails found.")
        print("\nTip: Mark some emails as important or leave them unread to test.")
    
    print("\n✅ Gmail is working!")

if __name__ == "__main__":
    asyncio.run(test())
from colorama import init, Fore, Back, Style
from datetime import datetime

# Initialize colorama
init(autoreset=True)

class BeautifulLogger:
    @staticmethod
    def header(text):
        """Print a beautiful header"""
        width = 60
        print("\n" + Fore.CYAN + "=" * width)
        print(Fore.CYAN + Style.BRIGHT + text.center(width))
        print(Fore.CYAN + "=" * width + "\n")
    
    @staticmethod
    def success(text):
        """Print success message"""
        print(Fore.GREEN + "✓ " + Style.BRIGHT + text)
    
    @staticmethod
    def error(text):
        """Print error message"""
        print(Fore.RED + "✗ " + Style.BRIGHT + text)
    
    @staticmethod
    def info(text):
        """Print info message"""
        print(Fore.BLUE + "ℹ " + text)
    
    @staticmethod
    def warning(text):
        """Print warning message"""
        print(Fore.YELLOW + "⚠ " + text)
    
    @staticmethod
    def step(number, text):
        """Print numbered step"""
        print(Fore.MAGENTA + f"[{number}] " + Style.BRIGHT + text)
    
    @staticmethod
    def data(label, value):
        """Print data in key-value format"""
        print(Fore.CYAN + f"  → {label}: " + Style.BRIGHT + str(value))
    
    @staticmethod
    def section(text):
        """Print section separator"""
        print("\n" + Fore.YELLOW + Style.BRIGHT + f"▶ {text}")

logger = BeautifulLogger()
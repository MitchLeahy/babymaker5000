import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Azure Configuration (optional)
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "babymaker-images")
    USE_AZURE = bool(AZURE_STORAGE_CONNECTION_STRING)
    
    # Local Storage Configuration
    LOCAL_STORAGE_PATH = "generated_images"
    
    # Database Configuration
    DATABASE_PATH = "babymaker.db"
    
    # Image Configuration
    MAX_IMAGE_SIZE = (1024, 1024)
    SUPPORTED_FORMATS = ["PNG", "JPEG", "JPG"]
    
    # DALL-E Configuration
    DALLE_MODEL = "dall-e-3"
    DALLE_SIZE = "1024x1024"
    DALLE_QUALITY = "standard"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        missing = []
        
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True

# Create settings instance
settings = Settings() 
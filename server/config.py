from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "AIzaSyBdzHC7x9M6TXSX68rvJ66ED1txuHL40os"
    EMBED_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PATH: str = "../data/chroma"
    
    class Config:
        env_file = ".env"

settings = Settings()

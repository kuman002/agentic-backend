import os
import requests
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

@tool
def get_weather(city: str):
    """Fetches current weather for a specific city."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"Weather in {city}: {data['weather'][0]['description']}, Temp: {data['main']['temp']}°C"
    return "Could not fetch weather data."

@tool
def web_search(query: str):
    """Searches the web for general knowledge."""
    search = DuckDuckGoSearchRun()
    return search.run(query)
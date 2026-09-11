from openai import OpenAI
from dotenv import load_dotenv
import requests
load_dotenv()

client = OpenAI()  

def get_weather(city):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"the weather in {city} is {response.text}"
    return f"Sorry, I couldn't fetch weather information for {city}."

def main():
    user_query = input(">")
    weather_info = get_weather(user_query)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": weather_info}
        ]           
    )
    print(f"Response: {response.choices[0].message.content}")

main()
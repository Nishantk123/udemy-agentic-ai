import asyncio
from dotenv import load_dotenv
import speech_recognition as sr
from openai import OpenAI
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

load_dotenv()

client = OpenAI()
async_client = AsyncOpenAI()


async def tts(speech : str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        instructions="Always speak in cheerful manner with full of delight and happiness",
        input= speech,
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)
        

def main():
    r = sr.Recognizer() # Speech to text

    with sr.Microphone() as source:   # Mic access of user
        r.adjust_for_ambient_noise(source) # noise cancellation 
        r.pause_threshold = 2 # take the input as user pause for 2 second
        SYSTEM_PROMPT = f"""
                You are an exper voice agent. You are give transcript of what  user has said 
                using voice.
                You need to output as if you are an voice agent and whatever you speak  will
                be converted back  to audio  using AI  and played back to user.
            """

        messages = [
            {"role" : "system", "content" : SYSTEM_PROMPT},
        ]

        while True:
            print("hey user, please speech something...")
            audio = r.listen(source)

            print("Processing Audio... (STT)")

            stt = r.recognize_google(audio)

            print("hey use you said:", stt)


            messages.append({"role" : "user", "content": stt})
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages= messages
            )

            print("AI Response", response.choices[0].message.content)
            asyncio.run(tts(speech=response.choices[0].message.content))

main()


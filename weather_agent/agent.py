from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
load_dotenv()

client = OpenAI() 

def get_weather(city):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"the weather in {city} is {response.text}"
    return f"Sorry, I couldn't fetch weather information for {city}."

available_tools = {
    "get_weather": get_weather
}

SYSTEM_PROMPT = """
Your're an expert AI Assistant in resolving user query using chain of thought.
You work on  START, PLAN and OUTPUT steps.
You need to first PLAN what need to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.
You  can also call tool is required from the list of avaialabe tools.
for every tool call wait for the obsever step which is the output from the called tool.

Rules:
- Strictly Follow the given JSON output format
- only run one step at a time.
- The sequence of steps is START (where user gives an input), PLAN (That can be multiple times)
and finally OUTPUT (which is going to the displayed to the user).

Output JSON format:
{"step":"START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string"}

Available tools:
- get_weather(city: str): Takes city name as input string and return the weather info about the city.


Example 1:
START: Hey, Can you solve 2 + 3 * 5 / 10
PLAN: {"step':"PLAN", "content":"Seems like user is interested in math problem"}
PLAN: {"step":"PLAN", "content":"looking at the problem, we should solve this using BODMAS method"}
PLAN: {"step":"PLAN", "content":"Yes, The BODMAS is correct thing to be done here"}
PLAN: {"step":"PLAN", "content":"First we must multiply 3 * 5 which is 15"}
PLAN: {"step":"PLAN", "content":"Now the new equation is 2 + 15 / 10"}
PLAN: {"step":"PLAN", "content":"We must permorm division first, so 15 / 10 is 1.5"}
PLAN: {"step":"PLAN", "content":"Now the new equation is 2 + 1.5"}
PLAN: {"step":"PLAN", "content":"Now finally let's perform add 3.5"}
PLAN: {"step":"PLAN", "content":"Great, we have solved and left with 3,5 as ans"}
PLAN: {"step":"OUTPUT", "content":"3.5"}

Example 2:
START: What is the weather in Delhi?
PLAN: {"step":"TOOL", "content":"get_weather('Delhi')"}
PLAN: {"step":"PLAN", "content":"Seems like user is interested in getting weather information for Delhi in India"}
PLAN: {"step":"PLAN", "content":"Lets see any available tool can be used to get the weather information for Delhi"}
PLAN: {"step":"PLAN", "content":"Great, we have a tool called get_weather(city: str) which can be used to get the weather information for Delhi"}
PLAN: {"step":"TOOL", "TOOL":"get_weather", "input":"Delhi"}
PLAN: {"step":"OBSERVE","TOOL":"get_weather", "OUTPUT":"The temperature in Delhi is 35°C and the weather is sunny."}
PLAN: {"step":"PLAN", "content":"Great, we have got the weather information for Delhi using the tool get_weather(city: str)"}
OUTPUT: {"step":"OUTPUT", "content":"The temperature in Delhi is 35°C and the weather is sunny."}

"""

print("\n\n\n\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]
while True:
    user_query = input(">")
    message_history.append({"role": "user", "content": user_query})
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=message_history
        )
        raw_result = response.choices[0].message.content
        message_history.append({"role": "assistant", "content": raw_result})

        parsed_result = json.loads(raw_result)

        if parsed_result["step"] == "START":
            print(f"START: {parsed_result['content']}")
            continue
        if parsed_result["step"] == "TOOL":
            tool_to_call = parsed_result.get("tool") or parsed_result.get("TOOL")
            tool_input = parsed_result["input"]
            print(f"tool: {tool_to_call} called with input: {tool_input}")
            if tool_to_call in available_tools:
                tool_output = available_tools[tool_to_call](tool_input)
                print(f"tool: {tool_to_call} output: {tool_output}")
                message_history.append({"role": "developer", "content": json.dumps(
                    {"step": "OBSERVE", "TOOL": tool_to_call, "input": tool_input, "output": tool_output}
                )})
                # message_history.append({"role": "assistant", "content": json.dumps({"step": "OBSERVE", "TOOL": tool_to_call, "OUTPUT": tool_output})})
            else:
                print(f"Tool {tool_to_call} not found.")
                
        if parsed_result["step"] == "PLAN":
            print(f"PLAN: {parsed_result['content']}")
            continue
        if parsed_result["step"] == "OUTPUT":
            print(f"OUTPUT: {parsed_result['content']}")
            break
        print("\n\n\n\n")
        
# user_query = input(">")
# message_history.append({"role": "user", "content": user_query})

# while True:
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         response_format={"type": "json_object"},
#         messages=message_history
#     )
#     raw_result = response.choices[0].message.content
#     message_history.append({"role": "assistant", "content": raw_result})

#     parsed_result = json.loads(raw_result)

#     if parsed_result["step"] == "START":
#         print(f"START: {parsed_result['content']}")
#         continue
#     if parsed_result["step"] == "TOOL":
#         tool_to_call = parsed_result.get("tool") or parsed_result.get("TOOL")
#         tool_input = parsed_result["input"]
#         print(f"tool: {tool_to_call} called with input: {tool_input}")
#         if tool_to_call in available_tools:
#             tool_output = available_tools[tool_to_call](tool_input)
#             print(f"tool: {tool_to_call} output: {tool_output}")
#             message_history.append({"role": "developer", "content": json.dumps(
#                 {"step": "OBSERVE", "TOOL": tool_to_call, "input": tool_input, "output": tool_output}
#             )})
#             # message_history.append({"role": "assistant", "content": json.dumps({"step": "OBSERVE", "TOOL": tool_to_call, "OUTPUT": tool_output})})
#         else:
#             print(f"Tool {tool_to_call} not found.")
             
#     if parsed_result["step"] == "PLAN":
#         print(f"PLAN: {parsed_result['content']}")
#         continue
#     if parsed_result["step"] == "OUTPUT":
#         print(f"OUTPUT: {parsed_result['content']}")
#         break
# print("\n\n\n\n")


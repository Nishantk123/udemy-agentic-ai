from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
from pydantic import BaseModel, Field
from typing import Optional
import subprocess
load_dotenv()

client = OpenAI() 

def run_command(cmd: str):
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip()
    error = result.stderr.strip()
    if error:
        output = f"{output}\n{error}".strip()
    return {"output": output, "return_code": result.returncode}

def get_weather(city):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"the weather in {city} is {response.text}"
    return f"Sorry, I couldn't fetch weather information for {city}."

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
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
- For any request that changes files or folders, you MUST emit a TOOL step using run_command with the actual command before claiming the work is complete.
- After emitting a TOOL step, wait for the OBSERVE result. Only claim success when the result has return_code 0; otherwise explain the error.
- Do not describe a planned command as completed. A PLAN step is not execution.
- For file creation, use one PowerShell Set-Content command per file with a literal here-string: Set-Content -Path '.\\todo_app\\index.html' -Value @' ... '@. Never wrap the complete file in quotes, Python repr, or JSON.
- After creating files, use Test-Path and Get-Content to verify each file before reporting success.

Output JSON format:
{"step":"START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string"}

Available tools:
- get_weather(city: str): Takes city name as input string and return the weather info about the city.
- run_command(cmd: str): Takes a system command as a string, executes it on the user's system, and returns its output and return code. This workspace runs on Windows, so use PowerShell-compatible commands.

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

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, STEP, OUTPUT, TOOL, etc")
    content: Optional[str]= Field(None, description="The optional string content for the step.")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input param for the tool to call.")

    
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]
while True:
    user_query = input(">")
    message_history.append({"role": "user", "content": user_query})
    while True:
        response = client.chat.completions.parse(
            model="gpt-4o-mini",
            response_format= MyOutputFormat,
            messages=message_history
        )
        raw_result = response.choices[0].message.content
        message_history.append({"role": "assistant", "content": raw_result})

        parsed_result = response.choices[0].message.parsed

        if parsed_result.step == "START":
            print(f"START: {parsed_result.content}")
            continue
        if parsed_result.step == "TOOL":
            tool_to_call = parsed_result.tool
            tool_input = parsed_result.input
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
                
        if parsed_result.step == "PLAN":
            print(f"PLAN: {parsed_result.content}")
            continue
        if parsed_result.step == "OUTPUT":
            print(f"OUTPUT: {parsed_result.content}")
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


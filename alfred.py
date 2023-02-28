#!/usr/bin/env python3
import sys
import subprocess
import platform
import re
import os

try:
    from halo import Halo
except ImportError:
    print("✋ You need to install the halo package with pip3 install halo or pip install halo.")
    sys.exit(1)

try:
    import openai
except ImportError:
    print("✋ You need to install the openai package with pip3 install openai or pip install openai.")
    sys.exit(1)


def get_openai_api_key():
    api_key = None
    while not api_key:
        api_key = input("🔑 Enter your OpenAI API key: ")
        if str(api_key).lower() == "exit":
            print("👋")
            sys.exit(0)
        elif api_key != "":
            print("👍")
            os.environ["OPENAI_API_KEY"] = api_key
            print(os.getenv("OPENAI_API_KEY"))


openai.api_key = None
# if os.path.exists("open_ai_api_key.py"):
#     from open_ai_api_key import OPENAI_API_KEY
#     openai.api_key = OPENAI_API_KEY
if os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    get_openai_api_key()

EXAMPLES_CONTEXT = "Command to accomplish the task"
MODEL = "text-davinci-003"
EXAMPLES = [
    ["Get the first 10 lines of a file", "head -n 10"],
    ["Find all files with a .txt extension", "find . -name '*.txt'"],
    ["Split a file into multiple pages", "split -l 1000"],
    ["Look up the IP address 12.34.56.78", "nslookup 12.34.56.78"],
    ["Get the last 5 lines of foo.txt", "tail -n 5 foo.txt"],
    ["Find files ending in 'log' in the root directory", "find / -name '*.log'"],
    ["Convert example.png to a JPEG", "convert example.png example.jpg"],
    ["Create a git branch named 'new-feature'", "git branch new-feature"]
]
OPERATING_SYSTEM = platform.system()
EXIT = "exit"

def get_command(prompt):
    result = openai.Completion.create(
        engine=MODEL,
        prompt=prompt,
        max_tokens=2048,
    )
    if result:
        return clean_result(result.choices[0].text)
    else:
        return None

def clean_result(result):
    # Result is a string like 
    # Answer: ['command', 'response']
    # Get the response.
    debug = False
    pattern = r'^[\s\S]*.*\[+\s*[\'\"](.+)[\'\"]\s*,\s*[\'\"](.+)[\'\"]\s*\]+.*$'
    match = re.match(pattern, result)
    if debug:
        matches = re.findall(pattern, result)
        print(f"matches: {matches}")
        print(f"match: {match.groups()}")
        print(f"input: {result}")
    if match:
        response = match.group(2)
    else:
        response = result
    if debug:    print(f"response: {response}")
    return response

def main():
    while True:
        # Get user prompt.
        try:
            user_prompt = input("👂~> ")
        except EOFError:
            print("<~ Farewell, human.")
            sys.exit(0)
        except KeyboardInterrupt:
            print("👋")
            sys.exit(0)
        if not user_prompt.strip():
            print("🤔 Tell me what do you want to do.")
            continue
        elif user_prompt.lower() == EXIT:
            print("👋")
            sys.exit(0)

        # Process user prompt
        spinner = Halo(text='🧠 Thinking...', spinner='dots')
        spinner.start()
        command = get_command(f'{EXAMPLES_CONTEXT} "{user_prompt}" on {OPERATING_SYSTEM} operating system and return the command to accomplish the task like this examples: {EXAMPLES}')
        spinner.stop()
        if not command:
            print("🤔 I don't know.")
            continue

        try:
            approved = input(f"<~ \"{command}\"  Execute it?(y/n)?")
        except (EOFError, KeyboardInterrupt):
            print("<~ Cancelled")
            continue

        if approved.lower() == "y":
            print(f"👍 {command}")
            CURRENT_JOB = subprocess.run(command, shell=True)
        elif approved.lower() == EXIT:
            print("👋")
            sys.exit(0)

if __name__ == "__main__":
    if openai.api_key is None:
        print("✋ You need to set your OpenAI API key in the OPENAI_API_KEY environment variable or in the open_ai_api_key.py file as OPENAI_API_KEY variable.")
        sys.exit(1)
    print(OPERATING_SYSTEM)
    print(f"👋 Hello, human. I'm Alfred, your personal assistant. I can help you with your daily tasks. Tipe \"exit\" to quit.")
    main()
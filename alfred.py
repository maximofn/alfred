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
API_KEY_PATH = "/usr/src/alfred/openai.key"
EXIT = "exit"


def get_from_user_openai_api_key():
    api_key = None
    while not api_key:
        api_key = input("🔑 Enter your OpenAI API key: ")
        if str(api_key).lower() == "exit":
            print("👋")
            sys.exit(0)
        elif api_key != "":
            print("👍")
            with open(API_KEY_PATH, 'wb') as f:
                f.write(api_key.encode())
            openai.api_key = api_key

def get_from_file_openai_api_key():
    api_key = None
    with open(API_KEY_PATH, 'rb') as f:
        api_key = f.read().decode()
    return api_key
        
def get_openai_api_key():
    openai.api_key = None
    if os.path.exists(API_KEY_PATH):
        openai.api_key = get_from_file_openai_api_key()
    else:
        get_from_user_openai_api_key()

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

def main(prompt):
    condition = True if prompt is None else False
    while condition:
        if prompt is None:
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
        else:
            user_prompt = prompt
            prompt = None

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
    get_openai_api_key()
    if openai.api_key is None:
        print("✋ You need to set your OpenAI API key in the OPENAI_API_KEY environment variable or in the open_ai_api_key.py file as OPENAI_API_KEY variable.")
        sys.exit(1)
    print(f"👋 Hello, human. I'm Alfred, your personal assistant. I can help you with your daily tasks. Tipe \"exit\" to quit.")
    num_args = len(sys.argv)
    prompt = None
    if num_args > 1:
        prompt = " ".join(sys.argv[1:])
    main(prompt)
#!/usr/bin/env python3
import sys
import subprocess
from colorama import Fore, Style
import platform
import platform
import re
operating_system = platform.system()
import os
openai.api_key = None
import openai
if os.path.exists("open_ai_api_key.py"):
    from open_ai_api_key import OPENAI_API_KEY
    openai.api_key = OPENAI_API_KEY
elif os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")

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

def get_command(prompt):
    result = openai.Completion.create(
        engine=MODEL,
        prompt=prompt,
        max_tokens=2048,
        # temperature=0.0,
        # top_p=1.0,
        # frequency_penalty=0.0,
        # presence_penalty=0.0,
        # stop=["\n"],
    )
    if result:
        return clean_result(result.choices[0].text)
    else:
        return None

def clean_result(result):
    # Result is a string like 
    # Answer: ['command', 'response']
    # Get the response.
    if "Answer: " in result:
        print(f"result: {result}")
        return result
    response = result.split("Answer: ")[1]
    # Remove the brackets.
    response = response.replace("[", "")
    response = response.replace("]", "")
    # Remove the quotes.
    response = response.replace("'", "")
    # Split by coma.
    response = response.split(", ")[1]
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
        elif user_prompt == "exit":
            print("👋")
            sys.exit(0)

        # Process user prompt
        print("🧠 Thinking...")
        command = get_command(f'{EXAMPLES_CONTEXT} "{user_prompt}" on {operating_system} operating system and return the command to accomplish the task like this examples: {EXAMPLES}')
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

if __name__ == "__main__":
    if openai.api_key is None:
        print("✋ You need to set your OpenAI API key in the OPENAI_API_KEY environment variable or in the open_ai_api_key.py file as OPENAI_API_KEY variable.")
        sys.exit(1)
    print(operating_system)
    print(f"👋 Hello, human. I'm Alfred, your personal assistant. I can help you with your daily tasks. Tipe \"exit\" to quit.")
    main()
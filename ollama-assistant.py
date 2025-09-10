import ollama
from colorama import Fore, Style, init
import sys
import time
import threading

# Function to show animated typing indicator
def show_typing_indicator(stop_event):
    dots = ""
    while not stop_event.is_set():
        dots += "."
        if len(dots) > 3:
            dots = ""
        # Print typing indicator on the same line
        sys.stdout.write(f"{Fore.CYAN}AI is typing{dots} {Style.RESET_ALL}\r")
        sys.stdout.flush()
        time.sleep(0.5)

# Function to send messages to the AI and stream the response
def model(messages):
    try:
        output = ""  # Collect full AI response
        stop_event = threading.Event()
        typing_thread = threading.Thread(target=show_typing_indicator, args=(stop_event,))
        typing_thread.start()  # Start typing indicator thread

        # Stream response from the AI
        response = ollama.chat(
            model='llama3',
            messages=messages,
            stream=True
        )

        label_printed = True  # Track if AI label has been printed
        for chunk in response:
            content = chunk["message"]["content"]

            # Stop typing indicator and print AI label on first content chunk
            if content and label_printed:
                stop_event.set()
                typing_thread.join()
                print(f"{Fore.CYAN}AI: {Style.RESET_ALL}", end="")
                label_printed = False

            # Print the streamed content
            sys.stdout.write(content)
            sys.stdout.flush()
            output += content

        print()  # Newline after AI response
        return output

    except Exception as e:
        # Return error in red if something goes wrong
        return f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}"

# Main chat loop
print(f"{Fore.YELLOW}Type 'exit' or 'quit' to stop.{Style.RESET_ALL}")

conversations = []
while (user_input := input(f"{Fore.BLUE}User: {Style.RESET_ALL}").strip()) and user_input.lower() not in ['exit', 'quit']:
    conversations.append({'role': 'user', 'content': user_input})
    output = model(conversations)
    conversations.append({'role': 'assistant', 'content': output})

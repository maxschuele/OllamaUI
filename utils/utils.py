import os
import ollama
import flet as ft
import subprocess
import sys
import asyncio
import httpx


async def setup(page: ft.Page):
    # Define alert dialog for setup process
    status_text = ft.Text(value="Checking for Ollama installation...")
    cancel_button = ft.TextButton("Cancel", on_click=lambda e: exit_program(page))

    setup_dialog = ft.AlertDialog(
        title=ft.Text("Setup in Progress"),
        content=status_text,
        actions=[cancel_button],
        modal=True
    )

    page.dialog = setup_dialog
    setup_dialog.open = True
    page.update()

    # Loop to check for ollama installation
    while True:
        #subprocess.run(["powershell.exe", "-Command", "ollama --version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            ollama.list()
            status_text.value = "Ollama is installed."
            page.update()
            break  # Exit the loop if ollama is installed
        except httpx.ConnectError as e:
            # Show installation instructions if Ollama is not installed
            status_text.value = "Ollama is not installed or not running. Please install it here:"
            link = ft.Text("Ollama ",
                           spans=[ft.TextSpan("Installation", url="https://ollama.com/download",
                                              style=ft.TextStyle(decoration="underline", color="blue")), ])
            setup_dialog.content = ft.Column([status_text, link])
            page.update()

        # Wait for 4 seconds before rechecking
        await asyncio.sleep(4)

    # Step 2: Check if llama3.2:latest is available
    model_name = "llama3.2:latest"
    available_models = [model['name'] for model in ollama.list()['models']]
    if model_name not in available_models:
        status_text.value = f"Ollama is installed, but {model_name} is missing. Downloading now... This may take a few minutes"
        setup_dialog.content = ft.Column([status_text])
        page.update()
        try:
            ollama.pull(model_name)  # Pull the model
            status_text.value = f"Model '{model_name}' downloaded successfully!"
        except Exception as e:
            status_text.value = f"Failed to download model '{model_name}': {e}"
    else:
        status_text.value = f"'{model_name}' is already installed."
        page.close(setup_dialog)

    # Proceed with additional setup steps if necessary
    status_text.value = "Setup completed successfully!"
    setup_dialog.actions = [ft.TextButton("Close", on_click=lambda e: page.close(setup_dialog))]
    page.update()


def exit_program(page):
    # Close the dialog and exit the program
    page.dialog.open = False
    page.update()
    sys.exit()



def load_chat_files(chat_folder="saved_chats"):
    """
    Load chat files from a specified directory and return a sorted list of filenames.
    """
    if not os.path.exists(chat_folder):
        os.makedirs(chat_folder)

    # List and sort .txt files by modification date
    chat_files = [f for f in os.listdir(chat_folder) if f.endswith(".txt")]
    chat_files = sorted(chat_files, key=lambda f: os.path.getmtime(os.path.join(chat_folder, f)), reverse=True)
    return chat_files


def format_chat_content(file_path):
    """
    Reads a chat file and formats it for display in Markdown.
    """
    chat_content = ""
    with open(file_path, "r", encoding="utf-8") as file:
        current_role = None
        current_message = []

        for line in file:
            if line.startswith("user: "):
                if current_message:
                    chat_content += f"**{current_role.capitalize()}:**\n" + "\n".join(current_message) + "\n\n"
                    current_message = []
                current_role = "user"
                current_message.append(line[len("user: "):].strip())
            elif line.startswith("assistant: "):
                if current_message:
                    chat_content += f"**{current_role.capitalize()}:**\n" + "\n".join(current_message) + "\n\n"
                    current_message = []
                current_role = "assistant"
                current_message.append(line[len("assistant: "):].strip())
            else:
                current_message.append(line.rstrip())

        if current_message:
            chat_content += f"**{current_role.capitalize()}:**\n" + "\n".join(current_message) + "\n\n"

    return chat_content

def save_chat_entry(chat_name, unsaved_text):
    """
    saves chat to .txt file
    """
    file_path = os.path.join("saved_chats", chat_name + ".txt")
    for entry in unsaved_text:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{entry['role']}: {entry['content']}\n")


def load_chat_file(file_path):
    """
    Generator function to read chat lines from a file.
    Yields a dictionary with 'role' and 'content' for each line.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Chat file '{file_path}' not found.")

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("user: "):
                yield {"role": "user", "content": line[len("user: "):].strip()}
            elif line.startswith("assistant: "):
                yield {"role": "assistant", "content": line[len("assistant: "):].strip()}

def delete_models(e):
    for model_name in e:
        ollama.delete(model_name)

def delete_chat(e):
    for name in e:
        os.remove(os.path.join("saved_chats", name+".txt"))

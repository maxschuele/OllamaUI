import flet as ft
import ollama
import asyncio
import os
from utils import utils


class ChatbotUI:
    def __init__(self, page: ft.Page, chatbot ):
        self.page = page
        page.on_disconnect = self.page.pubsub.unsubscribe_all()
        self.chatbot = chatbot
        self.page.title = "Chatbot"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.chat_content = ""
        self.chat_display = ft.Markdown(self.chat_content, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                        expand=True)
        self.file_chips = ft.Row(spacing=10)

        # Create model list for dropdown model selection
        model_list = [model['name'] for model in ollama.list()['models']]
        model_list.append("Add new model")
        self.model_options = [ft.dropdown.Option(model) for model in model_list]



        # Initialize FilePicker
        self.file_picker = ft.FilePicker(on_result=self.upload_files)
        self.page.overlay.append(self.file_picker)  # Add FilePicker to the page overlay

        # Drop down for model selection
        self.model_dropdown = ft.Dropdown(
            label = "Select Model",
            value = chatbot.model,
            options=self.model_options,
            on_change=self.handle_model_change

        )

        # Define a PopupMenuButton for settings

        self.settings_menu = ft.PopupMenuButton(
            icon=ft.icons.SETTINGS,  # Gear icon for settings
            items=[
                ft.PopupMenuItem(text="Models", icon="smart_toy" , on_click = lambda e: self.manage_models() ),
                ft.PopupMenuItem(text="Chats", icon="chat" ,on_click = lambda e: self.manage_chats()),
                ft.PopupMenuItem(),  # Separator
                ft.PopupMenuItem(content= ft.Switch(label="Dark mode", value=self.page.theme_mode == ft.ThemeMode.DARK, on_change=self.toggle_dark_mode)),
            ],

        )


        # Scrollable column to hold the Markdown content
        Markdown_column = ft.Column(
            [self.chat_display],
            expand=True
        )
        Markdown_column.scroll = "auto"

        # Scrollable container for chat display
        chat_container = ft.Container(
            content=Markdown_column,
            expand=True,
            padding=ft.padding.all(10),
            border=ft.border.all(1, "lightgrey"),
            border_radius=10,
            bgcolor="white",
            alignment=ft.alignment.top_left

        )


        # Sidebar for saved chats
        self.chat_sidebar = ft.Column(
            width=200,  # Set a fixed width for the sidebar
            expand = True

        )
        self.chat_sidebar.scroll = "auto" #allow to scroll thorugh chats


        self.load_chat_files()
        # UI components
        self.upload_file_button = ft.IconButton(icon="attach_file", on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["pdf"], allow_multiple=True))
        self.user_input = ft.TextField(label="Type your message", expand=True, on_submit=lambda _: self.handle_send_message())
        self.send_button = ft.ElevatedButton("Send", on_click=lambda _: self.handle_send_message())
        self.new_chat_button = ft.ElevatedButton("New Chat", on_click=lambda e: self.chatbot.new_chat())

        # Layout structure
        self.page.add(
            ft.Row(
                [
                    ft.Column([self.new_chat_button, self.chat_sidebar]),  # Sidebar on the left
                    ft.Column(
                        [
                            ft.Row([ft.Text("Chatbot", style="headlineMedium", color="purple"), self.model_dropdown, self.settings_menu], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            chat_container,  # Scrollable chat container
                            self.file_chips,
                            ft.Row([self.upload_file_button, self.user_input, self.send_button], alignment=ft.MainAxisAlignment.END)
                        ],
                        expand=True,
                    )
                ],
                expand=True,
            )
        )
        self.page.update()


    def upload_files(self, e):
        # Check if a file was selected
        file_paths = []
        if self.file_picker.result and self.file_picker.result.files:
            for file in self.file_picker.result.files:
                # Get the path of the selected files
                file_paths.append(file.path)
            self.process_files(file_paths)







    def process_files(self, file_paths):
        # disable send
        self.send_button.disabled = True
        self.user_input.on_submit = None
        self.page.update()

        for file_path in file_paths:
            chip = self.create_file_chip(file_path)
            self.file_chips.controls.append(chip)

        self.page.update()
        for file_path in file_paths:
            # process file
            self.chatbot.upload_file(file_path)

            # update chip icon to "check"
            chip = next((chip for chip in self.file_chips.controls if chip.data == file_path), None)
            if chip:
                chip.leading = ft.Icon(ft.icons.CHECK, color="green")
                self.page.update()

        # Enable send again

        self.send_button.disabled = False
        self.user_input.on_submit = lambda _: self.handle_send_message()
        self.page.update()



    def create_file_chip(self, file_path):
        # Truncate file name if it's too long
        file_name = file_path.split('\\')[-1]  # Get file name from the path

        max_display_length = 15
        display_name = (file_name[:max_display_length] + '...') if len(file_name) > max_display_length else file_name

        # Create the Chip with initial 'downloading' icon
        chip = ft.Chip(
            label=ft.Text(display_name),
            leading=ft.Icon(ft.icons.DOWNLOADING),
            on_click=lambda e: self.remove_file_chip(chip, file_path),  # Remove on click
            data = file_path
        )
        return chip



    def remove_file_chip(self, chip, file_path):
        # Remove chip from UI and delete the corresponding file entry
        self.file_chips.controls.remove(chip)
        if file_path in self.chatbot.files:
            self.chatbot.processed_files = [entry for entry in self.chatbot.processed_files if entry["file"] != file_path]
            self.chatbot.files.remove(file_path)
            utils.store_submitted_files(self.chatbot.files, self.chatbot.name_current_chat)

        self.page.update()

    def manage_models(self):
        def change_box(e):
            # Enable the delete button if any checkbox is checked
            delete_button.disabled = not any(checkbox.value for checkbox in self.checkboxes)
            self.page.update()

        def delete_models(e):
            utils.delete_models(e)
            model_list = [model['name'] for model in ollama.list()['models']]

            # Update the dialog content with the new checkboxes
            self.checkboxes = [ft.Checkbox(label=model, value=False, on_change=change_box) for model in model_list]
            model_dialog_content.controls = self.checkboxes
            self.model_dialog.update()

            # Update the dropdown options
            model_list.append("Add new model")
            self.model_options = [ft.dropdown.Option(model) for model in model_list]
            self.model_dropdown.options = self.model_options
            self.page.update()

        model_list = [model['name'] for model in ollama.list()['models']]
        self.checkboxes = [ft.Checkbox(label=model, value=False, on_change= change_box) for model in model_list]

        model_dialog_content = ft.Column(
            self.checkboxes
        )
        model_dialog_content.scroll = "auto"

        delete_button = ft.TextButton("Delete", icon="delete", icon_color="red", disabled=True,
                                      on_click=lambda e: delete_models(
                                          [checkbox.label for checkbox in self.checkboxes if checkbox.value]))
        self.model_dialog = ft.AlertDialog(
            title = ft.Text("Manage Models"),
            content = model_dialog_content,
            modal=True,
            actions=[delete_button , ft.TextButton("Close", on_click=lambda e: self.page.close(self.model_dialog))]
        )
        self.page.dialog = self.model_dialog
        self.model_dialog.open = True
        self.page.update()




    def manage_chats(self):

        def change_box(e):
            # Enable the delete button if any checkbox is checked
            delete_button.disabled = not any(checkbox.value for checkbox in self.checkboxes)
            self.page.update()
        def delete_chats(e):
            utils.delete_chat(e)

            # update chat list in alterWindow
            chat_list = utils.load_chat_files()
            self.checkboxes = [ft.Checkbox(label=chat_name.replace(".txt", ""), value=False, on_change=change_box) for
                               chat_name in chat_list]
            chat_dialog_content.controls = self.checkboxes
            self.chat_dialog.update()

            # update chat list in main
            self.load_chat_files()


        chat_list = utils.load_chat_files()
        self.checkboxes = [ft.Checkbox(label=chat_name.replace(".txt", ""), value=False, on_change= change_box) for chat_name in chat_list]
        # make scrollable column
        chat_dialog_content = ft.Column(
            self.checkboxes
        )
        chat_dialog_content.auto_scroll = True

        delete_button = ft.TextButton("Delete", icon="delete", icon_color="red", disabled=True,
                                      on_click=lambda e: delete_chats(
                                          [checkbox.label for checkbox in self.checkboxes if checkbox.value]))

        self.chat_dialog = ft.AlertDialog(
            title=ft.Text("Manage Chats"),
            content = chat_dialog_content,
            modal=True,
            actions=[delete_button, ft.TextButton("Close", on_click=lambda e: self.page.close(self.chat_dialog))]
        )

        self.page.dialog = self.chat_dialog
        self.chat_dialog.open = True
        self.page.update()

    def toggle_dark_mode(self, e):
        # Toggle theme mode and adjust Markdown styling
        if e.control.value:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.chat_display.bgcolor = "black"
            self.chat_display.color = "white"
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.chat_display.bgcolor = "white"
            self.chat_display.color = "black"
        self.page.update()
    def manage_layout(self):

        def toggle_dark_mode(e):
            # Toggle theme mode and adjust Markdown styling
            if e.control.value:
                self.page.theme_mode = ft.ThemeMode.DARK
                self.chat_display.bgcolor = "black"
                self.chat_display.color = "white"
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
                self.chat_display.bgcolor = "white"
                self.chat_display.color = "black"
            self.page.update()


        # Create a dark mode toggle
        dark_mode_toggle = ft.Switch(
            label="Dark Mode",
            value=self.page.theme_mode == ft.ThemeMode.DARK,  # Starts in light mode
            on_change=toggle_dark_mode
        )



        self.layout_dialog = ft.AlertDialog(
            title = ft.Text("Manage Layout"),
            content = ft.Column([dark_mode_toggle])
        )

        self.page.dialog = self.layout_dialog
        self.layout_dialog.open = True
        self.page.update()


    def handle_model_change(self, e):
        # Update the selected model when user selects a new one
        if self.model_dropdown.value == "Add new model":
            self.add_new_model()
        else:
            self.chatbot.model = self.model_dropdown.value

    def add_new_model(self):
        # Define a placeholder for status messages
        self.status_text = ft.Text("")  # This will be updated with download status
        # Define the content of the dialog
        dialog_content = ft.Column(
            [
                ft.Text("Please enter the model name below and press Enter."),
                ft.TextField(label="Model Name", on_submit=self.download_model),
                ft.Text(
                    "Find available ",
                    spans=[ft.TextSpan("models", url="https://ollama.com/library",
                                       style=ft.TextStyle(decoration="underline", color="blue"))]
                ),
                self.status_text
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        # Create and open the dialog
        self.dialog = ft.AlertDialog(
            title=ft.Text("Add New Model"),
            content=dialog_content,
            modal=True,
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.page.close(self.dialog))  # Add a Close button
            ]
        )
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    def download_model(self, model_name):
        model_name = model_name.control.value.strip()

        if not model_name:
            self.status_text.value = "Model name cannot be empty."
            self.page.update()
            return

        try:
            # Update status text to show download initiation
            self.status_text.value = f"Downloading model '{model_name}'... This might take a while."
            self.page.update()
            ollama.pull(model_name)
            # Update status on success
            self.status_text.value = f"Model '{model_name}' downloaded successfully!"
        except:
            # Update status on failure
            self.status_text.value = f"Error: Could not download model '{model_name}'. Please check the name."

        model_list = [model['name'] for model in ollama.list()['models']]
        model_list.append("Add new model")
        self.model_options = [ft.dropdown.Option(model) for model in model_list]
        self.model_dropdown.options=self.model_options
        # Refresh dialog content with updated status
        self.page.update()


    def load_chat_files(self):
        # Get chat files
        chat_files = utils.load_chat_files()

        # Clear existing sidebar entries
        self.chat_sidebar.controls.clear()

        if not chat_files:
            self.chat_sidebar.controls.append(ft.Text("No saved chats found.", color="grey"))
        else:
            for file_name in chat_files:
                # Create a button for each chat file
                chat_button = ft.TextButton(
                    file_name.replace(".txt", ""),
                    on_click=lambda e, f=file_name: self.open_chat(f)  # Pass file_name to the function
                )
                self.chat_sidebar.controls.append(chat_button)

        self.page.update()

    def open_chat(self, file_name):
        # Clear the current chat content
        self.chat_content = ""  # Reset chat content string
        file_path = os.path.join("saved_chats", file_name)
        # Load the chat history from the file
        self.chat_content = utils.format_chat_content(file_path)
        # Update the Markdown display with the entire chat content
        self.update_prompt()
        self.chatbot.load_chat(file_name)
    def update_prompt(self):
        self.chat_display.value = self.chat_content
        self.page.update()
    async def stream_response(self, prompt):
        # Display user message in chat
        self.chat_content += f"**User:** {prompt}\n\n"
        self.update_prompt()

        # Stream assistant's response as it comes in
        self.chat_content+=f"**Assistant:** "
        async for part in self.chatbot.send_message(prompt):
            self.chat_content += f"{part}"  # Append each streamed part
            self.update_prompt()

        # Add a line break after the full response is displayed
        self.chat_content += "\n\n"
        self.update_prompt()

    def handle_send_message(self):
        # Get user input, start the streaming coroutine
        user_message = self.user_input.value
        if user_message:
            self.user_input.value = ""  # Clear the input field
            asyncio.run(self.stream_response(user_message))  # Start the async streaming


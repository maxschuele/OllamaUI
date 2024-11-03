
# OllamaUI

**OllamaUI** is an interactive user interface (UI) built with [Flet](https://flet.dev/docs/) for convenient interactions with LL-Models hosted through [Ollama](https://ollama.com/). The interface provides tools for model management, chat-based interaction, and easy access to models from the Ollama model library.

## Features

- **Model Management**: Easily add and remove models available in the [Ollama Model Library](https://ollama.com/library).
- **Chat Interface**: Provides an interactive chat UI for engaging with selected models.
- **Model Installation Helper**: Automatic installation and setup of Ollama models if they aren’t pre-installed.

## Prerequisites

### 1. Install Ollama
The application requires [Ollama](https://ollama.com/download) to be installed. Ollama provides the backend support for hosting and running LL models on your local machine.

### 2. Conda Environment Setup
To ensure dependencies are installed correctly, use the provided `OllamaUI.yml` file to set up a Conda environment.

1. Clone the repository and navigate to the project folder:

   ```bash
   git clone https://github.com/xamweil/OllamaUI.git
   cd OllamaUI
   ```

2. Create the Conda environment using the `OllamaUI.yml` file:

   ```bash
   conda env create -f OllamaUI.yml
   ```

3. Activate the environment:

   ```bash
   conda activate OllamaUI
   ```

## Getting Started

1. **Run the Application**: Once your environment is activated, you can start the application with:

   ```bash
   python main.py
   ```

2. **Selecting Models**: In the UI, you’ll find a model dropdown where you can select a model to use from the Ollama library. If a model isn’t installed locally, you can download it directly through the interface.

3. **Interactive Chat**: Use the chat interface to interact with your selected model. The interface also supports dark mode and an option to manage installed models and saved chats.

## Dependencies

- **Flet**: The project’s UI is built with [Flet](https://flet.dev/docs/).
- **Ollama**: [Ollama](https://ollama.com/) hosts and runs the LL-Models. It’s essential to have Ollama installed and accessible on your local machine.
- **Ollama-Python**: This package is used to interact programmatically with Ollama models. More details can be found in the [Ollama-Python GitHub](https://github.com/ollama/ollama-python).

## Available Models

All models available in the [Ollama Model Library](https://ollama.com/library) are supported by OllamaUI. You can easily add or remove models from the library through the application.

## Notes

- Ensure that `Ollama` is installed and running on your system.
- If you encounter issues with missing models or dependencies, please refer to the links above for model downloads and installation help.

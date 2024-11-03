from bot.ollama_integration import OllamaCall
from ui.chatbot_ui import ChatbotUI
import flet as ft
import ollama
from utils import utils
import asyncio
async def main(page: ft.Page):
    await utils.setup(page)
    chatbot = OllamaCall("llama3.2:latest")
    UI = ChatbotUI(page, chatbot=chatbot)
    chatbot.UI = UI

if __name__ == "__main__":
    ft.app(target=lambda p: asyncio.run(main(p)))
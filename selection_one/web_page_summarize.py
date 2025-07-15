from ast import main
from email import message
from urllib import response
import bs4
import bs4.exceptions
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import openai

load_dotenv()

# const variables
MODEL_NAME = "gpt-4o-mini"


class WebPageScrap:
    title: str = ""
    exlude_list = ["script", "style", "header", "footer", "nav", "img"]
    page_content: str = ""

    def __init__(self, url: str):
        self.url = url

    def fetch_page(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            self.title = soup.title.string if soup.title else "No Title"
            for tag in self.exlude_list:
                for element in soup.body(self.exlude_list):
                    element.decompose()
            self.page_content = soup.body.get_text(separator='\n', strip=True)
        except requests.RequestException or bs4.exceptions as e:
            print(f"Error fetching the page: {e}")
            return None

    @property
    def getTitle(self) -> str:
        return self.title

    @property
    def getContent(self) -> str:
        return self.page_content


class Message:
    system_prompt: str = "You are an assistant that analyzes the contents of a website \
        and provides a short summary, ignoring text that might be navigation related. \
        Respond in markdown."
    user_prompt = ""

    def __init__(self, website: WebPageScrap):
        self.website = website

    def user_prompt(self) -> str:
        self.user_prompt = f"Please summarize the content of the website: {self.website.getTitle}\n"
        self.user_prompt += "\nThe contents of this website is as follows; please provide a short summary of this website in markdown.\
                            If it includes   news or announcements, then summarize these too.\n\n"
        self.user_prompt += self.website.getContent
        return self.user_prompt

    def send_message(self,):
        try:
            message = [{
                "role": "system",
                "content": self.system_prompt
            },
                {
                "role": "user",
                "content": self.user_prompt()
            }]
            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=message,
            )
            return response.choices[0].message.content if response.choices else "No response from model"
        except openai.APIConnectionError as e:
            print(f"Error communicating with OpenAI API: {e}")


if __name__ == "__main__":
    open_api_key = os.getenv("OPENAI_API_KEY")
    if not open_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    website = WebPageScrap("https://edwarddonner.com/")
    website.fetch_page()
    message = Message(website)
    summary = message.send_message()
    print(summary)

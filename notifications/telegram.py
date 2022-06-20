import requests
import os

# To start without DB.
chats = [
   {
      "chat_id": -724867662,
      "all": True
   },
   {
      "chat_id": -687323795,
      "all": False,
      "municipalities": ["GM0518", "GM0599"]
   }
]

def send_telegram_msg(text, chat_id):
   token = os.getenv("TELEGRAM_TOKEN")
   print(chat_id)
   print(text)
   url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + str(chat_id) + "&text=" + text 
   results = requests.get(url_req)
   print(results.json())

def send_msg(text, municipality):
   for chat in chats:
      if chat["all"] or municipality in chat["municipalities"]:
         send_telegram_msg(text, chat["chat_id"])

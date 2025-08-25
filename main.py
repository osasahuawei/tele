import requests
import sys
import json
import time
import threading
from colorama import Fore, init
import random
import itertools
import telebot
import re
import io

init(autoreset=True)

bot = telebot.TeleBot("YOUR_TOKEN_HERE")  # Replace with your Telegram bot token

stop_event = threading.Event()
script_thread = None

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class TelegramStream(io.StringIO):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
        self.buffer = ""
        self.last_message_id = None

    def write(self, s):
        cleaned_s = ansi_escape.sub('', s)  # Strip ANSI colors
        self.buffer += cleaned_s
        if self.buffer.endswith('\n'):
            text = self.buffer[:-1]
            self._send_new(text)
            self.buffer = ""
        elif self.buffer.endswith('\r'):
            text = self.buffer[:-1]
            self._send_overwrite(text)
            self.buffer = ""
        # If neither, it's partial write, keep in buffer

    def _send_new(self, text):
        if text.strip():  # Avoid sending empty
            message = self.bot.send_message(self.chat_id, text)
            # Do not set last_message_id here, as new lines start fresh

    def _send_overwrite(self, text):
        if text.strip():  # Avoid sending empty
            if self.last_message_id:
                try:
                    self.bot.edit_message_text(chat_id=self.chat_id, message_id=self.last_message_id, text=text)
                except telebot.apihelper.ApiTelegramException:
                    # If edit fails (e.g., text same), send new
                    message = self.bot.send_message(self.chat_id, text)
                    self.last_message_id = message.message_id
            else:
                message = self.bot.send_message(self.chat_id, text)
                self.last_message_id = message.message_id

    def flush(self):
        if self.buffer:
            self._send_new(self.buffer)
            self.buffer = ""

def run_script(number_oner, password_oner, number_men1, password_men1, number_men2, password_men2, chat_id):
    original_stdout = sys.stdout
    sys.stdout = TelegramStream(bot, chat_id)
    try:
        print("-*-*-*- Member 1 in the FAMILY with 1300 Flex -*-*-*-")

        quota_cycle = itertools.cycle(["10", "40"])

        def get_access_token_Owner(number_oner, password_oner):
            url1 = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
            payload1 = {
                'username': number_oner,
                'password': password_oner,
                'grant_type': "password",
                'client_secret': "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3",
                'client_id': "my-vodafone-app"
            }
            headers1 = {
                'User-Agent': "okhttp/4.9.3",
                'Accept': "application/json, text/plain, */*",
                'Accept-Encoding': "gzip",
                'x-agent-operatingsystem': "V12.5.13.0.RJQMIXM",
                'clientId': "xxx",
                'x-agent-device': "lime",
                'x-agent-version': "2024.10.1",
                'x-agent-build': "562"
            }

            r1 = requests.post(url1, data=payload1, headers=headers1).json()

            if 'access_token' not in r1:
                print(Fore.RED + "❌ Login failed. Check the number or password.")

            access_token = "Bearer " + r1['access_token']
            print(Fore.GREEN + "✅ Login successful For Owner!")
            return access_token
            
        def get_access_token_Second_number(number_men2, password_men2):
            url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
            payload = {
                'username': number_men2,
                'password': password_men2,
                'grant_type': "password",
                'client_secret': "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3",
                'client_id': "my-vodafone-app"
            }
            headers = {
                'User-Agent': "okhttp/4.9.3",
                'Accept': "application/json, text/plain, */*",
                'Accept-Encoding': "gzip",
                'x-agent-operatingsystem': "V12.5.13.0.RJQMIXM",
                'clientId': "xxx",
                'x-agent-device': "lime",
                'x-agent-version': "2024.10.1",
                'x-agent-build': "562"
            }
            r1 = requests.post(url, data=payload, headers=headers).json()
            if 'access_token' not in r1:
                print(Fore.RED + "❌ Login failed for the second member.")
                return

            acc = "Bearer " + r1['access_token']
            print(Fore.GREEN + "✅ Second member login successful!")
            return acc

            
        def Send_Invite(number_oner, number_men2 , password_oner):
            # Sending invitation to the second member
            access_token = get_access_token_Owner(number_oner, password_oner)
            quota_value = next(quota_cycle)
            print(quota_value)
            print(Fore.CYAN + "📨 Sending invitation to the second member...")
            url = "https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
            payload = {
              "name": "FlexFamily",
              "type": "SendInvitation",
              "category": [
                {"value": "523", "listHierarchyId": "PackageID"},
                {"value": "47", "listHierarchyId": "TemplateID"},
                {"value": "523", "listHierarchyId": "TierID"},
                {"value": "percentage", "listHierarchyId": "familybehavior"}
              ],
              "parts": {
                "member": [
                  {"id": [{"value": number_oner, "schemeName": "MSISDN"}], "type": "Owner"},
                  {"id": [{"value": number_men2, "schemeName": "MSISDN"}], "type": "Member"}
                ],
                "characteristicsValue": {
                  "characteristicsValue": [
                    {"characteristicName": "quotaDist1", "value": quota_value, "type": "percentage"}
                  ]
                }
              }
            }
            headers = {
              'User-Agent': "Mozilla/5.0 (Linux; Android 11; M2010J19SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36",
              'Accept': "application/json",
              'Content-Type': "application/json",
              'sec-ch-ua': "\"Chromium\";v=\"94\", \"Google Chrome\";v=\"94\", \";Not A Brand\";v=\"99\"",
              'msisdn': number_oner,
              'Accept-Language': "AR",
              'sec-ch-ua-mobile': "?1",
              'Authorization': access_token,
              'x-dtpc': "5$160966758_702h19vRCUAEMOMIIASTHWKLEMFNIHJNUTANVVK-0e0",
              'clientId': "WebsiteConsumer",
              'sec-ch-ua-platform': "\"Android\"",
              'Origin': "https://web.vodafone.com.eg",
              'Sec-Fetch-Site': "same-origin",
              'Sec-Fetch-Mode': "cors",
              'Sec-Fetch-Dest': "empty",
              'Referer': "https://web.vodafone.com.eg/spa/familySharing",
            }
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            print(Fore.MAGENTA + "📤 Invitation send response:")
            print(response.text)

        def Accept_Invite(number_oner, number_men2, password_men2):
            acc = get_access_token_Second_number(number_men2, password_men2)
            print(Fore.CYAN + "📩 Accepting the invitation...")
            url = "https://mobile.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
            payload = {
              "category": [{"listHierarchyId": "TemplateID", "value": "47"}],
              "name": "FlexFamily",
              "parts": {
                "member": [
                  {"id": [{"schemeName": "MSISDN", "value": number_oner}], "type": "Owner"},
                  {"id": [{"schemeName": "MSISDN", "value": number_men2}], "type": "Member"}
                ]
              },
              "type": "AcceptInvitation"
            }
            headers = {
              'User-Agent': "okhttp/4.11.0",
              'Connection': "Keep-Alive",
              'Accept': "application/json",
              'Accept-Encoding': "gzip",
              'Content-Type': "application/json",
              'api_id': "APP",
              'x-dynatrace': "MT_3_24_3486379639_64-0_a556db1b-4506-43f3-854a-1d2527767923_0_187_277",
              'Authorization': acc,
              'api-version': "v2",
              'x-agent-operatingsystem': "13",
              'clientId': "AnaVodafoneAndroid",
              'x-agent-device': "Xiaomi 21061119AG",
              'x-agent-version': "2024.12.1",
              'x-agent-build': "946",
              'msisdn': number_men2,
              'Accept-Language': "ar",
              'Content-Type': "application/json; charset=UTF-8"
            }
            response = requests.patch(url, data=json.dumps(payload), headers=headers)
            print(Fore.MAGENTA + "📥 Invitation accept response:")
            print(response.text)
            
        def Change_Quota(number_oner, number_men1, password_oner):
            access_token = get_access_token_Owner(number_oner, password_oner)
            # Changing quota distribution
            print(Fore.CYAN + "🔄 Changing quota distribution...")
            url = "https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
            payload = {
              "name": "FlexFamily",
              "type": "QuotaRedistribution",
              "category": [
                {"value": "523", "listHierarchyId": "PackageID"},
                {"value": "47", "listHierarchyId": "TemplateID"},
                {"value": "523", "listHierarchyId": "TierID"},
                {"value": "percentage", "listHierarchyId": "familybehavior"}
              ],
              "parts": {
                "member": [
                  {"id": [{"value": number_oner, "schemeName": "MSISDN"}], "type": "Owner"},
                  {"id": [{"value": number_men1, "schemeName": "MSISDN"}], "type": "Member"}
                ],
                "characteristicsValue": {
                  "characteristicsValue": [
                    {"characteristicName": "quotaDist1", "value": "40", "type": "percentage"}
                  ]
                }
              }
            }
            headers = {
              'User-Agent': "Mozilla/5.0 (Linux; Android 11; M2010J19SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36",
              'Accept': "application/json",
              'Content-Type': "application/json",
              'sec-ch-ua': "\"Chromium\";v=\"94\", \"Google Chrome\";v=\"94\", \";Not A Brand\";v=\"99\"",
              'msisdn': number_oner,
              'Accept-Language': "AR",
              'sec-ch-ua-mobile': "?1",
              'Authorization': access_token,
              'x-dtpc': "5$160966758_702h19vRCUAEMOMIIASTHWKLEMFNIHJNUTANVVK-0e0",
              'clientId': "WebsiteConsumer",
              'sec-ch-ua-platform': "\"Android\"",
              'Origin': "https://web.vodafone.com.eg",
              'Sec-Fetch-Site': "same-origin",
              'Sec-Fetch-Mode': "cors",
              'Sec-Fetch-Dest': "empty",
              'Referer': "https://web.vodafone.com.eg/spa/familySharing",
            }
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            print(Fore.MAGENTA + "📤 Quota redistribution response:")
            print(response.text)
            
        def Remove_Number(number_oner, number_men2, password_oner):
            access_token = get_access_token_Owner(number_oner, password_oner)
            print(Fore.CYAN + "🗑️ Removing the second member...")
            url = "https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
            payload = {
              "name": "FlexFamily",
              "type": "FamilyRemoveMember",
              "category": [{"value": "47", "listHierarchyId": "TemplateID"}],
              "parts": {
                "member": [
                  {"id": [{"value": number_oner, "schemeName": "MSISDN"}], "type": "Owner"},
                  {"id": [{"value": number_men2, "schemeName": "MSISDN"}], "type": "Member"}
                ],
                "characteristicsValue": {
                  "characteristicsValue": [
                    {"characteristicName": "Disconnect", "value": "0"},
                    {"characteristicName": "LastMemberDeletion", "value": "1"}
                  ]
                }
              }
            }
            headers = {
              'User-Agent': "Mozilla/5.0 (Linux; Android 11; M2010J19SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36",
              'Accept': "application/json",
              'Content-Type': "application/json",
              'sec-ch-ua': "\"Chromium\";v=\"94\", \"Google Chrome\";v=\"94\", \";Not A Brand\";v=\"99\"",
              'msisdn': number_oner,
              'Accept-Language': "AR",
              'sec-ch-ua-mobile': "?1",
              'Authorization': access_token,
              'x-dtpc': "8$160966758_702h28vFSPMIAKHHWGIIKVDPLHCDFHKOJUBFNJP-0e0",
              'clientId': "WebsiteConsumer",
              'sec-ch-ua-platform': "\"Android\"",
              'Origin': "https://web.vodafone.com.eg",
              'Sec-Fetch-Site': "same-origin",
              'Sec-Fetch-Mode': "cors",
              'Sec-Fetch-Dest': "empty",
              'Referer': "https://web.vodafone.com.eg/spa/familySharing",
            }
            response = requests.patch(url, data=json.dumps(payload), headers=headers)
            print(Fore.MAGENTA + "🗑️ Member removal response:")
            print(response.text)

        def Reset_Qota(number_oner, number_men1, password_oner):
            access_token = get_access_token_Owner(number_oner, password_oner)
            print(Fore.CYAN + "🔄 Redistributing quota to the original value...")
            url = "https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
            payload = {
              "name": "FlexFamily",
              "type": "QuotaRedistribution",
              "category": [
                {"value": "523", "listHierarchyId": "PackageID"},
                {"value": "47", "listHierarchyId": "TemplateID"},
                {"value": "523", "listHierarchyId": "TierID"},
                {"value": "percentage", "listHierarchyId": "familybehavior"}
              ],
              "parts": {
                "member": [
                  {"id": [{"value": number_oner, "schemeName": "MSISDN"}], "type": "Owner"},
                  {"id": [{"value": number_men1, "schemeName": "MSISDN"}], "type": "Member"}
                ],
                "characteristicsValue": {
                  "characteristicsValue": [
                    {"characteristicName": "quotaDist1", "value": "10", "type": "percentage"}
                  ]
                }
              }
            }
            headers = {
              'User-Agent': "Mozilla/5.0 (Linux; Android 11; M2010J19SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36",
              'Accept': "application/json",
              'Content-Type': "application/json",
              'sec-ch-ua': "\"Chromium\";v=\"94\", \"Google Chrome\";v=\"94\", \";Not A Brand\";v=\"99\"",
              'msisdn': number_oner,
              'Accept-Language': "AR",
              'sec-ch-ua-mobile': "?1",
              'Authorization': access_token,
              'x-dtpc': "5$160966758_702h19vRCUAEMOMIIASTHWKLEMFNIHJNUTANVVK-0e0",
              'clientId': "WebsiteConsumer",
              'sec-ch-ua-platform': "\"Android\"",
              'Origin': "https://web.vodafone.com.eg",
              'Sec-Fetch-Site': "same-origin",
              'Sec-Fetch-Mode': "cors",
              'Sec-Fetch-Dest': "empty",
              'Referer': "https://web.vodafone.com.eg/spa/familySharing",
            }
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            print(Fore.MAGENTA + "📤 Quota redistribution response:")
            print(response.text)
            

        i = 0
        while i < 10 and not stop_event.is_set():
            print(Fore.YELLOW + f"\n🌀 Starting cycle number {i+1}")
            Send_Invite(number_oner, number_men2 , password_oner)
            stop_event.wait(10)
            t1 = threading.Thread(target=Accept_Invite, args=(number_oner, number_men2, password_men2))
            t2 = threading.Thread(target=Change_Quota, args=(number_oner, number_men1, password_oner))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            stop_event.wait(5)
            Remove_Number(number_oner, number_men2, password_oner)
            seconds_left1 = 301
            while seconds_left1 > 0 and not stop_event.is_set():
                print(Fore.YELLOW + f"Time remaining: {seconds_left1} seconds", end='\r')
                stop_event.wait(1)
                seconds_left1 -= 1
            Reset_Qota(number_oner, number_men1, password_oner)
            seconds_left2 = 301
            while seconds_left2 > 0 and not stop_event.is_set():
                print(Fore.YELLOW + f"Time remaining: {seconds_left2} seconds", end='\r')
                stop_event.wait(1)
                seconds_left2 -= 1
            i += 1

        print(Fore.GREEN + "\n🎉 All cycles completed successfully")
    finally:
        sys.stdout = original_stdout

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Please send the data in one message separated by ':': owner_number:owner_password:member1_number:member1_password:member2_number:member2_password")

@bot.message_handler(func=lambda message: True)
def handle_data(message):
    global script_thread
    parts = message.text.split(':')
    if len(parts) == 6:
        number_oner, password_oner, number_men1, password_men1, number_men2, password_men2 = [p.strip() for p in parts]
        stop_event.clear()
        script_thread = threading.Thread(target=run_script, args=(number_oner, password_oner, number_men1, password_men1, number_men2, password_men2, message.chat.id))
        script_thread.start()
        bot.send_message(message.chat.id, "Script started with provided data.")
    else:
        bot.send_message(message.chat.id, "Invalid data format. Please send exactly 6 parts separated by ':'.")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    stop_event.set()
    bot.send_message(message.chat.id, "Stopping the script...")

bot.polling()

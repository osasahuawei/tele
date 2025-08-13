import requests
import sys
import json
import time
import threading
from colorama import Fore, init
import telebot
from telebot import types
from threading import Event

# Initialize colorama
init(autoreset=True)

# Telegram Bot Token
TOKEN = '8330939461:AAEUaMYi3UI_sx1pkrSqXT--Hgfzo21zHUg'
bot = telebot.TeleBot(TOKEN)

# Global variables to store user data and control the script
user_data = {}
script_active = False
stop_event = Event()

# Handler for /start command
@bot.message_handler(commands=['start'])
def start(message):
    global user_data, script_active
    
    if script_active:
        bot.send_message(message.chat.id, "⚠️ Script is already running. Use /stop to stop it first.")
        return
    
    user_data = {
        'chat_id': message.chat.id,
        'step': 0,
        'number_oner': None,
        'password_oner': None,
        'number_men1': None,
        'password_men1': None,
        'number_men2': None,
        'password_men2': None
    }
    
    msg = bot.send_message(message.chat.id, "🔹 Please enter all required data in one message separated by spaces in this order:\n\n"
                                          "1. Owner Number\n"
                                          "2. Owner Password\n"
                                          "3. Member 1 Number\n"
                                          "4. Member 1 Password\n"
                                          "5. Member 2 Number\n"
                                          "6. Member 2 Password\n\n"
                                          "Example:\n"
                                          "01012345678 pass123 01011111111 pass111 01022222222 pass222")
    
    bot.register_next_step_handler(msg, process_input)

def process_input(message):
    global user_data
    
    try:
        parts = message.text.split()
        if len(parts) != 6:
            raise ValueError("Incorrect number of parameters")
            
        user_data['number_oner'] = parts[0]
        user_data['password_oner'] = parts[1]
        user_data['number_men1'] = parts[2]
        user_data['password_men1'] = parts[3]
        user_data['number_men2'] = parts[4]
        user_data['password_men2'] = parts[5]
        
        # Confirm the data
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Yes', 'No')
        
        confirmation_msg = f"📋 Please confirm the entered data:\n\n" \
                         f"👑 Owner Number: {user_data['number_oner']}\n" \
                         f"🔑 Owner Password: {user_data['password_oner']}\n" \
                         f"👤 Member 1 Number: {user_data['number_men1']}\n" \
                         f"🔑 Member 1 Password: {user_data['password_men1']}\n" \
                         f"👤 Member 2 Number: {user_data['number_men2']}\n" \
                         f"🔑 Member 2 Password: {user_data['password_men2']}\n\n" \
                         f"Is this correct?"
                         
        msg = bot.send_message(message.chat.id, confirmation_msg, reply_markup=markup)
        bot.register_next_step_handler(msg, confirm_data)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}\n\nPlease send the data again in the correct format.")
        start(message)

def confirm_data(message):
    global user_data, script_active
    
    if message.text.lower() == 'yes':
        bot.send_message(message.chat.id, "✅ Data confirmed. Starting the script...", reply_markup=types.ReplyKeyboardRemove())
        
        # Start the script in a separate thread
        script_active = True
        stop_event.clear()
        threading.Thread(target=run_script, args=(user_data,)).start()
    else:
        bot.send_message(message.chat.id, "🔄 Please enter the data again.", reply_markup=types.ReplyKeyboardRemove())
        start(message)

# Handler for /stop command
@bot.message_handler(commands=['stop'])
def stop_script(message):
    global script_active
    
    if script_active:
        stop_event.set()
        script_active = False
        bot.send_message(message.chat.id, "🛑 Script stopping... Please wait for current cycle to complete.")
    else:
        bot.send_message(message.chat.id, "ℹ️ No script is currently running.")

def send_telegram_message(chat_id, text):
    try:
        bot.send_message(chat_id, text)
    except Exception as e:
        print(f"Failed to send Telegram message: {str(e)}")

def run_script(user_data):
    global script_active
    
    chat_id = user_data['chat_id']
    number_oner = user_data['number_oner']
    password_oner = user_data['password_oner']
    number_men1 = user_data['number_men1']
    password_men1 = user_data['password_men1']
    number_men2 = user_data['number_men2']
    password_men2 = user_data['password_men2']
    
    send_telegram_message(chat_id, "-*-*-*- Member 1 in the FAMILY with 1300 Flex -*-*-*-")
    
    for i in range(1, 11):
        if stop_event.is_set():
            send_telegram_message(chat_id, "🛑 Script stopped by user.")
            script_active = False
            return
            
        send_telegram_message(chat_id, f"\n🌀 Starting cycle number {i}")
        
        # Owner login
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {
            'username': number_oner,
            'password': password_oner,
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

        try:
            r1 = requests.post(url, data=payload, headers=headers).json()
            
            if 'access_token' not in r1:
                send_telegram_message(chat_id, "❌ Login failed. Check the number or password.")
                script_active = False
                return

            access_token = "Bearer " + r1['access_token']
            send_telegram_message(chat_id, "✅ Login successful!")
            time.sleep(10)
        except Exception as e:
            send_telegram_message(chat_id, f"❌ Error during login: {str(e)}")
            script_active = False
            return

        # Sending invitation to the second member
        send_telegram_message(chat_id, "📨 Sending invitation to the second member...")
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
        
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            send_telegram_message(chat_id, f"📤 Invitation send response:\n{response.text}")
            time.sleep(10)
        except Exception as e:
            send_telegram_message(chat_id, f"❌ Error sending invitation: {str(e)}")
            continue

        # Accepting the invitation
        def accept_invitation():
            try:
                send_telegram_message(chat_id, "📩 Accepting the invitation...")
                
                # Login for the second member
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
                    send_telegram_message(chat_id, "❌ Login failed for the second member.")
                    return

                acc = "Bearer " + r1['access_token']
                send_telegram_message(chat_id, "✅ Second member login successful!")

                # Accepting the invitation
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
                send_telegram_message(chat_id, f"📥 Invitation accept response:\n{response.text}")
            except Exception as e:
                send_telegram_message(chat_id, f"❌ Error in accept_invitation: {str(e)}")

        def change_quota(access_token):
            try:
                send_telegram_message(chat_id, "🔄 Changing quota distribution...")
                
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
                send_telegram_message(chat_id, f"📤 Quota redistribution response:\n{response.text}")
            except Exception as e:
                send_telegram_message(chat_id, f"❌ Error in change_quota: {str(e)}")
        
        # Start threads for accepting invitation and changing quota
        threading.Thread(target=accept_invitation).start()
        time.sleep(0.5)
        threading.Thread(target=change_quota, args=(access_token,)).start()
        
        # Wait for threads to complete
        time.sleep(10)
        
        if stop_event.is_set():
            send_telegram_message(chat_id, "🛑 Script stopped by user.")
            script_active = False
            return
            
        # Removing the second member
        send_telegram_message(chat_id, "🗑️ Removing the second member...")
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
        
        try:
            response = requests.patch(url, data=json.dumps(payload), headers=headers)
            send_telegram_message(chat_id, f"🗑️ Member removal response:\n{response.text}")
        except Exception as e:
            send_telegram_message(chat_id, f"❌ Error removing member: {str(e)}")
            continue

        # Changing the first member's quota from 5200 to 1300
        send_telegram_message(chat_id, "🔄 Redistributing quota to the original value...")
        send_telegram_message(chat_id, "⏳ Waiting for five minutes")
        
        # Wait for 5 minutes with periodic checks for stop command
        for _ in range(300):  # 300 seconds = 5 minutes
            if stop_event.is_set():
                send_telegram_message(chat_id, "🛑 Script stopped by user.")
                script_active = False
                return
            time.sleep(1)
        
        if stop_event.is_set():
            send_telegram_message(chat_id, "🛑 Script stopped by user.")
            script_active = False
            return
            
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
        
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            send_telegram_message(chat_id, f"📤 Quota redistribution response:\n{response.text}")
        except Exception as e:
            send_telegram_message(chat_id, f"❌ Error in final quota redistribution: {str(e)}")
            continue

        send_telegram_message(chat_id, f"✅ Cycle number {i} completed successfully!")
        
        if i < 10 and not stop_event.is_set():
            send_telegram_message(chat_id, "⏳ Waiting five more minutes to avoid quota restriction")
            
            # Wait for 5 minutes with periodic checks for stop command
            for _ in range(300):  # 300 seconds = 5 minutes
                if stop_event.is_set():
                    send_telegram_message(chat_id, "🛑 Script stopped by user.")
                    script_active = False
                    return
                time.sleep(1)
    
    send_telegram_message(chat_id, "🎉 All cycles completed successfully")
    script_active = False

# Start the bot
print("Bot is running...")
bot.polling()

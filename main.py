import requests
import sys, json, time
import threading
from colorama import Fore, init
import telebot
from requests.exceptions import ReadTimeout

init(autoreset=True)

# Replace with your Telegram Bot Token
TOKEN = '7777259761:AAGCDUJwQQAHSJRW1tBh1yJ43bL6OFORESI'
bot = telebot.TeleBot(TOKEN)

user_data = {}  # To store user inputs per chat_id
stop_flags = {}  # To track stop requests per chat_id

def send_message(chat_id, text):
    """Helper function to send message to Telegram and also print to console."""
    try:
        bot.send_message(chat_id, text)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")
    print(text)

def main_cycle(cycle_number, chat_id, number_oner, password_oner, number_men1, password_men1, number_men2, password_men2):
    if chat_id in stop_flags and stop_flags[chat_id]:
        send_message(chat_id, f"🛑 Cycle {cycle_number} stopped by user.")
        return False

    send_message(chat_id, f"\n🌀 Starting cycle number {cycle_number}")
    
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
        r1 = requests.post(url, data=payload, headers=headers, timeout=10).json()
    except requests.RequestException as e:
        send_message(chat_id, f"❌ Login failed due to network error: {e}")
        return False

    if 'access_token' not in r1:
        send_message(chat_id, "❌ Login failed. Check the number or password.")
        return False

    access_token = "Bearer " + r1['access_token']
    send_message(chat_id, "✅ Login successful!")
    time.sleep(10)

    # Sending invitation to the second member
    send_message(chat_id, "📨 Sending invitation to the second member...")
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
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        send_message(chat_id, "📤 Invitation send response:")
        send_message(chat_id, response.text)
    except requests.RequestException as e:
        send_message(chat_id, f"❌ Failed to send invitation: {e}")
        return False
    time.sleep(10)

    # Accepting the invitation
    send_message(chat_id, "📩 Accepting the invitation...")
    def accept_invitation():
        if chat_id in stop_flags and stop_flags[chat_id]:
            return
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
        try:
            r1 = requests.post(url, data=payload, headers=headers, timeout=10).json()
        except requests.RequestException as e:
            send_message(chat_id, f"❌ Login failed for the second member: {e}")
            return

        if 'access_token' not in r1:
            send_message(chat_id, "❌ Login failed for the second member.")
            return

        acc = "Bearer " + r1['access_token']
        send_message(chat_id, "✅ Second member login successful!")

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
        try:
            response = requests.patch(url, data=json.dumps(payload), headers=headers, timeout=10)
            send_message(chat_id, "📥 Invitation accept response:")
            send_message(chat_id, response.text)
        except requests.RequestException as e:
            send_message(chat_id, f"❌ Failed to accept invitation: {e}")
            return
    
    # Wait 0.5 seconds before changing the quota
    time.sleep(0.5)
    def change_quota(access_token):
        if chat_id in stop_flags and stop_flags[chat_id]:
            return
        # Changing quota distribution
        send_message(chat_id, "🔄 Changing quota distribution...")
        
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
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
            send_message(chat_id, "📤 Quota redistribution response:")
            send_message(chat_id, response.text)
        except requests.RequestException as e:
            send_message(chat_id, f"❌ Failed to redistribute quota: {e}")
            return
    
    threading.Thread(target=accept_invitation).start()
    threading.Thread(target=change_quota, args=(access_token,)).start()
    
    # Rest of the steps as they are...
    time.sleep(10)
    
    # Check stop flag
    if chat_id in stop_flags and stop_flags[chat_id]:
        send_message(chat_id, f"🛑 Cycle {cycle_number} stopped by user.")
        return False

    # Removing the second member
    send_message(chat_id, "🗑️ Removing the second member...")
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
        response = requests.patch(url, data=json.dumps(payload), headers=headers, timeout=10)
        send_message(chat_id, "🗑️ Member removal response:")
        send_message(chat_id, response.text)
    except requests.RequestException as e:
        send_message(chat_id, f"❌ Failed to remove member: {e}")
        return False

    # Check stop flag
    if chat_id in stop_flags and stop_flags[chat_id]:
        send_message(chat_id, f"🛑 Cycle {cycle_number} stopped by user.")
        return False

    # Changing the first member's quota from 5200 to 1300
    send_message(chat_id, "🔄 Redistributing quota to the original value...")
    send_message(chat_id, "Waiting for five minutes")
    time.sleep(300)
    
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
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        send_message(chat_id, "📤 Quota redistribution response:")
        send_message(chat_id, response.text)
    except requests.RequestException as e:
        send_message(chat_id, f"❌ Failed to redistribute quota: {e}")
        return False
    
    send_message(chat_id, f"✅ Cycle number {cycle_number} completed successfully!")
    return True

def run_script(chat_id):
    if chat_id not in user_data:
        send_message(chat_id, "⚠️ No user data found. Please start with /start.")
        return

    data = user_data[chat_id]
    number_oner = data['number_oner']
    password_oner = data['password_oner']
    number_men1 = data['number_men1']
    password_men1 = data['password_men1']
    number_men2 = data['number_men2']
    password_men2 = data['password_men2']
    
    for i in range(1, 41):
        if chat_id in stop_flags and stop_flags[chat_id]:
            send_message(chat_id, "🛑 Script stopped by user.")
            return
        if not main_cycle(i, chat_id, number_oner, password_oner, number_men1, password_men1, number_men2, password_men2):
            return
        if i < 40:
            send_message(chat_id, f"\n⏳ Waiting five more minutes to avoid quota restriction")
            time.sleep(300)

    send_message(chat_id, "\n🎉 All cycles completed successfully")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    stop_flags[chat_id] = False
    user_data[chat_id] = {}
    bot.send_message(chat_id, "Welcome! Please enter number_oner:")
    bot.register_next_step_handler(message, get_number_oner)

def get_number_oner(message):
    chat_id = message.chat.id
    user_data[chat_id]['number_oner'] = message.text
    bot.send_message(chat_id, "Enter password_oner:")
    bot.register_next_step_handler(message, get_password_oner)

def get_password_oner(message):
    chat_id = message.chat.id
    user_data[chat_id]['password_oner'] = message.text
    bot.send_message(chat_id, "Enter number_men1:")
    bot.register_next_step_handler(message, get_number_men1)

def get_number_men1(message):
    chat_id = message.chat.id
    user_data[chat_id]['number_men1'] = message.text
    bot.send_message(chat_id, "Enter password_men1:")
    bot.register_next_step_handler(message, get_password_men1)

def get_password_men1(message):
    chat_id = message.chat.id
    user_data[chat_id]['password_men1'] = message.text
    bot.send_message(chat_id, "Enter number_men2:")
    bot.register_next_step_handler(message, get_number_men2)

def get_number_men2(message):
    chat_id = message.chat.id
    user_data[chat_id]['number_men2'] = message.text
    bot.send_message(chat_id, "Enter password_men2:")
    bot.register_next_step_handler(message, get_password_men2)

def get_password_men2(message):
    chat_id = message.chat.id
    user_data[chat_id]['password_men2'] = message.text
    bot.send_message(chat_id, "All inputs received. Starting the script in background...")
    threading.Thread(target=run_script, args=(chat_id,)).start()

@bot.message_handler(commands=['stop'])
def stop(message):
    chat_id = message.chat.id
    stop_flags[chat_id] = True
    bot.send_message(chat_id, "🛑 Stop command received. The script will stop at the next safe point.")

def run_polling():
    while True:
        try:
            bot.polling(none_stop=True, timeout=20)
        except ReadTimeout as e:
            print(f"ReadTimeout caught: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Polling error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    # Start polling in a separate thread
    polling_thread = threading.Thread(target=run_polling)
    polling_thread.daemon = True  # Daemon thread to exit when main program exits
    polling_thread.start()
    
    # Keep the main thread alive
    while True:
        time.sleep(60)
import requests
import sys, json, time
import threading
from colorama import Fore, init
import random
import itertools
import logging
import io
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# تمكين التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
INPUT_DATA = 1

# إضافة متغير للتحكم في التوقف
stop_flag = False
script_running = False
script_thread = None
user_data_store = {}

# التقاط output من السكربت
class ScriptOutput:
    def __init__(self):
        self.buffer = io.StringIO()
        self.old_stdout = sys.stdout
        
    def write(self, text):
        self.buffer.write(text)
        self.old_stdout.write(text)
        
    def flush(self):
        self.buffer.flush()
        self.old_stdout.flush()
        
    def get_output(self):
        output = self.buffer.getvalue()
        self.buffer.truncate(0)
        self.buffer.seek(0)
        return output

script_output = ScriptOutput()

# دالة السكربت الرئيسية
def main_function(number_oner, password_oner, number_men1, password_men1, number_men2, password_men2):
    global stop_flag
    stop_flag = False
    
    init(autoreset=True)
    
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
            return None

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
            return None

        acc = "Bearer " + r1['access_token']
        print(Fore.GREEN + "✅ Second member login successful!")
        return acc

        
    def Send_Invite(number_oner, number_men2 , password_oner):
        # Sending invitation to the second member
        access_token = get_access_token_Owner(number_oner, password_oner)
        if not access_token:
            return False
            
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
        return True

    def Accept_Invite(number_oner, number_men2, password_men2):
        acc = get_access_token_Second_number(number_men2, password_men2)
        if not acc:
            return False
            
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
        return True
        
    def Change_Quota(number_oner, number_men1, password_oner):
        access_token = get_access_token_Owner(number_oner, password_oner)
        if not access_token:
            return False
            
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
        return True
        
    def Remove_Number(number_oner, number_men2, password_oner):
        access_token = get_access_token_Owner(number_oner, password_oner)
        if not access_token:
            return False
            
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
        return True

    def Reset_Qota(number_oner, number_men1, password_oner):
        access_token = get_access_token_Owner(number_oner, password_oner)
        if not access_token:
            return False
            
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
        return True

    for i in range(10):
        if stop_flag:
            print(Fore.YELLOW + "🛑 Process stopped by user")
            return
            
        print(Fore.YELLOW + f"\n🌀 Starting cycle number {i+1}")
        Send_Invite(number_oner, number_men2 , password_oner)
        
        for j in range(10):
            if stop_flag:
                print(Fore.YELLOW + "🛑 Process stopped by user")
                return
            time.sleep(1)
            
        t1 = threading.Thread(target=Accept_Invite, args=(number_oner, number_men2, password_men2))
        t2 = threading.Thread(target=Change_Quota, args=(number_oner, number_men1, password_oner))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        for j in range(5):
            if stop_flag:
                print(Fore.YELLOW + "🛑 Process stopped by user")
                return
            time.sleep(1)
            
        Remove_Number(number_oner, number_men2, password_oner)
        
        seconds_left1 = 301
        while seconds_left1 > 0:
            if stop_flag:
                print(Fore.YELLOW + "🛑 Process stopped by user")
                return
            print(Fore.YELLOW + f"Time remaining: {seconds_left1} seconds", end='\r')
            time.sleep(1)
            seconds_left1 -= 1
            
        Reset_Qota(number_oner, number_men1, password_oner)
        
        seconds_left2 = 301
        while seconds_left2 > 0:
            if stop_flag:
                print(Fore.YELLOW + "🛑 Process stopped by user")
                return
            print(Fore.YELLOW + f"Time remaining: {seconds_left2} seconds", end='\r')
            time.sleep(1)
            seconds_left2 -= 1

    print(Fore.GREEN + "\n🎉 All cycles completed successfully")

def stop_script():
    global stop_flag
    stop_flag = True

# وظائف البوت التليجرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء المحادثة وطلب البيانات."""
    await update.message.reply_text(
        "مرحباً! أرسل البيانات بالترتيب التالي في رسالة واحدة:\n\n"
        "رقم المالك\nكلمة مرور المالك\nرقم العضو الأول\nكلمة مرور العضو الأول\nرقم العضو الثاني\nكلمة مرور العضو الثاني\n\n"
        "يفضل فصل البيانات بسطر جديد أو بفاصلة.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return INPUT_DATA

async def input_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة البيانات المدخلة."""
    text = update.message.text
    lines = text.split('\n')
    if len(lines) < 6:
        # محاولة الفصل بالفاصلة
        lines = text.split(',')
    
    if len(lines) < 6:
        await update.message.reply_text(
            "لم يتم إدخال جميع البيانات المطلوبة. يرجى إدخال 6 قيم:\n\n"
            "1. رقم المالك\n2. كلمة مرور المالك\n3. رقم العضو الأول\n4. كلمة مرور العضو الأول\n5. رقم العضو الثاني\n6. كلمة مرور العضو الثاني"
        )
        return INPUT_DATA
    
    # تخزين البيانات
    user_data_store[update.effective_user.id] = {
        'number_oner': lines[0].strip(),
        'password_oner': lines[1].strip(),
        'number_men1': lines[2].strip(),
        'password_men1': lines[3].strip(),
        'number_men2': lines[4].strip(),
        'password_men2': lines[5].strip()
    }
    
    # تأكيد البيانات
    data = user_data_store[update.effective_user.id]
    confirmation = (
        f"تم استلام البيانات:\n\n"
        f"رقم المالك: {data['number_oner']}\n"
        f"كلمة مرور المالك: {data['password_oner']}\n"
        f"رقم العضو الأول: {data['number_men1']}\n"
        f"كلمة مرور العضو الأول: {data['password_men1']}\n"
        f"رقم العضو الثاني: {data['number_men2']}\n"
        f"كلمة مرور العضو الثاني: {data['password_men2']}\n\n"
        f"لبدء التشغيل، أرسل /run\nلإدخال بيانات جديدة، أرسل /start"
    )
    
    await update.message.reply_text(confirmation)
    return ConversationHandler.END

async def run_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تشغيل السكربت الرئيسي."""
    global script_thread, script_running
    
    user_id = update.effective_user.id
    if user_id not in user_data_store:
        await update.message.reply_text("لم يتم إدخال البيانات بعد. أرسل /start لإدخال البيانات.")
        return
    
    if script_running:
        await update.message.reply_text("السكربت يعمل بالفعل.")
        return
    
    data = user_data_store[user_id]
    
    # توجيه output إلى buffer الخاص بنا
    sys.stdout = script_output
    
    # تشغيل السكربت في thread منفصل
    script_running = True
    script_thread = threading.Thread(
        target=main_function,
        args=(
            data['number_oner'],
            data['password_oner'],
            data['number_men1'],
            data['password_men1'],
            data['number_men2'],
            data['password_men2']
        )
    )
    script_thread.daemon = True
    script_thread.start()
    
    # بدء إرسال التحديثات
    context.job_queue.run_repeating(send_updates, interval=10, first=5, chat_id=update.effective_chat.id, name=str(update.effective_chat.id))
    
    await update.message.reply_text("بدأ تشغيل السكربت. سأرسل التحديثات كل 10 ثوانٍ.")

async def send_updates(context: ContextTypes.DEFAULT_TYPE):
    """إرسال تحديثات output السكربت."""
    global script_running
    
    output = script_output.get_output()
    if output:
        # تقسيم النص إذا كان طويلاً
        if len(output) > 4000:
            parts = [output[i:i+4000] for i in range(0, len(output), 4000)]
            for part in parts:
                await context.bot.send_message(chat_id=context.job.chat_id, text=f"```\n{part}\n```", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=context.job.chat_id, text=f"```\n{output}\n```", parse_mode='Markdown')
    
    # التحقق إذا انتهى السكربت
    if script_thread and not script_thread.is_alive():
        script_running = False
        output = script_output.get_output()
        if output:
            if len(output) > 4000:
                parts = [output[i:i+4000] for i in range(0, len(output), 4000)]
                for part in parts:
                    await context.bot.send_message(chat_id=context.job.chat_id, text=f"```\n{part}\n```", parse_mode='Markdown')
            else:
                await context.bot.send_message(chat_id=context.job.chat_id, text=f"```\n{output}\n```", parse_mode='Markdown')
        
        await context.bot.send_message(chat_id=context.job.chat_id, text="✅ اكتمل تشغيل السكربت.")
        context.job.schedule_removal()

async def stop_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف السكربت."""
    global script_running
    
    if not script_running:
        await update.message.reply_text("لا يوجد سكربت يعمل حالياً.")
        return
    
    stop_script()
    script_running = False
    
    # إرسال آخر output
    output = script_output.get_output()
    if output:
        if len(output) > 4000:
            parts = [output[i:i+4000] for i in range(0, len(output), 4000)]
            for part in parts:
                await update.message.reply_text(f"```\n{part}\n```", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
    
    await update.message.reply_text("⏹️ تم إيقاف السكربت.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء المحادثة."""
    await update.message.reply_text(
        "تم الإلغاء.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض رسالة المساعدة."""
    help_text = (
        "أوامر البوت:\n\n"
        "/start - بدء إدخال البيانات\n"
        "/run - تشغيل السكربت بعد إدخال البيانات\n"
        "/stop - إيقاف السكربت أثناء التشغيل\n"
        "/help - عرض هذه الرسالة"
    )
    await update.message.reply_text(help_text)

def main() -> None:
    """تشغيل البوت."""
    # استبدل "YOUR_BOT_TOKEN" بـ token البوت الخاص بك
    application = Application.builder().token("8330939461:AAEUaMYi3UI_sx1pkrSqXT--Hgfzo21zHUg").build()

    # إعداد معالج المحادثة
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INPUT_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # إضافة المعالجات
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("run", run_script))
    application.add_handler(CommandHandler("stop", stop_script))
    application.add_handler(CommandHandler("help", help_command))

    # تشغيل البوت
    application.run_polling()

if __name__ == '__main__':
    main()

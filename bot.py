import os, requests
from telegram import Update
from datetime import datetime
from bs4 import BeautifulSoup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from telegram import Update
from typing import Any

TOKEN = "TOKEN"
BOT_USERNAME = "@yardimci_asistan_bot"
genai.configure(api_key="TOKEN")

url1 = "https://www.savunmasanayist.com/category/haberler/"
url2 = "https://www.trthaber.com/haber/turkiye/"
url3 = "https://www.trthaber.com/haber/dunya/"
url4 = "https://www.donanimhaber.com/savunma-sanayi"
url5 = "https://www.donanimhaber.com/yatirim"
url6 = "https://www.insaatyatirim.com/Haberler/yatirim-haberleri/13"
url7 = "https://www.getmidas.com/canli-borsa/en-cok-artan-hisseler"
url8 = "https://www.getmidas.com/canli-borsa/en-cok-islem-goren-hisseler"
url9 = "https://tr.steelorbis.com/celik-haberleri/guncel-haberler/yatirim?\
        period=2023-03-25+-+2024-03-25&tl=1188-1504-1499&fCountry=1188&f\
        Topic=1504&fTopic=1499&fromDate=2023-03-25&toDate=2024-03-25&submit=F%C4%B0LTRELE"

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update is not None and update.message is not None:
        await log_message(update.message.chat.id, "İşlem Başarısız!", f'{update} - {context.error}')

def get_news_titles(url, tag_name, class_name):
    return ([title.text.strip().replace('', '') for title in BeautifulSoup(requests.get(url).text, 'html.parser').find_all(tag_name, class_=class_name)])

def get_news_titles_2(url):
    return ([title.text.strip().replace('Ücretsiz', '') for title in BeautifulSoup(requests.get(url).text, 'html.parser').find_all('h3', class_="article-lead")])

def get_defense_news():
    return ("\n\n".join(get_news_titles(url1, "h2", "post-title") + get_news_titles(url4, "a", "baslik history-add")))

def get_investment_news():
    return ("\n\n".join(get_news_titles(url5, "a", "baslik history-add") + get_news_titles(url6, "h3", "title")))

def get_steel_investment_news():
    return "\n".join(get_news_titles_2(url9))

def get_most_rising_stocks():
    return "\n".join((get_news_titles(url7, "a", "title stock-code"))[:30])

def get_most_traded_stocks():
    return "\n".join((get_news_titles(url8, "a", "title stock-code"))[:30])

def turkiye_haber():
    return "\n".join((get_news_titles(url2, "a", "site-url"))[30:68])

async def not_ekle(text, user_id):
    filename = os.path.join('notlar_veritabani', f'notlar_{user_id}.txt')
    if not os.path.exists('notlar_veritabani'):
        os.makedirs('notlar_veritabani')
    with open(filename, 'a') as f:
        f.write(text + '\n\n')

async def notlari_gonder(update):
    user_id = update.message.chat.id
    filename = os.path.join('notlar_veritabani', f'notlar_{user_id}.txt')
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            notlar = f.read()
        if not notlar.strip(): 
            await update.message.reply_text("Notunuz Bulunmamaktadır!")
            await log_message(user_id, "İşlem Başarılı!", 'Not Bulunamadı!')
        else:
            await update.message.reply_text(notlar)
            await log_message(user_id, "İşlem Başarılı!", 'Notlar Listelendi!')
    else:
        await update.message.reply_text("Notunuz Bulunmamaktadır.")
        await log_message(user_id, "İşlem Başarılı!", 'Not Bulunamadı!')

async def notlar(text, user_id):
    if not os.path.exists('notlar_veritabani'):
        os.makedirs('notlar_veritabani')
    with open(os.path.join('notlar_veritabani', f'notlar_{user_id}.txt'), 'a') as f:
        f.write(text + '\n\n')

def handle_response(text):
    processed = text.lower()
    if 'savunma_haber' in processed:
        return get_defense_news()
    elif 'yatirim_haber' in processed:
        return get_investment_news()
    elif 'celik_yatirim' in processed:
        return get_steel_investment_news()
    elif 'yukselen_hisse' in processed:
        return get_most_rising_stocks()
    elif 'islem_goren_hisse' in processed:
        return get_most_traded_stocks()
    elif 'turkiye_haber' in processed: 
        return turkiye_haber()
    else:
        return 'Hatalı Komut Girdiniz!'

async def log_message(user_id, text, response):
    text = text.replace('\n', ' ').replace("'", "\\'")
    response = response.replace('\n\n', '\n').replace("'", "\\'")
    with open('log.txt', 'a') as f:
        f.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n- User ({user_id}): "{text}"\n')
        f.write(f'- Bot: {response}\n\n')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        await update.message.reply_text('Geçersiz Komut!\nLütfen doğru bir komut giriniz.')
        await log_message(update.message.chat.id, "İşlem Başarısız!", "Geçersiz Komut.")
        return
    if text.startswith("/"):
        command = text.split()[0].split("@")[0][1:]  
        if command == "not_ekle": 
            await not_ekle_command(update)  
            return
        elif command == "notlari_listele": 
            await notlari_gonder(update)  
            return
        elif command == "chatbot": 
            await chatbot_command(update)  
            return
        elif command == "start": 
            await update.message.reply_text('Hoş Geldiniz.\nYardımcı Olabilmem İçin Komut Girin.')
            return
        elif command not in ["savunma_haber", "yatirim_haber", "celik_yatirim",
                             "yukselen_hisse", "islem_goren_hisse", "turkiye_haber"]:
            await update.message.reply_text('Geçersiz Komut!\nLütfen doğru bir komut giriniz.')
            await log_message(update.message.chat.id, "İşlem Başarısız!", "Geçersiz Komut.")
            return
    else:
        await update.message.reply_text('Lütfen geçerli bir komut girin. Komutlar "/" ile başlamalıdır.')
        return
    if update.message.chat.type == 'group':
        if BOT_USERNAME in text:
            response = handle_response(text.replace(BOT_USERNAME, '').strip())
        else:
            response = handle_response(text)
    else:
        response = handle_response(text)
    if response is None:
        await update.message.reply_text('Böyle bir komut bulunmamaktadır. Lütfen geçerli bir komut girin.')
        await log_message(update.message.chat.id, "İşlem Başarısız!", "Geçersiz Komut.")
    else:
        await update.message.reply_text(response)
        await log_message(update.message.chat.id, "İşlem Başarılı!", "Komut Çalıştırıldı.")
        if "turkiye_haber" in text.lower():
            await update.message.reply_text("Diğer haberlere buradan ulaşabilirsiniz: \n(https://www.trthaber.com/haber/turkiye/)")

async def savunma_sanayi_haberleri_command(update: Update):
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)
    await log_message(update.message.chat.id, text, response)

async def yatirim_haberleri_command(update: Update):
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)
    await log_message(update.message.chat.id, text, response)

async def celik_yatirim_command(update: Update):
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)
    await log_message(update.message.chat.id, text, response)

async def en_cok_yukselen_hisseler_command(update: Update):
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)
    await log_message(update.message.chat.id, text, response)

async def en_cok_islem_goren_hisseler_command(update: Update):
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)
    await log_message(update.message.chat.id, text, response)

async def turkiye_haber_command(update: Update):  
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)
    await log_message(update.message.chat.id, text, response)

async def chatbot_command(update: Update):
    command = update.message.text
    if not command.startswith("/chatbot"):
        await update.message.reply_text("Komut biçimi yanlış. Lütfen '/chatbot \"komut\"' şeklinde girin.")
        return
    text = command.replace("/chatbot", "").strip()
    if not text:
        await update.message.reply_text("Komut göndermek için:\n\"/chatbot komut_yazınız\"")
        return
    await update.message.reply_text("Komutunuz İşleniyor...")
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]
    model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config, safety_settings=safety_settings)
    response = model.generate_content([text])
    await update.message.reply_text(response.text)
    await log_message(update.message.chat.id, text, "Komut İşlendi!")

async def not_ekle_command(update: Update):
    user_id = update.message.chat.id
    text = update.message.text
    if len(text.split()) <= 1: 
        await update.message.reply_text('Not kaydetmek için: \n\"/not_ekle notunuzu_yazınız\"')
        await log_message(user_id, "İşlem Başarısız!", 'Not Kaydedilemedi!')
    else:
        try:
            await not_ekle(f"{datetime.now().strftime('%d.%m.%Y - %H:%M')}\n{text.split('/not_ekle ')[1]}", user_id)
            await update.message.reply_text('Notunuz Kaydedildi!')
            await log_message(user_id, "İşlem Başarılı!", 'Not Kaydedildi!')
        except Exception as e:
            await update.message.reply_text('Not eklenirken bir hata oluştu.')
            await log_message(user_id, "İşlem Başarısız!", f'Hata: {str(e)}')

if __name__ == '__main__':
    print('Bot Başlatıldı...')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | (~filters.Command()), handle_message     ))
    app.add_handler(CommandHandler('savunma_haber',     savunma_sanayi_haberleri_command   ))
    app.add_handler(CommandHandler('yatirim_haber',     yatirim_haberleri_command          ))
    app.add_handler(CommandHandler('celik_yatirim',     celik_yatirim_command              ))
    app.add_handler(CommandHandler('yukselen_hisse',    en_cok_yukselen_hisseler_command   ))
    app.add_handler(CommandHandler('islem_goren_hisse', en_cok_islem_goren_hisseler_command))
    app.add_handler(CommandHandler('turkiye_haber',     turkiye_haber_command              )) 
    app.add_error_handler(error)
    app.run_polling(poll_interval=3)

# chatbot - Yapay Zeka Botu
# not_ekle - Not Ekler
# not_sil - Not Siler
# notlari_listele - Notları Listeler
# savunma_haber - Savunma Sanayii Haberleri
# turkiye_haber - Türkiye Son Dakika Haberleri 
# yatirim_haber - Yatırım Haberleri
# celik_yatirim - Yatırım Haberleri 2
# yukselen_hisse - En Çok Yükselen Hisseler
# islem_goren_hisse - En Çok İşlem Gören Hisseler

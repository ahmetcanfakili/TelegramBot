import os
import asyncio
import requests
from telegram import Update
from datetime import datetime
from bs4 import BeautifulSoup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "TOKEN"
BOT_USERNAME = "@yardimci_asistan_bot"

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

def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def get_news_titles(url, tag_name, class_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_titles = soup.find_all(tag_name, class_=class_name)
    titles = [title.text.strip().replace('', '') for title in news_titles]
    return titles

def get_news_titles_2(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_titles = soup.find_all('h3', class_="article-lead")
    titles = [title.text.strip().replace('Ücretsiz', '') for title in news_titles]
    return titles

def get_defense_news():
    titles1 = get_news_titles(url1, "h2", "post-title")
    titles2 = get_news_titles(url4, "a", "baslik history-add")
    combined_titles = "\n\n".join(titles1 + titles2)
    return combined_titles

def get_investment_news():
    titles1 = get_news_titles(url5, "a", "baslik history-add")
    titles2 = get_news_titles(url6, "h3", "title")
    combined_titles = "\n\n".join(titles1 + titles2)
    return combined_titles

def get_steel_investment_news():
    return "\n".join(get_news_titles_2(url9))

def get_most_rising_stocks():
    titles = get_news_titles(url7, "a", "title stock-code")
    return "\n".join(titles[:30])

def get_most_traded_stocks():
    titles = get_news_titles(url8, "a", "title stock-code")
    return "\n".join(titles[:30])

def turkiye_haber():
    titles = get_news_titles(url2, "a", "site-url")
    return "\n".join(titles[30:68])

async def not_ekle(text, user_id):
    folder_name = 'notlar_veritabani'
    filename = os.path.join(folder_name, f'notlar_{user_id}.txt')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    with open(filename, 'a') as f:
        f.write(text + '\n\n')
        
async def notlari_gonder(update):
    user_id = update.message.chat.id
    folder_name = 'notlar_veritabani'
    filename = os.path.join(folder_name, f'notlar_{user_id}.txt')
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            notlar = f.read()
        if not notlar.strip(): 
            await update.message.reply_text("Notunuz Bulunmamaktadır.")
            await log_message(user_id, "İşlem Başarılı!", 'Not Bulunamadı!')
        else:
            await update.message.reply_text(notlar)
            await log_message(user_id, "İşlem Başarılı!", 'Notlar Listelendi!')
    else:
        await update.message.reply_text("Notunuz Bulunmamaktadır.")
        await log_message(user_id, "İşlem Başarılı!", 'Not Bulunamadı!')

async def notlar(text, user_id):
    folder_name = 'notlar_veritabani'
    filename = os.path.join(folder_name, f'notlar_{user_id}.txt')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    with open(filename, 'a') as f:
        f.write(text + '\n\n')

def handle_response(text):
    processed = text.lower()
    if 'savunmasanayihaberleri' in processed:
        return get_defense_news()
    elif 'yatirimhaberleri' in processed:
        return get_investment_news()
    elif 'celikyatirim' in processed:
        return get_steel_investment_news()
    elif 'encokyukselenhisseler' in processed:
        return get_most_rising_stocks()
    elif 'encokislemgorenhisseler' in processed:
        return get_most_traded_stocks()
    elif 'turkiye_haber' in processed: 
        return turkiye_haber()
    else:
        return 'Hatalı Komut Girdiniz!'

async def log_message(user_id, text, response):
    log_file = 'log.txt'
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    with open(log_file, 'a') as f:
        text = text.replace('\n', ' ')
        response = response.replace('\n\n', '\n')
        f.write(f'{current_time}\n- User ({user_id}): "{text}"\n')
        f.write(f'- Bot: {response}\n\n')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    if not text:
        await update.message.reply_text('Geçersiz bir komut girdiniz. Lütfen doğru bir komut kullanın!')
        return
    if text.startswith("/"):
        command = text.split()[0].split("@")[0][1:]  
        if command == "not_ekle": 
            await not_ekle_command(update)  
            return
        elif command == "notlar": 
            await notlari_gonder(update)  
            return
        elif command == "start": 
            await update.message.reply_text('Hoş Geldiniz.\nYardımcı Olabilmem İçin Komut Girin.')
            return
        elif command not in ["savunmasanayihaberleri", "yatirimhaberleri", "celikyatirim",
                             "encokyukselenhisseler", "encokislemgorenhisseler", "turkiye_haber"]:
            await update.message.reply_text('Geçersiz bir komut girdiniz. Lütfen doğru bir komut kullanın!')
            return
    else:
        await update.message.reply_text('Lütfen geçerli bir komut girin. Komutlar "/" ile başlamalıdır.')
        return
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
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

async def not_ekle_command(update: Update):
    user_id = update.message.chat.id
    text = update.message.text
    if len(text.split()) <= 1: 
        await update.message.reply_text('Not kaydetmek için: \n\"/not_ekle notunuzu_yazınız\"')
        await log_message(user_id, "İşlem Başarısız!", 'Not Kaydedilemedi!')
    else:
        try:
            note_text = text.split("/not_ekle ")[1]
            yeni_not = f"{datetime.now().strftime('%d.%m.%Y %H:%M')}\n{note_text}"
            await not_ekle(yeni_not, user_id)
            await update.message.reply_text('Notunuz Kaydedildi!')
            await log_message(user_id, "İşlem Başarılı!", 'Not Kaydedildi!')
        except Exception as e:
            await update.message.reply_text('Not eklenirken bir hata oluştu.')
            await log_message(user_id, "İşlem Başarısız!", f'Hata: {str(e)}')

if __name__ == '__main__':
    print('Bot Başlatıldı...')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | (~filters.Command()), handle_message))
    app.add_handler(CommandHandler('savunmasanayihaberleri',  savunma_sanayi_haberleri_command   ))
    app.add_handler(CommandHandler('yatirimhaberleri',        yatirim_haberleri_command          ))
    app.add_handler(CommandHandler('celikyatirim',            celik_yatirim_command              ))
    app.add_handler(CommandHandler('encokyukselenhisseler',   en_cok_yukselen_hisseler_command   ))
    app.add_handler(CommandHandler('encokislemgorenhisseler', en_cok_islem_goren_hisseler_command))
    app.add_handler(CommandHandler('turkiye_haber',           turkiye_haber_command              )) 
    app.add_error_handler(error)
    app.run_polling(poll_interval=3)

# savunmasanayihaberleri - Savunma Sanayii Haberleri
# yatirimhaberleri - Yatırım Haberleri
# celikyatirim - Yatırım Haberleri 2
# encokyukselenhisseler - En Çok Yükselen Hisseler
# encokislemgorenhisseler - En Çok İşlem Gören Hisseler
# turkiye_haber - Türkiye Son Dakika Haberleri 
# not_ekle - Hatırlatıcı Notu Eklenir
# notlar - Tüm Notları Listeler

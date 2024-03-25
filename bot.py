import requests
from typing import Final
from telegram import Update
from bs4 import BeautifulSoup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

url1 = "https://www.savunmasanayist.com/category/haberler/"                         # savunmasanayist.com / savunma haber
url4 = "https://www.donanimhaber.com/savunma-sanayi"                                # donanimhaber.com / savunma haber
url5 = "https://www.donanimhaber.com/yatirim"                                       # donanimhaber.com / yatırım
url6 = "https://www.insaatyatirim.com/Haberler/yatirim-haberleri/13"                # insaatyatirim.com / yatırım
url9 = "https://tr.steelorbis.com/celik-haberleri/guncel-haberler/yatirim?period\
        =2023-03-25+-+2024-03-25&tl=1188-1504-1499&fCountry=1188&fTopic=1504&f\
        Topic=1499&fromDate=2023-03-25&toDate=2024-03-25&submit=F%C4%B0LTRELE"      # yatırım
url7 = "https://www.getmidas.com/canli-borsa/en-cok-artan-hisseler"                 # en çok artan hisseler
url8 = "https://www.getmidas.com/canli-borsa/en-cok-islem-goren-hisseler"           # en çok işlem gören hisseler

TOKEN: Final        = 'TOKEN'
BOT_USERNAME: Final = '@borsa_yatirim_bot'

def get_news_titles(url, tag_name, class_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_titles = soup.find_all(tag_name, class_=class_name)
    titles = [title.text.strip() for title in news_titles]
    return titles

def get_news_titles_2(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_titles = soup.find_all('h3', class_="article-lead")
    titles = [title.text.strip().replace('Ücretsiz', '') for title in news_titles]
    return titles

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Selam!')

def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'savunmasanayihaberleri' in processed:
        titles1 = get_news_titles(url1, "h2", "post-title")
        titles2 = get_news_titles(url4, "a", "baslik history-add")
        combined_titles = "\n\n".join(titles1 + titles2)
        return combined_titles
    if 'yatirimhaberleri' in processed:
        titles1 = get_news_titles(url5, "a", "baslik history-add")
        titles2 = get_news_titles(url6, "h3", "title")
        combined_titles = "\n\n".join(titles1 + titles2)
        return combined_titles
    if 'celikyatirim' in processed:
        titles = "\n".join(get_news_titles_2(url9))
        return titles
    if 'encokyukselenhisseler' in processed:
        titles = get_news_titles(url7, "a", "title stock-code")
        return "\n".join(titles[:30])
    if 'encokislemgorenhisseler' in processed:
        titles = get_news_titles(url8, "a", "title stock-code")
        return "\n".join(titles[:30])
    return 'Hatalı Komut Girdiniz!'

def log_message(user_id, message_type, text, response):
    log_file = 'log.txt'
    with open(log_file, 'a') as f:
        f.write(f'User ({user_id}) in {message_type}: "{text}"\n')
        f.write(f'Bot: {response}\n')
   
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bu İşlem Biraz Zaman Alabilir...")
    message_type: str = update.message.chat.type
    text: str = update.message.text
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    await update.message.reply_text(response)
    log_message(update.message.chat.id, message_type, text, response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Bot Başlatıldı...')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)
    app.run_polling(poll_interval=3)

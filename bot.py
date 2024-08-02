#BOT CODE, CHANGE TOKEN TO YOUR BOT TOKEN(line: 10) WHAT YOU GOT FROM @BotFather , AND PASTE YOUR TELEGRAM ID IN admins(line: 16) LIST
#Send '/help' command to bot for see all commands

import telebot
import sqlite3
import json
import random
import string
import os

TOKEN = 'PASTE HERE YOUR BOT API'
bot = telebot.TeleBot(TOKEN)

product_imgs = 'product_images' #Path to floder where save all photos of your products
news_file = 'news.json' #Path to file where save text of newsletters
database = 'database/database.db' #Path to database
admins = [] #Paste here admins telegram ID (For newsletter, adding new products)
manager = [] #Paste here telegram ID of people who accept your products

#generate random name for image
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

#add user to database afrer that they write /start
def check_and_add_user(user_id):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user = ?', (user_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.execute('INSERT INTO users (user, areact) VALUES (?, ?)', (user_id, 'Active'))
    conn.commit()
    conn.close()
    return user

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = check_and_add_user(user_id)
    
    if user is None:
        menu = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        products = telebot.types.KeyboardButton('Products🛍️')
        contacts = telebot.types.KeyboardButton('Contacts📱')
        howtobuy = telebot.types.KeyboardButton('How to buy❓')
        menu.add(products, contacts, howtobuy)
        bot.send_message(message.chat.id, '👋 Welcome to shop!\n\nIn this store you will make all your dreams come true!', reply_markup=menu)
    else:
        menu = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        products = telebot.types.KeyboardButton('Products🛍️')
        contacts = telebot.types.KeyboardButton('Contacts📱')
        howtobuy = telebot.types.KeyboardButton('How to buy❓')
        menu.add(products, contacts, howtobuy)
        bot.send_message(message.chat.id, '👋 Welcome to shop!\n\nIn this store you will make all your dreams come true!', reply_markup=menu)

#command for refresh menu
@bot.message_handler(commands=['refresh'])
def refresh(message):
    menu = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    products = telebot.types.KeyboardButton('Products🛍️')
    contacts = telebot.types.KeyboardButton('Contacts📱')
    howtobuy = telebot.types.KeyboardButton('How to buy❓')
    menu.add(products, contacts, howtobuy)
    bot.send_message(message.chat.id, '🔄 Your menu has been refreshed!', reply_markup=menu)

#command for add new product
@bot.message_handler(commands=['addproduct'])
def addproduct(message):
    user_id = message.from_user.id
    if user_id in admins:
        bot.send_message(message.chat.id, 'Please, enter name of your product:')
        bot.register_next_step_handler(message, add_product_name)
    else:
        bot.send_message(message.chat.id, "You can't use this command.")

product_data = {}

def add_product_name(message):
    product_data['name'] = message.text
    bot.send_message(message.chat.id, 'Okay, now enter description of your product:')
    bot.register_next_step_handler(message, add_product_description)

def add_product_description(message):
    product_data['description'] = message.text
    bot.send_message(message.chat.id, 'Okay, now enter price of your product:')
    bot.register_next_step_handler(message, add_product_price)

def add_product_price(message):
    product_data['price'] = message.text
    bot.send_message(message.chat.id, 'Okay, now enter category of your product:')
    bot.register_next_step_handler(message, add_product_category)

def add_product_category(message):
    product_data['category'] = message.text
    bot.send_message(message.chat.id, 'Okay, now send image of your product:')
    bot.register_next_step_handler(message, add_product_image)

def add_product_image(message):
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        random_filename = generate_random_string() + '.jpg'
        photo_path = os.path.join(product_imgs, random_filename)

        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        product_data['image'] = random_filename

        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, description, price, category, image) VALUES (?, ?, ?, ?, ?)',
                       (product_data['name'], product_data['description'], product_data['price'], product_data['category'], product_data['image']))
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, '✅ Your product added! Check it!')
    else:
        bot.send_message(message.chat.id, '❌ Error')

@bot.message_handler(func=lambda message: message.text == 'Contacts📱')
def contacts(message):
    bot.send_message(message.chat.id, '*Location:* Los Angeles\n*Email:* shop@example.com\nWorking hours: Mon-Fri 10:00-18:00\n', parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == 'Products🛍️')
def assortment(message):
    menu = telebot.types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    categories = ['Electronics💻', 'Clothes🧥', 'Toys🎲', 'Books📖', 'Video-Games🎮', 'Cars🚗', 'Home🏠', 'Comics🃏', 'Souvenirs🎴']
    buttons = [telebot.types.KeyboardButton(category) for category in categories]
    menu.add(*buttons)
    bot.send_message(message.chat.id, 'Write /refresh for back to start menu.', reply_markup=menu, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text.endswith('💻') or message.text.endswith('🧥') or message.text.endswith('🎲') or message.text.endswith('📖') or message.text.endswith('🎮') or message.text.endswith('🚗') or message.text.endswith('🏠') or message.text.endswith('🃏') or message.text.endswith('🎴'))
def show_products(message):
    category = message.text.split(' ')[0]
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('SELECT name, description, price, image FROM products WHERE category=?', (category,))
    products = cursor.fetchall()
    conn.close()

    if products:
        for product in products:
            name, description, price, image = product
            with open(os.path.join(product_imgs, image), 'rb') as img:
                markup = telebot.types.InlineKeyboardMarkup()
                buy_button = telebot.types.InlineKeyboardButton('Buy', callback_data=f'buy_{name}')
                markup.add(buy_button)
                bot.send_photo(message.chat.id, img, caption=f'*{name}*\n\n_{description}_\n\nPrice: {price}', reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'No products found in this category.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy(call):
    product_name = call.data.split('_')[1]
    bot.send_message(call.message.chat.id, 'Please, enter your name:')
    bot.register_next_step_handler(call.message, lambda msg: process_name(msg, product_name))

def process_name(message, product_name):
    customer_name = message.text
    bot.send_message(message.chat.id, 'Please, enter your phone number:')
    bot.register_next_step_handler(message, lambda msg: process_phone(msg, product_name, customer_name))

def process_phone(message, product_name, customer_name):
    phone = message.text
    customer_username = message.from_user.username
    customer_id = message.from_user.id

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (product, name, username, id, phonenumber) VALUES (?, ?, ?, ?, ?)',
                   (product_name, customer_name, customer_username, customer_id, phone))
    conn.commit()
    conn.close()

    for manager_id in manager:
        bot.send_message(manager_id, f'New order!\nProduct: {product_name}\nCustomer Name: {customer_name}\nTelegram Username: @{customer_username}\nTelegram ID: {customer_id}\nPhone: {phone}')

    bot.send_message(message.chat.id, 'Thank you for your purchase! We will contact you soon.')

# Command to add news
@bot.message_handler(commands=['addnews'])
def add_news_start(message):
    user_id = message.from_user.id
    if user_id in admins:
        msg = bot.send_message(user_id, "📝 Please write the news:")
        bot.register_next_step_handler(msg, add_news_finish)
    else:
        bot.send_message(user_id, "🚫 You do not have permission to add news.")

def add_news_finish(message):
    user_id = message.from_user.id
    news_text = message.text
    
    if os.path.exists(news_file):
        with open(news_file, 'r') as file:
            news_list = json.load(file)
    else:
        news_list = []

    news_list.append({'text': news_text})
    
    with open(news_file, 'w') as file:
        json.dump(news_list, file, indent=4)

    bot.send_message(user_id, "✅ News added successfully!")

# Command to view news
@bot.message_handler(commands=['seenews'])
def see_news(message):
    user_id = message.from_user.id
    if user_id in admins:
        if os.path.exists(news_file):
            with open(news_file, 'r') as file:
                news_list = json.load(file)
            
            if news_list:
                for news in news_list:
                    news_message = f"🗞 {news['text']}"
                    bot.send_message(user_id, news_message)
            else:
                bot.send_message(user_id, "ℹ️ No news available.")
        else:
            bot.send_message(user_id, "ℹ️ No news file found.")
    else:
        bot.send_message(user_id, "🚫 You do not have permission to view news.")

# Command to send news to all users
@bot.message_handler(commands=['sendnews'])
def send_news(message):
    user_id = message.from_user.id
    if user_id in admins:
        if os.path.exists(news_file):
            with open(news_file, 'r') as file:
                news_list = json.load(file)
            
            if news_list:
                latest_news = news_list[-1]
                news_message = f"{latest_news['text']}"
                
                conn = sqlite3.connect(database)
                cursor = conn.cursor()
                cursor.execute('SELECT user FROM users')
                users = cursor.fetchall()
                conn.close()

                for user in users:
                    user_id = user[0]
                    try:
                        bot.send_message(user_id, news_message)
                    except telebot.apihelper.ApiException as e:
                        print(f"Failed to send message to user {user_id}: {e}")
            else:
                bot.send_message(user_id, "ℹ️ No news available to send.")
        else:
            bot.send_message(user_id, "ℹ️ No news file found.")
    else:
        bot.send_message(user_id, "🚫 You do not have permission to send news.")

def send_message_with_block_check(user_id, text):
    try:
        bot.send_message(user_id, text)
        return True
    except telebot.apihelper.ApiException as e:
        if e.error_code == 403:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET areact = "Disable" WHERE user = ?', (user_id,))
            conn.commit()
            conn.close()
        return False

@bot.message_handler(commands=['help'])
def helpp(message):
    user_id = message.from_user.id
    if user_id in admins:
        bot.send_message(message.chat.id, 'Commands list:\n\n/addproduct - add new product to your shop.\n\n/addnews - add new text to newsletter\n\n/seenews - check your text for newsletter (Bot send text only to you)\n\n/sendnews - bot send newsletter to everyone who used your bot.')
    else:
        bot.send_message(message.chat.id, '🚫 You do not have permission to use this command.')

bot.polling(none_stop=True)
import os
import django
import telebot
from partner.models import Product, Order
from customer.models import CustomerProfile

# Django sozlamalarini o'rnatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Botning qolgan kodlari
BOT_TOKEN = '8036800793:AAEPHm_wttAv8A8U7ZUqon108wGykXf9Kdo'
ADMIN_CHAT_ID = '5282231484'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Assalomu alaykum! Mahsulot buyurtma yoki sotuv jarayonini boshqarish uchun tanlang.")
    show_main_menu(message)

def show_main_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🛒 Buyurtma qilish", "📈 Sotuvlar statistikasi")
    bot.send_message(message.chat.id, "Menyuni tanlang:", reply_markup=keyboard)

@bot.message_handler(func=lambda msg: msg.text == "🛒 Buyurtma qilish")
def list_products(message):
    products = Product.objects.all()
    if products.exists():
        for product in products:
            bot.send_message(
                message.chat.id,
                f"Mahsulot: {product.name}\nNarx: {product.price}",
                reply_markup=product_keyboard(product)
            )
    else:
        bot.send_message(message.chat.id, "Hozircha hech qanday mahsulot mavjud emas.")

def product_keyboard(product):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("Buyurtma berish", callback_data=f"order_{product.id}")
    )
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def place_order(call):
    product_id = int(call.data.split("_")[1])
    try:
        customer = CustomerProfile.objects.get(user_id=call.from_user.id)
        product = Product.objects.get(id=product_id)
        Order.objects.create(customer=customer.user, product=product, quantity=1)
        bot.send_message(call.message.chat.id, "Buyurtmangiz qabul qilindi!")
        notify_admin(product, customer)
    except CustomerProfile.DoesNotExist:
        bot.send_message(call.message.chat.id, "Profilingiz topilmadi. Iltimos, ro'yxatdan o'ting.")
    except Product.DoesNotExist:
        bot.send_message(call.message.chat.id, "Mahsulot topilmadi.")

def notify_admin(product, customer):
    message = (
        f"Yangi buyurtma!\n\n"
        f"Mijoz: {customer.user.username}\n"
        f"Telefon: {customer.phone_number}\n"
        f"Mahsulot: {product.name}\n"
        f"Narx: {product.price}"
    )
    bot.send_message(ADMIN_CHAT_ID, message)

bot.polling()
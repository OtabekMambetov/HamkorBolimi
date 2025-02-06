import telebot
import django
import os
from django.db import IntegrityError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myapp.models import Partner, Product

TOKEN = "7654859599:AAFhRYoIY9puyxk2U21lAjFSnj-wbbf_vfQ"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 5282231484

IMAGE_DIR = "product_images/"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

@bot.message_handler(commands=['start'])
def start(message):
    # Foydalanuvchi telegram_id sini tekshiramiz
    try:
        partner = Partner.objects.get(telegram_id=str(message.from_user.id))
        if partner.is_approved:
            send_partner_menu(message.from_user.id)
        else:
            bot.send_message(message.chat.id, "Siz hali admin tomonidan tasdiqlanmagansiz. Tasdiqlanishni kuting.")
    except Partner.DoesNotExist:
        bot.send_message(message.chat.id, "Assalomu alaykum! Hamkor bo‘lish uchun ismingizni kiriting:")
        bot.register_next_step_handler(message, get_full_name)

def get_full_name(message):
    full_name = message.text
    bot.send_message(message.chat.id, "Telefon raqamingizni jo‘nating (Kontaktingizni ulashing).",
                     reply_markup=contact_keyboard())
    bot.register_next_step_handler(message, get_contact, full_name)

def contact_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = telebot.types.KeyboardButton(text="📞 Kontaktni ulashish", request_contact=True)
    keyboard.add(button)
    return keyboard

def get_contact(message, full_name):
    if message.contact:
        phone_number = message.contact.phone_number
        bot.send_message(message.chat.id, "Firma nomini kiriting:")
        bot.register_next_step_handler(message, get_company_name, full_name, phone_number)
    else:
        bot.send_message(message.chat.id, "Iltimos, kontaktni yuboring!")
        bot.register_next_step_handler(message, get_contact, full_name)

def get_company_name(message, full_name, phone_number):
    company_name = message.text
    try:
        partner = Partner.objects.create(
            full_name=full_name,
            phone_number=phone_number,
            company_name=company_name,
            telegram_id=message.from_user.id  # Telegram IDni saqlash
        )
        # Inline tugma yaratish
        keyboard = telebot.types.InlineKeyboardMarkup()
        approve_button = telebot.types.InlineKeyboardButton(text="Tasdiqlash", callback_data=f"approve_{partner.id}")
        reject_button = telebot.types.InlineKeyboardButton(text="Rad etish", callback_data=f"reject_{partner.id}")
        keyboard.add(approve_button, reject_button)

        bot.send_message(ADMIN_ID, f"Yangi hamkor: {full_name}\nTelefon: {phone_number}\nFirma: {company_name}", reply_markup=keyboard)
        bot.send_message(message.chat.id, "Hamkorlik uchun ro‘yxatdan o‘tdingiz! Admin tasdiqlashini kuting.")
    except IntegrityError:
        bot.send_message(message.chat.id, "Xatolik! Bu telefon raqami allaqachon mavjud.")

# Callback funksiyalar
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_partner(call):
    if call.from_user.id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "Sizda bu amalni bajarish huquqi yo'q!")

    partner_id = int(call.data.split("_")[1])
    try:
        partner = Partner.objects.get(id=partner_id)
        partner.is_approved = True
        partner.save()

        # Foydalanuvchini tekshirish va xabar yuborish
        try:
            bot.send_message(partner.telegram_id, "Hamkorlik tasdiqlandi! Mahsulot qo‘shish menyusidan foydalaning.")
            send_partner_menu(partner.telegram_id)
        except telebot.apihelper.ApiTelegramException as e:
            if e.result.status_code == 400:
                bot.answer_callback_query(call.id, "Xatolik! Foydalanuvchi botni boshlamagan yoki bloklagan.")

        bot.answer_callback_query(call.id, f"Hamkor {partner.full_name} tasdiqlandi!")
    except Partner.DoesNotExist:
        bot.answer_callback_query(call.id, "Xatolik! Hamkor ID noto‘g‘ri.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_partner(call):
    if call.from_user.id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "Sizda bu amalni bajarish huquqi yo'q!")

    partner_id = int(call.data.split("_")[1])
    try:
        partner = Partner.objects.get(id=partner_id)
        partner.delete()

        bot.answer_callback_query(call.id, f"Hamkor {partner.full_name} rad etildi!")
    except Partner.DoesNotExist:
        bot.answer_callback_query(call.id, "Xatolik! Hamkor ID noto‘g‘ri.")

def send_partner_menu(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Mahsulot qo'shish", "Mahsulotlarni ko'rish")
    bot.send_message(user_id, "Hamkorlik menyusi:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Mahsulot qo'shish")
def add_product(message):
    try:
        partner = Partner.objects.get(telegram_id=str(message.from_user.id))
        if not partner.is_approved:
            bot.send_message(message.chat.id, "Siz hali admin tomonidan tasdiqlanmagansiz. Tasdiqlanishni kuting.")
            return
    except Partner.DoesNotExist:
        bot.send_message(message.chat.id, "Siz ro'yxatdan o'tmagansiz!")
        return

    bot.send_message(message.chat.id, "Mahsulot nomini kiriting:")
    bot.register_next_step_handler(message, get_product_name)

def get_product_name(message):
    product_name = message.text
    bot.send_message(message.chat.id, "Mahsulot narxini kiriting:")
    bot.register_next_step_handler(message, get_product_price, product_name)

def get_product_price(message, product_name):
    try:
        product_price = float(message.text)
        bot.send_message(message.chat.id, "Mahsulot rasmini yuboring:")
        bot.register_next_step_handler(message, get_product_image, product_name, product_price)
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, narxni to'g'ri formatda kiriting.")
        bot.register_next_step_handler(message, get_product_price, product_name)

def get_product_image(message, product_name, product_price):
    if not message.photo:
        bot.send_message(message.chat.id, "Iltimos, mahsulot rasmini yuboring!")
        bot.register_next_step_handler(message, get_product_image, product_name, product_price)
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image_name = os.path.join(IMAGE_DIR, f"{file_id}.jpg")
    with open(image_name, "wb") as new_file:
        new_file.write(downloaded_file)

    product = Product.objects.create(name=product_name, price=product_price, image=image_name)
    bot.send_message(message.chat.id, f"Mahsulot: {product_name} qo‘shildi! Narxi: {product_price} so‘m")

@bot.message_handler(func=lambda message: message.text == "Mahsulotlarni ko'rish")
def view_products(message):
    products = Product.objects.all()
    if products:
        for product in products:
            with open(product.image.path, "rb") as img:
                bot.send_photo(message.chat.id, img, caption=f"{product.name}: {product.price} so‘m")
    else:
        bot.send_message(message.chat.id, "Mahsulotlar mavjud emas.")

@bot.message_handler(commands=['partners'])
def view_partners(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "Sizda bu amalni bajarish huquqi yo'q!")

    partners = Partner.objects.all()
    if partners:
        for partner in partners:
            approval_status = "Tasdiqlangan" if partner.is_approved else "Tasdiqlanmagan"
            bot.send_message(
                message.chat.id,
                f"ID: {partner.id}\nIsm: {partner.full_name}\nTelefon: {partner.phone_number}\nFirma: {partner.company_name}\nHolati: {approval_status}"
            )
    else:
        bot.send_message(message.chat.id, "Hozircha hech qanday hamkorlar mavjud emas.")

bot.polling()
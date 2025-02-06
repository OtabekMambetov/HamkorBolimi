from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Partner(models.Model):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=255)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)  # Telegram ID
    is_approved = models.BooleanField(default=False)  # Tasdiqlash maydoni

    objects = models.Manager()

    def __str__(self):
        return self.full_name



class Product(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    quantity = models.IntegerField(default=1)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name
import sqlite3

# Ma'lumotlar bazasini yaratish
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Kategoriyalar jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# Mahsulotlar jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
""")

conn.commit()
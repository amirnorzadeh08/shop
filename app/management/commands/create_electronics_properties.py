from django.core.management.base import BaseCommand
from app.models import Category, Property
import json


class Command(BaseCommand):
	help = 'Creates 7-20 properties for each subcategory of Electronics'

	def handle(self, *args, **kwargs):
		# یافتن دسته اصلی الکترونیک
		electronics = Category.objects.get(catName="الکترونیک")

		# دریافت تمام زیردسته‌های الکترونیک
		subcategories = Category.objects.filter(parentCatId=electronics)

		# دیکشنری ویژگی‌ها برای هر زیردسته
		properties_map = {
			"موبایل": [
				{"propName": "برند", "input_type": "select",
				 "options": ["سامسونگ", "اپل", "شیائومی", "هوآوی", "نوکیا", "ال جی", "موتورولا"]},
				{"propName": "مدل", "input_type": "text"},
				{"propName": "رنگ", "input_type": "select",
				 "options": ["مشکی", "سفید", "آبی", "قرمز", "طلایی", "نقره‌ای"]},
				{"propName": "حافظه داخلی", "input_type": "select",
				 "options": ["32GB", "64GB", "128GB", "256GB", "512GB", "1TB"]},
				{"propName": "RAM", "input_type": "select", "options": ["2GB", "4GB", "6GB", "8GB", "12GB", "16GB"]},
				{"propName": "اندازه صفحه نمایش", "input_type": "number"},
				{"propName": "سیستم عامل", "input_type": "select", "options": ["اندروید", "iOS", "ویندوز فون", "سایر"]},
				{"propName": "تعداد سیم کارت", "input_type": "number"},
				{"propName": "دوربین اصلی", "input_type": "number"},
				{"propName": "دوربین جلو", "input_type": "number"},
				{"propName": "باتری", "input_type": "number"},
				{"propName": "فناوری شبکه", "input_type": "select", "options": ["2G", "3G", "4G", "5G"]},
				{"propName": "سال تولید", "input_type": "number"},
				{"propName": "وضعیت گارانتی", "input_type": "select", "options": ["دارد", "ندارد"]},
			],
			"تبلت": [
				{"propName": "برند", "input_type": "select",
				 "options": ["سامسونگ", "اپل", "لنوو", "هواوی", "امازون", "مایکروسافت"]},
				{"propName": "مدل", "input_type": "text"},
				{"propName": "اندازه صفحه نمایش", "input_type": "number"},
				{"propName": "رزولوشن", "input_type": "text"},
				{"propName": "حافظه داخلی", "input_type": "select", "options": ["32GB", "64GB", "128GB", "256GB"]},
				{"propName": "RAM", "input_type": "select", "options": ["2GB", "4GB", "6GB", "8GB"]},
				{"propName": "سیستم عامل", "input_type": "select", "options": ["اندروید", "iOS", "ویندوز"]},
				{"propName": "پردازنده", "input_type": "text"},
				{"propName": "باتری", "input_type": "number"},
				{"propName": "دوربین اصلی", "input_type": "number"},
				{"propName": "دوربین جلو", "input_type": "number"},
				{"propName": "اتصالات", "input_type": "select", "options": ["Wi-Fi", "4G", "5G", "GPS"]},
			],
			"لپ تاپ": [
				{"propName": "برند", "input_type": "select",
				 "options": ["اپل", "دل", "اچ پی", "لنوو", "ایسوس", "ایسر", "ام اس آی"]},
				{"propName": "مدل", "input_type": "text"},
				{"propName": "پردازنده", "input_type": "select",
				 "options": ["Intel Core i3", "Intel Core i5", "Intel Core i7", "Intel Core i9", "AMD Ryzen 3",
				             "AMD Ryzen 5", "AMD Ryzen 7"]},
				{"propName": "حافظه RAM", "input_type": "select", "options": ["4GB", "8GB", "16GB", "32GB", "64GB"]},
				{"propName": "حافظه داخلی", "input_type": "select",
				 "options": ["256GB SSD", "512GB SSD", "1TB SSD", "1TB HDD", "2TB HDD"]},
				{"propName": "اندازه صفحه نمایش", "input_type": "number"},
				{"propName": "کارت گرافیک", "input_type": "text"},
				{"propName": "سیستم عامل", "input_type": "select",
				 "options": ["Windows", "macOS", "Linux", "بدون سیستم عامل"]},
				{"propName": "وزن", "input_type": "number"},
				{"propName": "باتری", "input_type": "text"},
				{"propName": "پورت‌ها", "input_type": "text"},
				{"propName": "نوع لپ تاپ", "input_type": "select",
				 "options": ["گیمر", "اداری", "مالتی مدیا", "نازک و سبک"]},
				{"propName": "سال تولید", "input_type": "number"},
			],
			"هدفون و هندزفری": [
				{"propName": "برند", "input_type": "select",
				 "options": ["اپل", "سامسونگ", "سونی", "بیتس", "جی بی ال", "شیائومی"]},
				{"propName": "مدل", "input_type": "text"},
				{"propName": "نوع", "input_type": "select",
				 "options": ["هدفون", "هندزفری", "هدفون بی سیم", "هندزفری بی سیم"]},
				{"propName": "فناوری اتصال", "input_type": "select", "options": ["بلوتوث", "سیمی", "هر دو"]},
				{"propName": "رنگ", "input_type": "select", "options": ["مشکی", "سفید", "آبی", "قرمز", "نقره‌ای"]},
				{"propName": "محدوده فرکانسی", "input_type": "text"},
				{"propName": "امپدانس", "input_type": "number"},
				{"propName": "حساسیت", "input_type": "number"},
				{"propName": "قابلیت‌ها", "input_type": "select",
				 "options": ["نویزکنسلینگ", "میکروفون", "ضد آب", "تا شو"]},
				{"propName": "باتری", "input_type": "text"},
			],
			"شارژر و کابل": [
				{"propName": "برند", "input_type": "select", "options": ["اپل", "سامسونگ", "آنکر", "بلکین", "یوروکبل"]},
				{"propName": "نوع", "input_type": "select",
				 "options": ["شارژر دیواری", "شارژر فندکی", "شارژر بی سیم", "کابل USB"]},
				{"propName": "پورت", "input_type": "select", "options": ["USB-A", "USB-C", "Lightning", "Micro USB"]},
				{"propName": "توان خروجی", "input_type": "text"},
				{"propName": "طول کابل", "input_type": "number"},
				{"propName": "قابلیت‌ها", "input_type": "select", "options": ["فست شارژ", "شارژ هوشمند", "قابل حمل"]},
				{"propName": "سازگاری", "input_type": "text"},
			],
			"پاوربانک": [
				{"propName": "برند", "input_type": "select",
				 "options": ["شیائومی", "آنکر", "راوان", "سامسونگ", "روموس"]},
				{"propName": "ظرفیت", "input_type": "number"},
				{"propName": "تعداد پورت", "input_type": "number"},
				{"propName": "جریان خروجی", "input_type": "text"},
				{"propName": "فناوری‌ها", "input_type": "select",
				 "options": ["Power Delivery", "Quick Charge", "شارژ هوشمند"]},
				{"propName": "وزن", "input_type": "number"},
				{"propName": "ابعاد", "input_type": "text"},
				{"propName": "جنس بدنه", "input_type": "select", "options": ["پلاستیک", "فلزی", "ترکیبی"]},
			],
			"ساعت هوشمند": [
				{"propName": "برند", "input_type": "select",
				 "options": ["اپل", "سامسونگ", "هواوی", "شیائومی", "امازون"]},
				{"propName": "مدل", "input_type": "text"},
				{"propName": "اندازه صفحه نمایش", "input_type": "number"},
				{"propName": "رزولوشن", "input_type": "text"},
				{"propName": "سیستم عامل", "input_type": "select", "options": ["WatchOS", "Wear OS", "Tizen", "سایر"]},
				{"propName": "باتری", "input_type": "text"},
				{"propName": "مقاومت در آب", "input_type": "select", "options": ["دارد", "ندارد"]},
				{"propName": "سنسورها", "input_type": "select",
				 "options": ["ضربان قلب", "GPS", "شتاب‌سنج", "ژیروسکوپ", "ECG"]},
				{"propName": "رنگ", "input_type": "select", "options": ["مشکی", "سفید", "نقره‌ای", "طلایی", "آبی"]},
				{"propName": "جنس بند", "input_type": "select", "options": ["سیلیکونی", "فلزی", "چرمی", "پارچه‌ای"]},
			]
		}

		created_count = 0

		for subcategory in subcategories:
			sub_name = subcategory.catName
			if sub_name in properties_map:
				properties = properties_map[sub_name]
				for prop_data in properties:
					# تبدیل لیست options به JSON اگر وجود دارد
					select_options = json.dumps(prop_data.get('options', [])) if 'options' in prop_data else None

					# ایجاد ویژگی
					_, created = Property.objects.get_or_create(
						catId=subcategory,
						propName=prop_data['propName'],
						defaults={
							'input_type': prop_data['input_type'],
							'select_options': select_options
						}
					)

					if created:
						created_count += 1

		self.stdout.write(self.style.SUCCESS(
			f"Successfully created {created_count} properties "
			f"for {len(subcategories)} electronic subcategories"
		))
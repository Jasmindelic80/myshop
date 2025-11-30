# 🛒 MyShop — Django E-Commerce Web Application

MyShop is a simple e-commerce web application built using **Python & Django**, designed as a portfolio project to demonstrate full-stack web development skills.

The application supports product listing, cart functionality, and admin management of items.

---

## 🚀 Features

- Product list and category browsing  
- Product detail pages  
- Shopping cart (add / remove products)  
- Django admin panel for product management  
- Responsive frontend templates  

---

## 🛠 Technology Stack

- Python 3  
- Django  
- HTML / CSS  
- SQLite (development database)  

---

## 📁 Project Structure

myshop/
│
├── myshop/ # Django project config (settings, urls)
├── shop/ # Main application (models, views, templates)
│
├── manage.py
├── README.md # <-- this file
├── requirements.txt
├── .gitignore
└── screenshots/

yaml
Copy code

---

## ⚙️ Installation & Setup

### 1. Clone repository

```bash
git clone https://github.com/Jasmindelic80/myshop.git
cd myshop
2. Create virtual environment
Windows:

bash
Copy code
python -m venv venv
venv\Scripts\activate
Linux/Mac:

bash
Copy code
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
bash
Copy code
pip install -r requirements.txt
4. Apply migrations
bash
Copy code
python manage.py migrate
5. Create admin user
bash
Copy code
python manage.py createsuperuser
6. Run development server
bash
Copy code
python manage.py runserver
Open in browser:
http://127.0.0.1:8000/

Admin panel:
http://127.0.0.1:8000/admin/

📸 Screenshots
Add screenshots to /screenshots folder and display them here:

home.png
cart.png
admin.png
pay.png
pay2.png

🎯 Portfolio Purpose
This project demonstrates:

Django MVC / MVT structure

CRUD functionality

Admin usage and backend logic

Clean project organization

It serves as a foundation for real-world ecommerce platforms or small business websites.

📝 Next Steps / Improvements
Optional improvements to enhance the project:

User authentication (login/register)

Order and checkout process

Payment integration (Stripe / PayPal)

Product search/filter, pagination, categories

REST API (via Django REST Framework)

Static/media file handling (images for products)

Docker + production-ready settings

📧 Contact
Open for freelance work & collaboration.

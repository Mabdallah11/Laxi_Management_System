# 🏢 Laxi Management System

A Django-based property management system with role-based login for **Manager** and **Tenant**.

---

## 🚀 Features
- Separate login for **Manager** and **Tenant**
- Manager dashboard
- Tenant dashboard
- Role-based authentication
- Logout functionality

---

## 🛠️ Requirements

Make sure you have installed:

- [Python 3.13+](https://www.python.org/downloads/)
- [Django 5.2+](https://www.djangoproject.com/download/)
- Virtual environment (`venv`)

---

## ⚙️ Installation & Setup

1. **Clone the repo**:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

python -m venv venv

venv\Scripts\activate

source venv/bin/activate

pip install -r requirements.txt

📦 Running the Project

Run migrations:

python manage.py migrate


Create a superuser (Manager):

python manage.py createsuperuser


Run the development server:

python manage.py runserver


Visit:
👉 Manager Login: http://127.0.0.1:8000/accounts/login/?role=manager
👉 Tenant Login: http://127.0.0.1:8000/accounts/login/?role=tenant


# NuraStore 🛒

[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-API%20First-red)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**NuraStore** is a robust, API-first E-commerce platform tailored for the **Northern Nigerian market**. 

Built with **Django** and **Django Rest Framework**, it solves specific local challenges including state-based delivery logistics (Kano vs. Abuja pricing), hybrid payment systems (Paystack + Payment on Delivery), and a trust-driven review system.

## 🚀 Features

### Core Experience
* **Dynamic Product Catalog:** Filter by category, price, and search terms instantly.
* **Smart Cart System:** Server-side validation with session management.
* **Localized Logistics:** Delivery fees calculated based on distance from Kano (HQ).
* **Checkout:** Integrated **Paystack** payment gateway & Cash on Delivery (POD) support.

### User & Trust
* **User Profiles:** Order history, address management, and saved preferences.
* **Verified Reviews:** Only users who purchased an item can leave a rating (1-5 stars).
* **Mobile-Ready UI:** Responsive frontend built with Vanilla JS and Bootstrap 5.

### Developer & Admin
* **API-First Architecture:** Complete separation of concerns. Ready for Mobile App integration.
* **Business Dashboard:** Custom admin command center for sales tracking and inventory alerts.
* **Documentation:** Integrated Swagger/OpenAPI docs.

## 🛠 Tech Stack

* **Backend:** Python, Django, Django Rest Framework (DRF)
* **Frontend:** HTML5, Bootstrap 5, Vanilla JavaScript (Fetch API)
* **Database:** SQLite (Dev) / PostgreSQL (Prod ready)
* **Payments:** Paystack API
* **Documentation:** drf-spectacular (OpenAPI 3.0)

## 📦 Installation Guide

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/nuramustaphaali/nurastore.git](https://github.com/nuramustaphaali/nurastore.git)
    cd nurastore
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Create Superuser (Admin)**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run Server**
    ```bash
    python manage.py runserver
    ```

Visit `http://127.0.0.1:8000` to browse the store.

## 📖 API Documentation

The API is fully documented. Once the server is running, visit:

* **Swagger UI (Interactive):** `http://127.0.0.1:8000/api/docs/`
* **Redoc (Reference):** `http://127.0.0.1:8000/api/redoc/`

## 📸 Screenshots

*(Home page, Product Page, and Admin Dashboard hre)e*

## 🤝 Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Built with ❤️ in Kano, Nigeria by Nura Mustapha Ali.**
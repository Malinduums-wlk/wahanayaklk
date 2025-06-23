# Vehicle Selling Ads Website

A web application that allows users to post and manage vehicle selling advertisements. Built with Django, HTML, CSS, and JavaScript.

## Features

- User authentication and authorization
- Vehicle ad posting with images
- Admin dashboard for site management
- Search and filter functionality
- Responsive design

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `vehicle_ads/` - Main project directory
  - `core/` - Main Django app
  - `users/` - User authentication app
  - `ads/` - Vehicle advertisements app
  - `static/` - Static files (CSS, JS, images)
  - `templates/` - HTML templates
  - `media/` - User uploaded files

## Technologies Used

- Django 5.0.2
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- SQLite (development) / PostgreSQL (production) 
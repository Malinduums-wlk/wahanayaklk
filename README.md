# Vehicle Selling Ads Website

A web application that allows users to post and manage vehicle selling advertisements. Built with Django, HTML, CSS, and JavaScript.

## Features

- User authentication and authorization
- Vehicle ad posting with images
- Admin dashboard for site management
- Search and filter functionality
- Responsive design

## Environment Setup

1. Create a `.env` file in the project root:
```bash
cp env_example.txt .env
```

2. Edit the `.env` file with your actual values:
   - Set your database credentials
   - Add your email password
   - Configure Bunny.net storage settings (if using)
   - Update allowed hosts for your domain

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

4. Set up your environment variables (see Environment Setup above)

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Load initial data (optional):
```bash
python manage.py loaddata database_backup.json
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
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
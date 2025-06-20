# Dental Lab Management System

A comprehensive web application for managing a dental laboratory, including appointments, orders, materials, and services.

## Features

- **User Management**
  - User registration and authentication
  - Profile management with password updates
  - Role-based access control (Admin and User roles)

- **Patient Services**
  - Appointment scheduling and management
  - Service catalog and information
  - Responsive, modern UI with animations and visual feedback

- **Inventory Management**
  - Product catalog and ordering
  - Materials inventory with stock tracking
  - Stock adjustment with reason tracking

- **Admin Dashboard**
  - Comprehensive admin panel for monitoring appointments and orders
  - User management interface
  - Material management with advanced filtering and search
  - Real-time statistics and data visualization

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Additional Libraries**: Flask-SQLAlchemy, WTForms, PyMySQL

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/dental-lab.git
cd dental-lab
```

2. Install required packages:
```
pip install flask flask-sqlalchemy flask-wtf pymysql
```

3. Set up the MySQL database:
```
python setup_mysql.py
```
Follow the prompts to enter your MySQL credentials.

4. Run the Flask application:
```
python flask_dental_lab.py
```

5. Access the application at: http://127.0.0.1:5000

## Directory Structure

```
dental-lab/
├── flask_dental_lab.py      # Main Flask application
├── static/                  # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css        # Custom CSS
│   └── images/              # Image files
├── templates/               # HTML templates
│   ├── admin/               # Admin panel templates
│   │   ├── dashboard.html   # Admin dashboard
│   │   ├── materials.html   # Materials management
│   │   ├── users.html       # User management
│   │   ├── orders.html      # Order management
│   │   └── appointments.html # Appointment management
│   ├── base.html            # Base template with layout
│   ├── index.html           # Homepage
│   ├── dashboard.html       # User dashboard
│   ├── profile.html         # User profile management
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── about.html           # About page
│   ├── orders.html          # Order form
│   ├── appointments.html    # Appointment booking
│   ├── products.html        # Product catalog
│   └── services.html        # Services information
├── dental_lab_db.sql        # Database schema SQL
├── user_table.sql           # User table schema SQL
└── setup_mysql.py           # Database setup script
```

## Database Schema

The application uses the following tables:
- `user`: For user authentication and role management
- `appointment`: For storing appointment details
- `material`: For managing materials inventory
- `order`: For tracking customer orders
- `service`: For storing service information

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. # DentalLab
# Dental

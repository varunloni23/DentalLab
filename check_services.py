from flask_dental_lab import app, Service

with app.app_context():
    services = Service.query.all()
    print(f"Found {len(services)} services")
    for service in services:
        print(f"ID: {service.id}, Title: {service.title}")
        print(f"Features: {repr(service.features)}")
        print("-" * 40) 
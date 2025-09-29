import click
from flask.cli import AppGroup
from datetime import datetime, timezone
from App.database import db, get_migrate
from App.main import create_app
from App.models import User, Driver, Resident, Street, Route, StopRequest, Notification

# Create Flask app
app = create_app()
migrate = get_migrate(app)

# --- SYSTEM COMMANDS --- #

init_cli = AppGroup('init', help='Database initialization commands') 

@init_cli.command('db', help="Initialize and seed the database")
def init_db():
    db.drop_all()
    db.create_all()
    
    # Seed Streets
    main_street = Street(name="Main Street")
    oak_street = Street(name="Oak Avenue")
    db.session.add_all([main_street, oak_street])
    db.session.flush()  # This ensures we get the IDs
    
    # Create users using our new models directly (bypassing the old controller)
    driver1 = Driver(username="alice_driver", password="alice123", name="Alice Driver")
    driver2 = Driver(username="bob_driver", password="bob123", name="Bob Driver")
    resident1 = Resident(username="john_resident", password="john123", name="John Resident", street=main_street)
    resident2 = Resident(username="mary_resident", password="mary123", name="Mary Resident", street=oak_street)
    
    # Also create the old 'bob' user for compatibility with existing controllers
    resident_bob = Resident(username="bob", password="bobpass", name="Bob", street=main_street)
    
    db.session.add_all([driver1, driver2, resident1, resident2, resident_bob])
    db.session.commit()
    
    # Create a sample route
    route = Route(driver_id=driver1.id, street_id=main_street.street_id, scheduled_time=datetime.now(timezone.utc), status="scheduled")
    db.session.add(route)
    db.session.commit()
    
    print(" ✅ Database initialized and seeded with sample data")

app.cli.add_command(init_cli)

# --- DRIVER COMMANDS --- #

driver_cli = AppGroup("driver", help="Driver-related commands")

@driver_cli.command("list", help="List all drivers")
def list_drivers():
    drivers = Driver.query.all()
    print(" 🚗 Drivers:")
    for driver in drivers:
        print(f"   ID: {driver.id}, Username: {driver.username}, Name: {driver.name}, Status: {driver.status}")

@driver_cli.command("create", help="Create a new driver")
@click.argument("username")
@click.argument("password")
@click.argument("name")
def create_driver(username, password, name):
    driver = Driver(username=username, password=password, name=name)
    db.session.add(driver)
    db.session.commit()
    print(f" ✅ Driver '{username}' created!")

@driver_cli.command("schedule", help="Schedule a route for a driver")
@click.argument("driver_id", type=int)
@click.argument("street_id", type=int)
def schedule_route(driver_id, street_id):
    driver = Driver.query.get(driver_id)
    street = Street.query.get(street_id)
    
    if not driver:
        print(f" ❌ Driver with ID {driver_id} not found")
        return
    if not street:
        print(f" ❌ Street with ID {street_id} not found")
        return
    
    route = Route(driver_id=driver.id, street_id=street.street_id, scheduled_time=datetime.now(timezone.utc), status="scheduled")
    db.session.add(route)
    
    # Notify all residents of that street
    residents = Resident.query.filter_by(street_id=street.street_id).all()
    for resident in residents:
        notification = Notification(
            resident_id=resident.id, 
            route_id=route.route_id, 
            message=f"Driver {driver.name} scheduled to visit {street.name} at {route.scheduled_time}"
        )
        db.session.add(notification)
    
    db.session.commit()
    print(f" ✅ Driver {driver.name} scheduled route to {street.name}")

app.cli.add_command(driver_cli)

# --- RESIDENT COMMANDS --- #

resident_cli = AppGroup("resident", help="Resident-related commands")

@resident_cli.command("list", help="List all residents")
def list_residents():
    residents = Resident.query.all()
    print(" 🏠 Residents:")
    for resident in residents:
        street_name = resident.street.name if resident.street else 'None'
        print(f"   ID: {resident.id}, Username: {resident.username}, Name: {resident.name}, Street: {street_name}")

@resident_cli.command("create", help="Create a new resident")
@click.argument("username")
@click.argument("password")
@click.argument("name")
@click.argument("street_id", type=int)
def create_resident(username, password, name, street_id):
    street = Street.query.get(street_id)
    if not street:
        print(f" ❌ Street with ID {street_id} not found")
        return
    
    resident = Resident(username=username, password=password, name=name, street=street)
    db.session.add(resident)
    db.session.commit()
    print(f" ✅ Resident '{username}' created!")

@resident_cli.command("inbox", help="View a resident's notifications")
@click.argument("resident_id", type=int)
def inbox(resident_id):
    resident = Resident.query.get(resident_id)
    if not resident:
        print(f" ❌ Resident with ID {resident_id} not found")
        return
    
    print(f" 📬 Notifications for {resident.name}:")
    if not resident.notifications:
        print("   No notifications")
    for notification in resident.notifications:
        print(f"   [{notification.timestamp}] {notification.message}")

@resident_cli.command("request-stop", help="Request a stop for a route")
@click.argument("resident_id", type=int)
@click.argument("route_id", type=int)
@click.argument("notes", default="Need bread")
def request_stop(resident_id, route_id, notes):
    resident = Resident.query.get(resident_id)
    route = Route.query.get(route_id)
    
    if not resident:
        print(f" ❌ Resident with ID {resident_id} not found")
        return
    if not route:
        print(f" ❌ Route with ID {route_id} not found")
        return
    
    stop_request = StopRequest(resident_id=resident.id, route_id=route.route_id, notes=notes)
    db.session.add(stop_request)
    
    # Notify driver
    driver = Driver.query.get(route.driver_id)
    notification = Notification(
        resident_id=resident.id, 
        route_id=route.route_id, 
        message=f"Stop requested on {route.street.name} by {resident.name}. Notes: {notes}"
    )
    db.session.add(notification)
    
    db.session.commit()
    print(f" ✅ {resident.name} requested stop on {route.street.name}")

@resident_cli.command("driver-status", help="View driver status and location")
@click.argument("driver_id", type=int)
def driver_status(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        print(f" ❌ Driver with ID {driver_id} not found")
        return
    
    route = Route.query.filter_by(driver_id=driver.id).first()
    if route:
        print(f" 🚗 Driver {driver.name}:")
        print(f"   Status: {driver.status}")
        print(f"   Location: {driver.location}")
        print(f"   Active Route: {route.street.name} at {route.scheduled_time}")
    else:
        print(f" 🚗 Driver {driver.name}:")
        print(f"   Status: {driver.status}")
        print(f"   Location: {driver.location}")
        print("   No active routes")

app.cli.add_command(resident_cli)

# --- STREET COMMANDS --- #

street_cli = AppGroup("street", help="Street-related commands")

@street_cli.command("list", help="List all streets")
def list_streets():
    streets = Street.query.all()
    print(" 🛣️  Streets:")
    for street in streets:
        print(f"   ID: {street.street_id}, Name: {street.name}")

@street_cli.command("create", help="Create a new street")
@click.argument("name")
def create_street(name):
    street = Street(name=name)
    db.session.add(street)
    db.session.commit()
    print(f" ✅ Street '{name}' created!")

app.cli.add_command(street_cli)

if __name__ == "__main__":
    app.run()
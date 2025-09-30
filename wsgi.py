import click
from flask.cli import AppGroup
from datetime import datetime, timezone, timedelta
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
    
    # --- 1. Seed Streets (6 Streets) ---
    print(" 1. Seeding Streets...")
    streets_data = [
        "Main Street", "Oak Avenue", "Cedar Lane", "Willow Drive", 
        "Pine Close", "Elm Road"
    ]
    streets = [Street(name=name) for name in streets_data]
    db.session.add_all(streets)
    db.session.flush() 
    
    # Map for easy access
    s_main, s_oak, s_cedar, s_willow, s_pine, s_elm = streets
    
    # --- 2. Seed Drivers (6 Drivers) ---
    print(" 2. Seeding Drivers...")
    drivers = [
        # Driver 1: Alice - Active on a route
        Driver(username="alice_driver", password="alice123", name="Alice Driver", 
               status="on_route", location="Near Main Street Park"),
        # Driver 2: Bob - Available
        Driver(username="bob_driver", password="bob123", name="Bob Baker", 
               status="available", location="Depot"),
        # Driver 3: Charlie - On break
        Driver(username="charlie_van", password="charpass", name="Charlie's Crumb", 
               status="on_break", location="Cafe"),
        # Driver 4: David - Scheduled for later
        Driver(username="david_van", password="davidpass", name="David's Delight", 
               status="available", location="Depot"),
        # Driver 5: Eve - On route, but not visible
        Driver(username="eve_driver", password="evepass", name="Eve's Eats", 
               status="on_route", location="Tracking disabled"),
        # Driver 6: Frank - Offline
        Driver(username="frank_driver", password="frankpass", name="Frank's Fresh", 
               status="offline", location="None"),
    ]
    db.session.add_all(drivers)
    db.session.flush()
    
    d_alice, d_bob, d_charlie, d_david, d_eve, d_frank = drivers
    
    # --- 3. Seed Residents (10 Residents) ---
    print(" 3. Seeding Residents...")
    residents = [
        Resident(username="john_main", password="john123", name="John Resident", street=s_main),
        Resident(username="mary_oak", password="mary123", name="Mary Resident", street=s_oak),
        Resident(username="sara_oak", password="sarapass", name="Sara Lee", street=s_oak),
        Resident(username="bob", password="bobpass", name="Bob The Baker", street=s_main), # Old user for compatibility
        Resident(username="tim_cedar", password="timpass", name="Tim Ceder", street=s_cedar),
        Resident(username="anna_cedar", password="annapass", name="Anna Cornwell", street=s_cedar),
        Resident(username="willow_res", password="willpass", name="Will Lowe", street=s_willow),
        Resident(username="penny_pine", password="penpass", name="Penny Pine", street=s_pine),
        Resident(username="luke_elm", password="lukepass", name="Luke Elm", street=s_elm),
        Resident(username="greg_main", password="gregpass", name="Greg Mainman", street=s_main),
    ]
    db.session.add_all(residents)
    db.session.flush()
    
    r_john, r_mary, r_sara, r_bob, r_tim, r_anna, r_will, r_penny, r_luke, r_greg = residents
    
    # --- 4. Seed Routes (5 Routes) ---
    print(" 4. Seeding Routes...")
    now = datetime.now(timezone.utc)
    routes = [
        # Route 1: Alice on Main - Active, will get a stop request
        Route(driver_id=d_alice.id, street_id=s_main.street_id, 
              scheduled_time=now - timedelta(minutes=30), status="in_progress"),
        # Route 2: Bob on Oak - Scheduled for later
        Route(driver_id=d_bob.id, street_id=s_oak.street_id, 
              scheduled_time=now + timedelta(hours=2), status="scheduled"),
        # Route 3: Charlie on Cedar - Completed
        Route(driver_id=d_charlie.id, street_id=s_cedar.street_id, 
              scheduled_time=now - timedelta(hours=4), status="completed"),
        # Route 4: David on Willow - Scheduled for tomorrow
        Route(driver_id=d_david.id, street_id=s_willow.street_id, 
              scheduled_time=now + timedelta(days=1), status="scheduled"),
        # Route 5: Eve on Pine - Scheduled
        Route(driver_id=d_eve.id, street_id=s_pine.street_id, 
              scheduled_time=now + timedelta(minutes=45), status="scheduled"),
    ]
    db.session.add_all(routes)
    db.session.flush()
    
    rt_alice_main, rt_bob_oak, rt_charlie_cedar, rt_david_willow, rt_eve_pine = routes
    
    # --- 5. Seed Stop Requests (5 Stop Requests) ---
    print(" 5. Seeding Stop Requests...")
    stop_requests = [
        # SR 1: John on Main (Route 1) - Pending
        StopRequest(resident_id=r_john.id, route_id=rt_alice_main.route_id, 
                    quantity=3, notes="3 croissants needed!", status="requested"),
        # SR 2: Sara on Oak (Route 2) - Confirmed, waiting for route
        StopRequest(resident_id=r_sara.id, route_id=rt_bob_oak.route_id, 
                    quantity=1, notes="Sourdough for sure.", status="confirmed"),
        # SR 3: Tim on Cedar (Route 3) - Cancelled (Driver completed already)
        StopRequest(resident_id=r_tim.id, route_id=rt_charlie_cedar.route_id, 
                    quantity=None, notes="Missed the van, requesting a stop!", status="cancelled"),
        # SR 4: Penny on Pine (Route 5) - Pending
        StopRequest(resident_id=r_penny.id, route_id=rt_eve_pine.route_id, 
                    quantity=5, notes="Loaf and 4 rolls. Please call first.", status="requested"),
        # SR 5: Greg on Main (Route 1) - Confirmed, urgent
        StopRequest(resident_id=r_greg.id, route_id=rt_alice_main.route_id, 
                    quantity=2, notes="2 baguettes. Urgent!", status="confirmed"),
    ]
    db.session.add_all(stop_requests)
    
    # --- 6. Seed Notifications (10 Notifications) ---
    print(" 6. Seeding Notifications...")
    notifications = [
        # Notif 1 (Resident: John, Route: 1) - Initial Schedule Alert
        Notification(resident_id=r_john.id, route_id=rt_alice_main.route_id, 
                     message=f"Driver {d_alice.name} scheduled to visit {s_main.name} now!"),
        # Notif 2 (Resident: Mary, Route: 2) - Initial Schedule Alert
        Notification(resident_id=r_mary.id, route_id=rt_bob_oak.route_id, 
                     message=f"Driver {d_bob.name} scheduled for {s_oak.name} at {rt_bob_oak.scheduled_time.strftime('%H:%M')}."),
        # Notif 3 (Resident: Sara, Route: 2) - Initial Schedule Alert
        Notification(resident_id=r_sara.id, route_id=rt_bob_oak.route_id, 
                     message=f"New route for {s_oak.name} tomorrow."),
        # Notif 4 (Driver: Alice, Route: 1) - Stop Request Alert
        Notification(resident_id=d_alice.id, route_id=rt_alice_main.route_id, 
                     message=f"Stop requested on {s_main.name} by {r_john.name}. Notes: 3 croissants needed!"),
        # Notif 5 (Driver: Alice, Route: 1) - Another Stop Request Alert
        Notification(resident_id=d_alice.id, route_id=rt_alice_main.route_id, 
                     message=f"Stop requested on {s_main.name} by {r_greg.name}. Notes: 2 baguettes. Urgent!"),
        # Notif 6 (Resident: John, Route: 1) - Driver Near Alert
        Notification(resident_id=r_john.id, route_id=rt_alice_main.route_id, 
                     message=f"Driver {d_alice.name} is 5 minutes away from {s_main.name}!"),
        # Notif 7 (Resident: Will, Route: 4) - Initial Schedule Alert
        Notification(resident_id=r_will.id, route_id=rt_david_willow.route_id, 
                     message=f"Route scheduled for {s_willow.name} tomorrow."),
        # Notif 8 (Resident: Mary, Route: 2) - Route Status Update
        Notification(resident_id=r_mary.id, route_id=rt_bob_oak.route_id, 
                     message=f"Route for {s_oak.name} is delayed by 15 mins."),
        # Notif 9 (Resident: Penny, Route: 5) - Stop Request Confirmation
        Notification(resident_id=r_penny.id, route_id=rt_eve_pine.route_id, 
                     message=f"Your stop request on {s_pine.name} has been confirmed."),
        # Notif 10 (Resident: Tim, Route: 3) - Cancellation Notice
        Notification(resident_id=r_tim.id, route_id=rt_charlie_cedar.route_id, 
                     message=f"Driver {d_charlie.name} has cancelled the route to {s_cedar.name}."),
    ]
    db.session.add_all(notifications)
    
    db.session.commit()
    print(" Database initialized and seeded with 6 Drivers, 6 Streets, 10 Residents, 5 Routes, 5 Stop Requests, and 10 Notifications.")
app.cli.add_command(init_cli)

# --- DRIVER COMMANDS --- #

driver_cli = AppGroup("driver", help="Driver-related commands")

@driver_cli.command("list", help="List all drivers")
def list_drivers():
    drivers = Driver.query.all()
    print(" Drivers:")
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
    print(f" Driver '{username}' created!")

@driver_cli.command("schedule", help="Schedule a route for a driver")
@click.argument("driver_id", type=int)
@click.argument("street_id", type=int)
def schedule_route(driver_id, street_id):
    driver = Driver.query.get(driver_id)
    street = Street.query.get(street_id)
    
    if not driver:
        print(f" Driver with ID {driver_id} not found")
        return
    if not street:
        print(f" Street with ID {street_id} not found")
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
    print(f" Driver {driver.name} scheduled route to {street.name}")

app.cli.add_command(driver_cli)

# --- RESIDENT COMMANDS --- #

resident_cli = AppGroup("resident", help="Resident-related commands")

@resident_cli.command("list", help="List all residents")
def list_residents():
    residents = Resident.query.all()
    print(" Residents:")
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
        print(f" Street with ID {street_id} not found")
        return
    
    resident = Resident(username=username, password=password, name=name, street=street)
    db.session.add(resident)
    db.session.commit()
    print(f" Resident '{username}' created!")

@resident_cli.command("inbox", help="View a resident's notifications")
@click.argument("resident_id", type=int)
def inbox(resident_id):
    resident = Resident.query.get(resident_id)
    if not resident:
        print(f" Resident with ID {resident_id} not found")
        return
    
    print(f" Notifications for {resident.name}:")
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
        print(f" Resident with ID {resident_id} not found")
        return
    if not route:
        print(f" Route with ID {route_id} not found")
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
    print(f" {resident.name} requested stop on {route.street.name}")

@resident_cli.command("driver-status", help="View driver status and location")
@click.argument("driver_id", type=int)
def driver_status(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        print(f" Driver with ID {driver_id} not found")
        return
    
    route = Route.query.filter_by(driver_id=driver.id).first()
    if route:
        print(f" Driver {driver.name}:")
        print(f"   Status: {driver.status}")
        print(f"   Location: {driver.location}")
        print(f"   Active Route: {route.street.name} at {route.scheduled_time}")
    else:
        print(f" Driver {driver.name}:")
        print(f"   Status: {driver.status}")
        print(f"   Location: {driver.location}")
        print("   No active routes")

app.cli.add_command(resident_cli)

# --- STREET COMMANDS --- #

street_cli = AppGroup("street", help="Street-related commands")

@street_cli.command("list", help="List all streets")
def list_streets():
    streets = Street.query.all()
    print(" Streets:")
    for street in streets:
        print(f"   ID: {street.street_id}, Name: {street.name}")

@street_cli.command("create", help="Create a new street")
@click.argument("name")
def create_street(name):
    street = Street(name=name)
    db.session.add(street)
    db.session.commit()
    print(f" Street '{name}' created!")

app.cli.add_command(street_cli)

if __name__ == "__main__":
    app.run()

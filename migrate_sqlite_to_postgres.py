from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import db, NormalUser, Administrator, Record, Media
from dotenv import load_dotenv
import os

load_dotenv()

SQLITE_DB_URL = "sqlite:///instance/jiseti.db"  
POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")

if not POSTGRES_DB_URL:
    raise ValueError("POSTGRES_DB_URL is not set in environment variables")

print(f"SQLite URL: {SQLITE_DB_URL}")
print(f"PostgreSQL URL: {POSTGRES_DB_URL}")


sqlite_engine = create_engine(SQLITE_DB_URL)
postgres_engine = create_engine(POSTGRES_DB_URL)


with sqlite_engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()
    print("Available tables in SQLite:", [table[0] for table in tables])


SQLiteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)

sqlite_session = SQLiteSession()
postgres_session = PostgresSession()

# --- Step 1: Create PostgreSQL Tables ---
try:
    print("Creating PostgreSQL tables...")
    db.metadata.create_all(postgres_engine)
    print("✅ PostgreSQL tables created successfully")
except Exception as e:
    print(f"❌ Error creating PostgreSQL tables: {e}")
    exit(1)


print("\nChecking existing data in PostgreSQL...")
existing_users = postgres_session.query(NormalUser).count()
existing_admins = postgres_session.query(Administrator).count()
existing_records = postgres_session.query(Record).count()
existing_media = postgres_session.query(Media).count()

print(f"Existing data in PostgreSQL:")
print(f"  - Normal Users: {existing_users}")
print(f"  - Administrators: {existing_admins}")
print(f"  - Records: {existing_records}")
print(f"  - Media: {existing_media}")

if existing_users > 0 or existing_admins > 0 or existing_records > 0 or existing_media > 0:
    print("\n⚠️  PostgreSQL database already contains data!")
    choice = input("Do you want to:\n1. Clear existing data and migrate (c)\n2. Skip duplicate records (s)\n3. Cancel migration (x)\nEnter choice (c/s/x): ").lower()
    
    if choice == 'c':
        print("Clearing existing data...")
        postgres_session.query(Media).delete()
        postgres_session.query(Record).delete()
        postgres_session.query(Administrator).delete()
        postgres_session.query(NormalUser).delete()
        postgres_session.commit()
        print("✅ Existing data cleared")
    elif choice == 's':
        print("Will skip duplicate records during migration...")
    else:
        print("Migration cancelled.")
        sqlite_session.close()
        postgres_session.close()
        exit(0)


try:
    total_migrated = 0
    
    
    print("\nMigrating Normal Users...")
    users = sqlite_session.query(NormalUser).all()
    print(f"Found {len(users)} normal users")
    
    for user in users:
        
        existing_user = postgres_session.query(NormalUser).filter_by(id=user.id).first()
        if existing_user and choice == 's':
            print(f"  - Skipping user: {user.name} ({user.email}) - already exists")
            continue
            
        new_user = NormalUser(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password
        )
        postgres_session.add(new_user)
        print(f"  - Migrating user: {user.name} ({user.email})")
    
    total_migrated += len(users)
    
    
    print("\nMigrating Administrators...")
    admins = sqlite_session.query(Administrator).all()
    print(f"Found {len(admins)} administrators")
    
    for admin in admins:
    
        existing_admin = postgres_session.query(Administrator).filter_by(id=admin.id).first()
        if existing_admin and choice == 's':
            print(f"  - Skipping admin: {admin.name} ({admin.email}) - already exists")
            continue
            
        new_admin = Administrator(
            id=admin.id,
            name=admin.name,
            email=admin.email,
            password=admin.password,
            admin_number=admin.admin_number
        )
        postgres_session.add(new_admin)
        print(f"  - Migrating admin: {admin.name} ({admin.email})")
    
    total_migrated += len(admins)
    
    
    print("\nMigrating Records...")
    records = sqlite_session.query(Record).all()
    print(f"Found {len(records)} records")
    
    for record in records:
        
        existing_record = postgres_session.query(Record).filter_by(id=record.id).first()
        if existing_record and choice == 's':
            print(f"  - Skipping record: {record.title} - already exists")
            continue
            
        new_record = Record(
            id=record.id,
            type=record.type,
            title=record.title,
            description=record.description,
            status=record.status,
            latitude=record.latitude,
            longitude=record.longitude,
            created_at=record.created_at,
            normal_user_id=record.normal_user_id
        )
        postgres_session.add(new_record)
        print(f"  - Migrating record: {record.title}")
    
    total_migrated += len(records)
    
    
    print("\nMigrating Media...")
    media_items = sqlite_session.query(Media).all()
    print(f"Found {len(media_items)} media items")
    
    for media in media_items:
    
        existing_media = postgres_session.query(Media).filter_by(id=media.id).first()
        if existing_media and choice == 's':
            print(f"  - Skipping media: {media.id} - already exists")
            continue
            
        new_media = Media(
            id=media.id,
            image_url=media.image_url,
            video_url=media.video_url,
            record_id=media.record_id
        )
        postgres_session.add(new_media)
        print(f"  - Migrating media: {media.id}")
    
    total_migrated += len(media_items)
    
    print(f"\nTotal items to migrate: {total_migrated}")

except Exception as e:
    print(f"❌ Error during data migration: {e}")
    postgres_session.rollback()
    sqlite_session.close()
    postgres_session.close()
    exit(1)


try:
    postgres_session.commit()
    print("\n✅ Data migration completed successfully!")
    print(f"📊 Summary:")
    print(f"  - {len([u for u in users if not (postgres_session.query(NormalUser).filter_by(id=u.id).first() and choice == 's')])} normal users migrated")
    print(f"  - {len([a for a in admins if not (postgres_session.query(Administrator).filter_by(id=a.id).first() and choice == 's')])} administrators migrated") 
    print(f"  - {len([r for r in records if not (postgres_session.query(Record).filter_by(id=r.id).first() and choice == 's')])} records migrated")
    print(f"  - {len([m for m in media_items if not (postgres_session.query(Media).filter_by(id=m.id).first() and choice == 's')])} media items migrated")
    
except Exception as e:
    print(f"❌ Error during commit: {e}")
    postgres_session.rollback()
    
finally:
    sqlite_session.close()
    postgres_session.close()
    print("\n🔒 Database connections closed")
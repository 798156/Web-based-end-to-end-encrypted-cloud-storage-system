from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Check if column exists
        try:
            # Attempt to query the new column to see if it exists
            db.session.execute(text("SELECT avatar FROM user LIMIT 1"))
            print("Column 'avatar' already exists.")
        except Exception:
            print("Adding 'avatar' column to 'user' table...")
            try:
                # Add avatar column
                db.session.execute(text("ALTER TABLE user ADD COLUMN avatar VARCHAR(255) DEFAULT 'default-avatar.png'"))
                db.session.commit()
                print("Migration successful.")
            except Exception as e:
                print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()

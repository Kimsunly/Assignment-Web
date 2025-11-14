"""Quick script to recreate database with updated schema"""
import os
os.environ['RECREATE_DB'] = 'true'

# This will trigger database recreation when app is imported
import app

print("✅ Database recreation triggered! The app will recreate all tables on next run.")
print("   Now you can run: python app.py")


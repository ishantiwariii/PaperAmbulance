from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from sqlalchemy import text
from app.db.session import engine, Base

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Automated Migration: Ensure missing columns exist
def run_migrations():
    with engine.connect() as conn:
        print("DEBUG: Checking/Running schema migrations...")
        try:
            # Add user_id to profiles if missing
            conn.execute(text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='profiles' AND column_name='user_id') THEN
                        ALTER TABLE profiles ADD COLUMN user_id INTEGER;
                        ALTER TABLE profiles ADD CONSTRAINT fk_profiles_user 
                            FOREIGN KEY (user_id) REFERENCES users(id);
                    END IF;
                END $$;
            """))
            # Add user_id to form_history if missing
            conn.execute(text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='form_history' AND column_name='user_id') THEN
                        ALTER TABLE form_history ADD COLUMN user_id INTEGER;
                        ALTER TABLE form_history ADD CONSTRAINT fk_form_history_user 
                            FOREIGN KEY (user_id) REFERENCES users(id);
                    END IF;
                END $$;
            """))
            conn.commit()
            print("DEBUG: Schema migration checks complete.")
        except Exception as e:
            print(f"DEBUG: Migration auto-run failed: {e}")

run_migrations()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Technical Note: PaperAmbulance Backend Architecture 🚑

This document outlines the technical responsibilities of each component in the PaperAmbulance backend.

---

## 🏗️ System Architecture Overview
The backend is built using **FastAPI** (Python), designed to be a stateless, high-performance engine that orchestrates AI reasoning and secure data storage.
- **AI Engine**: Google Gemini 2.5 Flash via LangChain.
- **Database**: Neon (Serverless PostgreSQL).
- **Authentication**: Neon Auth (powered by Clerk).

---

## 📂 Component Breakdown

### 1. `app.core` (The Base)
- **`config.py`**: Uses Pydantic to validate environment variables (`DATABASE_URL`, `GOOGLE_API_KEY`, etc.). It ensures the server doesn't start if credentials are missing.
- **`security.py`**: The "Gatekeeper". It fetches JWKS from Neon Auth to verify that incoming requests have a valid login token. It maps the Clerk `sub` ID to our internal profiles.

### 2. `app.db` (The Data Layer)
- **`session.py`**: Manages the connection pool to NeonDB.
- **`models.py`**: 
    - `Profile`: Uses a **JSONB** column to store universal user data, allowing for flexible fields (Name, Aadhaar, etc.) without rigid schema changes.
    - `FormHistory`: Tracks every auto-fill event for user auditing.

### 3. `app.services` (The Brains)
- **`ai_service.py`**: 
    - `analyze_form_fields`: Uses Gemini to understand the *intent* of tech-heavy HTML fields.
    - `parse_voice_transcript`: A specialized prompt that extracts structured profile updates from natural speech (Hindi/English).
- **`pdf_service.py`**: Uses `ReportLab` to draw a professional application-style document from the raw profile data.

### 4. `app.api.v1` (The Interface)
- **`profiles.py`**: Handles CRUD (Create, Read, Update) for the user's universal identity.
- **`analyze.py`**: The endpoint for the Chrome Extension to request form field mapping.
- **`voice.py`**: Receives voice transcripts and returns the "understood" profile updates.
- **`export.py`**: Handles streaming the binary PDF file to the user's browser for download.

---

## 🔄 Core Workflow (The "Magic")
1. **Request**: Extension sends raw HTML field IDs.
2. **Analysis**: `ai_service` uses Gemini to map IDs to intents (e.g., `id="f_7"` -> `pan_number`).
3. **Retrieval**: Backend pulls the user's profile from NeonDB.
4. **Mapping**: `ai_service` matches the profile's `pan_number` to the specific field `id`.
5. **Logging**: `FormHistory` records the event.
6. **Response**: Extension receives a clean JSON map to auto-fill the browser.

# Frontend Design Note: PaperAmbulance Chrome Extension 🚑

This document outlines the architecture, UI/UX, and technical setup for the PaperAmbulance Chrome Extension (Manifest V3).

---

## 🏗️ Architecture Overview
The extension is divided into three main layers:
1. **Popup (React + Vite)**: The primary UI for user login, signup, and universal profile management.
2. **Content Scripts**: The "Surveillance" layer that runs on web pages to detect form fields and inject auto-fill data.
3. **Background Service Worker**: Handles communication with the FastAPI backend and manages the authentication state (Clerk).

---

## 🎨 Visual Identity & Mockups

````carousel
![Extension Login / Signup Screen](/C:/Users/ieish/.gemini/antigravity/brain/deced1e1-9acc-4e91-a385-0a89fd3dc795/extension_popup_mockup_auth_1776024141215.png)
<!-- slide -->
![Extension Dashboard & Form Detection](/C:/Users/ieish/.gemini/antigravity/brain/deced1e1-9acc-4e91-a385-0a89fd3dc795/extension_popup_mockup_dashboard_1776024161504.png)
````

### 🏠 Popup States
1. **Guest State**:
   - Clean, premium "Hero" section with the tagline: *"Duniya ka koi bhi form — PaperAmbulance bhar dega"*.
   - **Login / Signup** button that opens a Clerk hosted modal or uses the Clerk SDK for extensions.
2. **Authenticated State**:
   - **Profile Summary**: Quick view of filled vs. missing fields (Aadhaar: ✅, Income: ❌).
   - **Form Detector Status**: Indicator showing if a form is detected on the current active tab.
   - **Voice Toggle**: Button to start voice-to-profile extraction.

---

## 🎨 UI/UX Design (Visual Language)
- **Palette**: Sleek Dark Mode (Deep Charcoal `#121212`) with **Electric Blue** (`#007AFF`) and **Emergency Red** (`#FF3B30`) accents.
- **Typography**: `Inter` or `Outfit` (modern, sans-serif).
- **Animations**: Subtle pulsing "Detection" ring when scanning forms.

### 📦 Popup Mockup (Draft)
| Header | Description |
| :--- | :--- |
| **Navbar** | Logo 🚑 + User Settings Icon |
| **Status Card** | "Form Detected on *sarkari-result.com*" |
| **Action Button** | Large "Auto-Fill ⚡" Button |
| **Missing List** | ⚠️ *Missing: Income Certificate* |

---

## 🛠️ Components Breakdown

### 1. `extension/popup/`
- **`AuthGuard.tsx`**: High-order component that checks Clerk session.
- **`Dashboard.tsx`**: Main UI after login.
- **`VoiceRecorder.tsx`**: Integration with Web Speech API for Hindi voice input.

### 2. `extension/content/` (The "Injectors")
- **`DetectionEngine.ts`**: Runs on page load, finds inputs, sends raw labels/IDs to backend.
- **`FillEngine.ts`**: Receives mapping from backend and programmatically sets field values.

### 3. `extension/background/`
- **`AuthService.ts`**: Caches the JWT token and adds it to the `Authorization` header for all backend requests.

---

## 🔄 Interaction Flow
1. **User lands on a form page.**
2. **Content Script** scans the DOM and sends field metadata to the **Background Worker**.
3. **Background Worker** calls `POST /analyze/fill` on the FastAPI server with the user's token.
4. **Backend/AI** returns the `fill_map`.
5. **Content Script** injects values and highlights the filled fields in a subtle green glow.

---

## 📋 Recommended Tech Stack (Frontend)
- **Framework**: React 18 + Vite (TailwindCSS for rapid styling).
- **Auth**: `@clerk/chrome-extension`.
- **Icons**: Lucide-React.
- **Bundler**: CRXJS (best Vite plugin for Extensions).

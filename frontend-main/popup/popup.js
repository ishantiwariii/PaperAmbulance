// popup/popup.js

const BACKEND_URL = "https://paperambulance.onrender.com";
const AUTH_API_BASE = "https://paperambulance.onrender.com/api/v1/auth";

document.addEventListener("DOMContentLoaded", () => {
  // --- UI Elements ---
  const authSubmitBtn = document.getElementById("auth-submit-btn");
  const authToggleBtn = document.getElementById("auth-toggle-btn");
  const authTitle = document.getElementById("auth-title");
  const authSubtitle = document.getElementById("auth-subtitle");
  const authSubmitText = document.getElementById("auth-submit-text");
  const authNameInput = document.getElementById("auth-name");
  const authEmailInput = document.getElementById("auth-email");
  const authPasswordInput = document.getElementById("auth-password");
  const authToggleMsg = document.getElementById("auth-toggle-msg");

  const logoutBtn = document.getElementById("logout-btn");
  const guestView = document.getElementById("guest-view");
  const authView = document.getElementById("auth-view");
  const autoFillBtn = document.getElementById("autofill-btn");
  const formStatus = document.getElementById("form-status");
  const statusIndicator = document.querySelector(".status-indicator");
  const voiceBtn = document.getElementById("voice-btn");
  const transcriptionOutput = document.getElementById("transcription-output");
  const documentList = document.getElementById("document-list");

  let isSignupMode = false;

  // --- Auth Logic ---
  async function checkAuthState() {
    chrome.storage.local.get(["userToken", "isAuthenticated"], async (result) => {
      if (result.isAuthenticated && result.userToken) {
        guestView.classList.add("hidden");
        authView.classList.remove("hidden");
        await fetchProfileStatus(result.userToken);
        checkFormStatus();
      } else {
        guestView.classList.remove("hidden");
        authView.classList.add("hidden");
      }
    });
  }

  authToggleBtn.addEventListener("click", (e) => {
    e.preventDefault();
    isSignupMode = !isSignupMode;
    
    if (isSignupMode) {
      authTitle.innerText = "Join PaperAmbulance";
      authSubtitle.innerText = "Create your universal profile in seconds.";
      authSubmitText.innerText = "Create Account";
      authNameInput.classList.remove("hidden");
      authToggleMsg.innerText = "Already have an account?";
      authToggleBtn.innerText = "Sign In";
    } else {
      authTitle.innerText = "Welcome Back!";
      authSubtitle.innerText = "Login to sync your profile across devices.";
      authSubmitText.innerText = "Sign In";
      authNameInput.classList.add("hidden");
      authToggleMsg.innerText = "Don't have an account?";
      authToggleBtn.innerText = "Sign Up";
    }
  });

  authSubmitBtn.addEventListener("click", async () => {
    const email = authEmailInput.value.trim();
    const password = authPasswordInput.value.trim();
    const name = authNameInput.value.trim();

    if (!email || !password || (isSignupMode && !name)) {
      alert("Please fill in all fields.");
      return;
    }

    authSubmitBtn.disabled = true;
    authSubmitText.innerText = isSignupMode ? "Creating..." : "Signing In...";

    const endpoint = isSignupMode ? `${AUTH_API_BASE}/signup` : `${AUTH_API_BASE}/login`;
    const body = isSignupMode ? { email, password, name } : { email, password };

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      const result = await response.json();

      if (response.ok) {
        // Neon Auth returns a token in the 'token' or 'session' field
        const token = result.token || (result.session && result.session.token);
        if (token) {
          chrome.storage.local.set({ isAuthenticated: true, userToken: token }, () => {
            checkAuthState();
          });
        } else {
          // Handle cases where auth might be working but token is hidden in cookies
          // For now, we assume token is returned as per typical Standalone API
          chrome.storage.local.set({ isAuthenticated: true, userToken: "MOCK_TOKEN_SUCCESS" }, () => {
            checkAuthState();
          });
        }
      } else {
        alert(`Auth Error: ${result.message || "Invalid credentials"}`);
      }
    } catch (err) {
      console.error(err);
      alert("Connection failed. Is the backend or auth service down?");
    } finally {
      authSubmitBtn.disabled = false;
      authSubmitText.innerText = isSignupMode ? "Create Account" : "Sign In";
    }
  });

  async function fetchProfileStatus(token) {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/profiles/me`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (response.ok) {
        const profile = await response.json();
        updateUIWithProfile(profile.data);
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
    }
  }

  function updateUIWithProfile(data) {
    const listItems = documentList.querySelectorAll("li");
    listItems.forEach(li => {
      const key = li.getAttribute("data-key");
      const badge = li.querySelector(".badge");
      if (data && data[key]) {
        badge.innerText = "✅ Ready";
        badge.className = "badge success";
      } else {
        badge.innerText = "❌ Missing";
        badge.className = "badge error";
      }
    });
  }

  function logout() {
    chrome.storage.local.set({ isAuthenticated: false, userToken: null }, () => {
      checkAuthState();
    });
  }

  logoutBtn.addEventListener("click", logout);

  // --- Form Auto-Fill Trigger ---
  autoFillBtn.addEventListener("click", () => {
    autoFillBtn.innerHTML = "<span>⏳</span> Filling... ⚡";
    chrome.runtime.sendMessage({ action: "TRIGGER_AUTOFILL" });
    setTimeout(() => {
      autoFillBtn.innerHTML = "<span>⚡</span> Auto-Fill Form";
    }, 1500);
  });

  // --- Form Status Syncing ---
  function checkFormStatus() {
    chrome.runtime.sendMessage({ action: "GET_FORM_STATUS" }, (response) => {
      if (response && response.status === "detected") {
        formStatus.innerText = `Form Detected: ${response.data.url}`;
        statusIndicator.classList.remove("scanning");
        statusIndicator.style.backgroundColor = "var(--success-green)";
        statusIndicator.style.boxShadow = "0 0 10px var(--success-green)";
        autoFillBtn.disabled = false;
      } else {
        formStatus.innerText = "Scanning for forms...";
        statusIndicator.classList.add("scanning");
        statusIndicator.style.backgroundColor = "var(--accent-blue)";
        statusIndicator.style.boxShadow = "0 0 8px var(--accent-blue)";
        autoFillBtn.disabled = true;
      }
    });
  }

  // --- Voice Parser Logic ---
  async function processProfileUpdate(transcript) {
      chrome.storage.local.get(["userToken"], async (res) => {
          const token = res.userToken || "LOCAL_DEV_TOKEN";
          transcriptionOutput.classList.remove("hidden");
          transcriptionOutput.innerText = `Parsing Input: "${transcript}"...`;
          
          try {
              const parseRes = await fetch(`${BACKEND_URL}/api/v1/voice/parse`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                  body: JSON.stringify({ transcript })
              });
              const resData = await parseRes.json();
              const extracted = resData.understood;
              
              if (extracted && Object.keys(extracted).length > 0) {
                  transcriptionOutput.innerText = "Saving profile data...";
                  const saveRes = await fetch(`${BACKEND_URL}/api/v1/profiles/me`, {
                      method: "POST",
                      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                      body: JSON.stringify({ data: extracted })
                  });
                  if (saveRes.ok) {
                      transcriptionOutput.innerText = "✅ Profile updated in NeonDB!";
                      await fetchProfileStatus(token); // Refresh UI
                  }
              }
          } catch (err) {
              console.error(err);
              transcriptionOutput.innerText = "❌ Error connecting to backend.";
          }
      });
  }

  document.getElementById("manual-submit-btn").addEventListener("click", () => {
      const text = document.getElementById("manual-text").value.trim();
      if (!text) return;
      processProfileUpdate(text);
  });

  voiceBtn.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs || tabs.length === 0) return;
        const tabId = tabs[0].id;
        voiceBtn.innerHTML = "<span>🔴</span> Listening...";
        transcriptionOutput.classList.remove("hidden");
        transcriptionOutput.innerText = "Check your browser tab for the Mic prompt!";
        
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: () => {
                return new Promise((resolve) => {
                    if (!('webkitSpeechRecognition' in window)) {
                        resolve({ error: "Speech API not supported" });
                        return;
                    }
                    const recognition = new webkitSpeechRecognition();
                    recognition.lang = "hi-IN";
                    recognition.onresult = (e) => resolve({ transcript: e.results[0][0].transcript });
                    recognition.onerror = (e) => resolve({ error: e.error });
                    recognition.start();
                });
            }
        }, (results) => {
            voiceBtn.innerHTML = "<span>🎤</span> Voice Update (Hindi)";
            if (chrome.runtime.lastError || !results || !results[0]) {
                document.getElementById("manual-fallback").classList.remove("hidden");
                document.getElementById("manual-fallback").style.display = "flex";
                transcriptionOutput.innerText = "⚠️ Mic error. Try typing below.";
                return;
            }
            const res = results[0].result;
            if (res.error) {
                document.getElementById("manual-fallback").classList.remove("hidden");
                document.getElementById("manual-fallback").style.display = "flex";
                transcriptionOutput.innerText = `⚠️ Mic: ${res.error}`;
            } else if (res.transcript) {
                document.getElementById("manual-fallback").classList.add("hidden");
                document.getElementById("manual-fallback").style.display = "";
                processProfileUpdate(res.transcript);
            }
        });
    });
  });

  checkAuthState();
});

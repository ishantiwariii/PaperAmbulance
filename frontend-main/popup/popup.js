// popup/popup.js

let BACKEND_URL = "https://paperambulance.onrender.com";
let AUTH_API_BASE = "https://paperambulance.onrender.com/api/v1/auth";

document.addEventListener("DOMContentLoaded", () => {
    // --- Environment Setup ---
    const envSelect = document.getElementById("env-select");
    
    function updateBackendUrls(mode) {
        if (mode === "local") {
            BACKEND_URL = "http://127.0.0.1:8000";
            AUTH_API_BASE = "http://127.0.0.1:8000/api/v1/auth";
        } else {
            BACKEND_URL = "https://paperambulance.onrender.com";
            AUTH_API_BASE = "https://paperambulance.onrender.com/api/v1/auth";
        }
    }

    chrome.storage.local.get(["envMode"], (res) => {
        const mode = res.envMode || "prod";
        if (envSelect) envSelect.value = mode;
        updateBackendUrls(mode);
        checkAuthState(); // Initial check
    });

    if (envSelect) {
        envSelect.addEventListener("change", (e) => {
            const mode = e.target.value;
            chrome.storage.local.set({ envMode: mode }, () => {
                updateBackendUrls(mode);
                window.location.reload(); // Refresh to apply new URL
            });
        });
    }

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

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || "Authentication failed");
      }

      const result = await response.json();

      // Exhaustive search for the JWT in Clerk/Neon Auth OR Better Auth token
      const token = result.token || 
                    (result.session && result.session.token) ||
                    (result.session && result.session.last_active_token && result.session.last_active_token.jwt) ||
                    result.jwt ||
                    (result.client && result.client.sessions && result.client.sessions[0] && result.client.sessions[0].last_active_token && result.client.sessions[0].last_active_token.jwt);

      if (token) {
        chrome.storage.local.set({ isAuthenticated: true, userToken: token }, () => {
          checkAuthState();
        });
      } else {
        const foundKeys = Object.keys(result).join(", ");
        alert(`Auth Succeeded but no valid token found. Found keys: [${foundKeys}].`);
        console.log("Full Auth Response:", result);
      }
    } catch (err) {
      console.error(err);
      alert(`Auth Failed: ${err.message}`);
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
          const token = res.userToken;
          if (!token) {
              transcriptionOutput.innerText = "❌ No valid session found. Please Log Out and Sign In again.";
              return;
          }
          transcriptionOutput.classList.remove("hidden");
          transcriptionOutput.innerText = `Parsing Input: "${transcript}"...`;
          
          try {
              const parseRes = await fetch(`${BACKEND_URL}/api/v1/voice/parse`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                  body: JSON.stringify({ transcript })
              });
              
              if (!parseRes.ok) {
                  const errorData = await parseRes.json().catch(() => ({}));
                  console.error("Parse API Error Output:", errorData);
                  throw new Error(errorData.detail || errorData.message || "Voice parse failed");
              }
              
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
                  } else {
                      const errData = await saveRes.json().catch(() => ({}));
                      transcriptionOutput.innerText = `❌ Update failed: ${errData.detail || "Unauthorized"}`;
                  }
              } else {
                  transcriptionOutput.innerText = "⚠️ No structured data found.";
              }
          } catch (err) {
              console.error(err);
              if (err.message.includes("failed to fetch") || err.message.includes("NetworkError")) {
                  transcriptionOutput.innerText = "❌ Connection failed (Check Backend URL/VPN)";
              } else {
                  transcriptionOutput.innerText = `❌ Error: ${err.message}`;
              }
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
        transcriptionOutput.innerText = "Check your browser tab (NOT this popup) for the Mic permission prompt and speak!";
        
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
});

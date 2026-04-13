// popup/popup.js

const BACKEND_URL = "http://localhost:8005";
const CLERK_AUTH_URL = "https://ep-orange-smoke-amcqt5k6.neonauth.c-5.us-east-1.aws.neon.tech/neondb/auth/sign-in";

document.addEventListener("DOMContentLoaded", () => {
  const loginBtn = document.getElementById("login-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const guestView = document.getElementById("guest-view");
  const authView = document.getElementById("auth-view");
  const autoFillBtn = document.getElementById("autofill-btn");
  const formStatus = document.getElementById("form-status");
  const statusIndicator = document.querySelector(".status-indicator");
  const voiceBtn = document.getElementById("voice-btn");
  const transcriptionOutput = document.getElementById("transcription-output");
  const documentList = document.getElementById("document-list");

  // --- Auth & Profile State Management ---
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

  async function fetchProfileStatus(token) {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/profiles/me`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (response.ok) {
        const profile = await response.json();
        updateUIWithProfile(profile.data);
      } else if (response.status === 401) {
        logout(); // Token expired
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

  loginBtn.addEventListener("click", () => {
    // Open Neon Auth (Clerk) Sign-In in a new tab
    chrome.tabs.create({ url: CLERK_AUTH_URL });
    
    // Simple polling/listener logic for token capture would go here
    // For local dev, we might use a prompt or a cookie listener
    // Here we'll simulate the successful capture for now but explain it to user
    alert("Please sign in in the new tab. Once done, PaperAmbulance will sync your profile automatically!");
  });

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

  // Hook up manual fallback
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
                transcriptionOutput.innerText = "⚠️ Mic error. Try typing below.";
                return;
            }
            const res = results[0].result;
            if (res.error) {
                document.getElementById("manual-fallback").classList.remove("hidden");
                transcriptionOutput.innerText = `⚠️ Mic: ${res.error}`;
            } else if (res.transcript) {
                document.getElementById("manual-fallback").classList.add("hidden");
                processProfileUpdate(res.transcript);
            }
        });
    });
  });

  // Initialize view
  checkAuthState();
});

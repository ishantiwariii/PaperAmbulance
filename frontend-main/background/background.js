// background/background.js

// Keep track of the form data per tab
let formsByTab = {};

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // 1. Listen for detected forms from detection.js
  if (message.action === "FORM_DETECTED") {
    console.log(
      `Received form data from ${message.payload.url}`,
      message.payload.fields,
    );
    if (sender.tab) {
      formsByTab[sender.tab.id] = message.payload;
    }
  }

  // 2. Listen for the Auto-Fill click from the popup.js
  if (message.action === "TRIGGER_AUTOFILL") {
    console.log("Auto-fill requested by user. Fetching from FastAPI backend...");

    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      if (tabs.length > 0) {
        const tabId = tabs[0].id;
        const formPayload = formsByTab[tabId];

        if (!formPayload || !formPayload.fields) {
          console.error("No form data available for this tab.");
          return;
        }

        // Firing the exact fields to the FastAPI LangGraph backend
        fetch("https://paperambulance.onrender.com/api/v1/analyze/fill", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer LOCAL_DEV_TOKEN"
          },
          body: JSON.stringify(formPayload.fields)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.detail || "Server error"); });
            }
            return response.json();
        })
        .then(data => {
            console.log("Backend LangGraph Analysis Result:", data);
            if (data && data.fill_map) {
                // Send the payload to fill.js in the active tab
                chrome.tabs.sendMessage(tabId, {
                  action: "EXECUTE_FILL",
                  fill_map: data.fill_map,
                });
            }
        })
        .catch(err => {
            console.error("Error communicating with backend:", err);
            // Alert the user on the webpage that something went wrong
            chrome.scripting.executeScript({
              target: { tabId: tabId },
              func: (msg) => alert(`🚑 PaperAmbulance: ${msg}\nDid you speak your data into the extension first?`),
              args: [err.message]
            });
        });
      }
    });
  }

  // 3. Listen for popup asking about the active tab's form status
  if (message.action === "GET_FORM_STATUS") {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      if (tabs.length > 0) {
        const tabId = tabs[0].id;
        const formStatus = formsByTab[tabId] || null;
        sendResponse({ status: formStatus ? "detected" : "none", data: formStatus });
      } else {
        sendResponse({ status: "none", data: null });
      }
    });
    return true; // Indicates we will respond asynchronously
  }
});

// Clean up when tabs are closed
chrome.tabs.onRemoved.addListener((tabId) => {
  delete formsByTab[tabId];
});

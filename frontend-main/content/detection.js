// content/detection.js
const VERSION = "1.1";

function scanForForms() {
  const inputs = document.querySelectorAll(
    'input:not([type="hidden"]):not([type="submit"]), select, textarea',
  );

  if (inputs.length === 0) return;

  const fieldData = Array.from(inputs).map((input) => ({
    id: input.id,
    name: input.name,
    type: input.type,
    placeholder: input.placeholder || "",
    tagName: input.tagName.toLowerCase(),
  }));

  chrome.runtime.sendMessage({
    action: "FORM_DETECTED",
    payload: {
      url: window.location.hostname,
      fields: fieldData,
    },
  });
}

function showActivationToast() {
  const hostname = window.location.hostname;
  
  // Check if we already have permission for this site
  chrome.storage.local.get(["allowedDomains"], (res) => {
    const allowedDomains = res.allowedDomains || [];
    if (allowedDomains.includes(hostname)) {
      scanForForms();
      return;
    }

    // Create Toast UI
    const toast = document.createElement("div");
    toast.className = "paper-ambulance-toast";
    toast.innerHTML = `
      <div class="icon">🚑</div>
      <div class="text">Allow PaperAmbulance to help with forms on this site?</div>
      <div class="actions">
        <button class="paper-ambulance-btn paper-ambulance-btn-yes" id="pa-activate">Yes</button>
        <button class="paper-ambulance-btn paper-ambulance-btn-no" id="pa-dismiss">No</button>
      </div>
    `;

    document.body.appendChild(toast);

    document.getElementById("pa-activate").addEventListener("click", () => {
      // Save choice for next time
      chrome.storage.local.set({ allowedDomains: [...allowedDomains, hostname] }, () => {
        toast.remove();
        scanForForms();
      });
    });

    document.getElementById("pa-dismiss").addEventListener("click", () => {
      toast.remove();
    });
  });
}

// Logic: Check if page has any inputs before even showing the toast
function init() {
  const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]), select, textarea');
  if (inputs.length > 0) {
    showActivationToast();
  }
}

if (document.readyState === "complete") {
  init();
} else {
  window.addEventListener("load", init);
}

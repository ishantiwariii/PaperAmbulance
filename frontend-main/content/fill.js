// content/fill.js

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "EXECUTE_FILL") {
    console.log("🚑 Commencing Auto-Fill Sequence...", message.fill_map);

    const map = message.fill_map;

    // Dynamic matching engine mapping LangGraph mapped nodes to physical DOM targets
    Object.entries(map).forEach(([key, value]) => {
      if (!value) return;

      // 1. Direct hit from Gemini using unique HTML tags
      let targetInput = document.getElementById(key) || document.querySelector(`[name="${key}"]`);

      // 2. Intelligent fuzzy fallback just in case Gemini inferred the semantic ID abstractly
      if (!targetInput) {
        const inputs = document.querySelectorAll("input:not([type='hidden']), select, textarea");
        for (const input of inputs) {
          const identifier = (input.id || input.name || "").toLowerCase();
          const cleanKey = key.toLowerCase().replace(/_/g, "");
          if (identifier && (identifier.includes(cleanKey) || cleanKey.includes(identifier))) {
            targetInput = input;
            break;
          }
        }
      }

      if (targetInput) {
        targetInput.value = value;
        highlightField(targetInput);
      }
    });
  }
});

// Add a nice visual glow so the user knows what we changed
function highlightField(element) {
  element.style.transition = "all 0.3s ease";
  element.style.boxShadow = "0 0 8px #34C759";
  element.style.border = "1px solid #34C759";

  // Remove the glow after 2 seconds
  setTimeout(() => {
    element.style.boxShadow = "none";
    element.style.border = "";
  }, 2000);
}

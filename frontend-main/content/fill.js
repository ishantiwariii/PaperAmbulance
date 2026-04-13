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
        // Handle different input types
        const type = targetInput.type ? targetInput.type.toLowerCase() : "";
        
        if (type === "checkbox" || type === "radio") {
          targetInput.checked = (value.toString().toLowerCase() === "true" || value === "1" || value === "yes");
        } else {
          targetInput.value = value;
        }

        // Trigger events so modern frameworks (React/Vue) see the change
        targetInput.dispatchEvent(new Event("input", { bubbles: true }));
        targetInput.dispatchEvent(new Event("change", { bubbles: true }));
        
        highlightField(targetInput);
      }
    });
  }
});

// Add a nice visual glow so the user knows what we changed
function highlightField(element) {
  const originalTransition = element.style.transition;
  const originalShadow = element.style.boxShadow;
  const originalBorder = element.style.border;

  element.style.transition = "all 0.3s ease";
  element.style.boxShadow = "0 0 10px rgba(52, 199, 89, 0.6)";
  element.style.border = "1px solid #34C759";

  // Remove the glow after 2.5 seconds
  setTimeout(() => {
    element.style.boxShadow = originalShadow;
    element.style.border = originalBorder;
    setTimeout(() => {
      element.style.transition = originalTransition;
    }, 300);
  }, 2500);
}

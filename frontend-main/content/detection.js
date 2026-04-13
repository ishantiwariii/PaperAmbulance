// content/detection.js
console.log("🚑 PaperAmbulance: Surveillance Active");

function scanForForms() {
  // Grab all visible inputs, selects, and textareas
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

  console.log(`Found ${fieldData.length} fields. Sending to HQ...`);

  // Send the data to our background script
  chrome.runtime.sendMessage({
    action: "FORM_DETECTED",
    payload: {
      url: window.location.hostname,
      fields: fieldData,
    },
  });
}

// Run the scan when the page is fully loaded or immediately if already loaded
if (document.readyState === "complete") {
  scanForForms();
} else {
  window.addEventListener("load", scanForForms);
}

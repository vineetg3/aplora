let port; // Global port variable

document.getElementById("fillContent").addEventListener("click", () => {
  console.log("Filling content started..")
  // Check if the port is already open
  if (!port) {
    port = chrome.runtime.connect({ name: "content-port" }); // Open a new port
    setupPortListeners();
    console.log("Port opened.");
  } else {
    console.log("Port already opened.");
  }

  // Query the active tab in the current window
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    // Inject the script into the active tab to extract rendered HTML content
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id }, // Target the current tab
        function: extractRenderedHTML, // Execute the function in the page context
      },
      (results) => {
        // Get the extracted HTML content
        const renderedHTML = results[0].result;

        // Console log the rendered HTML content
        console.log("Process has started", renderedHTML);

        // // Display a message that content is logged in the console
        // document.getElementById("result").innerText =
        //   "Rendered HTML logged in console.";

        // // Copy the extracted HTML content to the clipboard
        // copyToClipboard(renderedHTML);

        // alert(
        //   "Rendered HTML content copied to clipboard! Check the console for the full content."
        // );
        showSpinner("result")
        // Send a message via the port
        port.postMessage({
          action: "start-process",
          renderedHTML: renderedHTML,
          tabid: tabs[0].id,
        });
        console.log("Message sent to content script via port.");
      }
    );
  });
});

// Show spinner
function showSpinner(id) {
    document.getElementById(id).innerHTML = `
        <div class="spinner"></div>
        <span>Process running...</span>
    `;
}
// Hide spinner
function hideSpinner(id) {
    document.getElementById(id).innerText = "Process complete";
}

// This function extracts the full rendered HTML content of the webpage
function extractRenderedHTML() {
  // Wait for the DOMContentLoaded event to ensure that the JS has completed rendering
  return new Promise((resolve) => {
    if (
      document.readyState === "complete" ||
      document.readyState === "interactive"
    ) {
      resolve(document.documentElement.outerHTML); // Return rendered HTML immediately
    } else {
      window.addEventListener("DOMContentLoaded", () => {
        resolve(document.documentElement.outerHTML); // Return rendered HTML after DOM is ready
      });
    }
  });
}

// Function to copy text to clipboard
function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => console.log("Copied to clipboard successfully."))
    .catch((err) => console.error("Error copying to clipboard: ", err));
}

function setupPortListeners() {
  // Handle incoming messages from background script
  port.onMessage.addListener((message) => {
    console.log("Received message from background:", message);

    switch (message.action) {
      case "process-complete":
        hideSpinner("result")
        document.getElementById("result").innerText = message.result;
        break;
      case "process-error":
        document.getElementById("result").innerText = `Error: ${message.error}`;
        break;
      case "status-update":
        updateStatus(message.status);
        break;
      default:
        console.log("Unknown message type:", message);
    }
  });

  // Handle port disconnection
  port.onDisconnect.addListener(() => {
    console.log("Port disconnected");
    port = null; // Reset port variable
  });
}
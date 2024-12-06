// // Content script can listen for messages from the popup or background script
// // chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
// //   // If the request action is to extract content
// //   if (request.action === "extractContent") {
// //     // Send back the page content (text inside the body tag)
// //     sendResponse({ content: document.body.innerText });
// //   }
// // });

// // content.js
// const port = chrome.runtime.connect({ name: "content-port" });
// console.log("Inside content.js");
// // Send initial message
// port.postMessage({ action: "initialize-puppeteer" });
// // console.log("Received response in content script:", response);
// // Listen for response
// port.onMessage.addListener((response) => {
//   if (response.success) {
//     console.log("Title received in content script:", response.title);
//   } else {
//     console.error("Error:", response.error);
//   }
// });




// // This function extracts the full rendered HTML content of the webpage
// function extractRenderedHTML() {
//   // Wait for the DOMContentLoaded event to ensure that the JS has completed rendering
//   return new Promise((resolve) => {
//     if (
//       document.readyState === "complete" ||
//       document.readyState === "interactive"
//     ) {
//       resolve(document.documentElement.outerHTML); // Return rendered HTML immediately
//     } else {
//       window.addEventListener("DOMContentLoaded", () => {
//         resolve(document.documentElement.outerHTML); // Return rendered HTML after DOM is ready
//       });
//     }
//   });
// }

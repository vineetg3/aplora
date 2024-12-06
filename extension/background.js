// background.js
import {
  connect,
  ExtensionTransport,
} from "puppeteer-core/lib/esm/puppeteer/puppeteer-core-browser.js";

import { io } from "https://cdn.jsdelivr.net/npm/socket.io-client@4.7.1/+esm";
import PQueue from "https://cdn.jsdelivr.net/npm/p-queue@8.0.1/+esm";

//global variables

// Create a PQueue instance with concurrency 1 for sequential processing
const queue = new PQueue({ concurrency: 1 });

let server_url = "http://127.0.0.1:5001";

let socket = io("http://127.0.0.1:5001", { transports: ["websocket"] });

class GlobalStateManager {
  constructor() {
    this.globalState = {}; // Internal state object
  }

  // Add a new work_id entry
  addWorkState(work_id, page) {
    this.globalState[work_id] = { page };
  }

  // Retrieve the state for a specific work_id
  getWorkState(work_id) {
    return this.globalState[work_id] || null;
  }

  // Add or update a key for a specific work_id
  addOrUpdateKey(work_id, key, value) {
    if (!this.globalState[work_id]) {
      console.error(
        `Work ID ${work_id} does not exist. Use addWorkState() first.`
      );
      return;
    }
    this.globalState[work_id][key] = value;
  }

  // Remove a work_id entry
  removeWorkState(work_id) {
    delete this.globalState[work_id];
  }

  // List all work_ids
  listWorkIds() {
    return Object.keys(this.globalState);
  }

  // Check if a work_id exists
  hasWorkState(work_id) {
    return this.globalState.hasOwnProperty(work_id);
  }

  // Clear all states
  clearAll() {
    this.globalState = {};
  }
}

const globalStateManager = new GlobalStateManager();

function generateShortId() {
  return `${Date.now().toString(36)}-${Math.random()
    .toString(36)
    .substr(2, 5)}`;
}

chrome.runtime.onConnect.addListener((port) => {
  //   console.assert(port.name === "initialize-puppeteer");

  if (port.name == "content-port")
    port.onMessage.addListener((msg) => {
      if (msg.action === "start-process") {
        let browser;
        (async () => {
          try {
            // create browser and tab connection
            browser = await connect({
              transport: await ExtensionTransport.connectTab(msg.tabid),
            });

            let [page] = await browser.pages();
            let work_id = generateShortId();
            globalStateManager.addWorkState(work_id, page);
            globalStateManager.addOrUpdateKey(work_id, "tabid", msg.tabid);
            globalStateManager.addOrUpdateKey(work_id, "port", port);
            console.log(globalStateManager);

            // Dynamically set viewport to match the full window size
            const { width, height } = await page.evaluate(() => {
              const width = Math.min(window.innerWidth * 1.7, 1920); // max width
              const height = Math.min(window.innerHeight * 1.7, 1080); // max height
              return { width, height };
            });
            await page.setViewport({ width, height });

            //send html to server and start process
            socket.emit("new_work", {
              work_id: work_id,
              renderedHTML: String(msg.renderedHTML),
            });

            //testing stuff
          } catch (error) {
            console.error("Error:", error);
            if (browser) await browser.close();
          }
        })();
        return true;
      }
      return true;
    });
});

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

//socket events
socket.on("connect", () => {
  console.log("Connected to server");
});

socket.on("disconnect", (reason) => {
  console.log("Disconnected from server:", reason);
});

socket.on("fill_text_input", (data) => {
  queue.add(async () => await handleFillTextInput(data));
});

socket.on("fill_checkbox", (data) => {
  queue.add(async () => await handleFillCheckBox(data));
});

socket.on("fill_radio_btn", (data) => {
  queue.add(async () => await handleRadioButton(data));
});

socket.on("click", (data) => {
  console.log("Clicking", data);
  queue.add(async () => await scrollAndClickElement(data));
});

socket.on("end-process", (data) => {
  const jsonData = typeof data === "string" ? JSON.parse(data) : data;
  let port = globalStateManager.getWorkState(jsonData.work_id).port;
  queue.add(() => sendMessageToPopup(port));
});

// background.js
function sendMessageToPopup(port) {
  console.log("Sending ending notif..");
  port.postMessage({
    action: "process-complete",
    result: "Run finished!",
  });
}

socket.on("click_dropdown_and_select", (data) => {
  const jsonData = typeof data === "string" ? JSON.parse(data) : data;
  queue.add(async () => {
    let tabid = globalStateManager.getWorkState(jsonData.work_id).tabid;
    const linesOld = await getLinesOfTextPromise(tabid);
    let selector = cssSelector(jsonData.tag);
    console.log("selector");
    console.log(selector);
    await scrollAndClickElement(jsonData, selector);
    console.log("scrolling done.");
    // await delay(1000);
    const linesNew = await getLinesOfTextPromise(tabid);
    const htmlNew = await getLatestHtmlPromise(tabid);
    let new_options = findNewLines(linesOld, linesNew);
    console.log(new_options);
    try {
      const response = await fetch("http://127.0.0.1:5001/api/select_option", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          options: new_options,
          work_id: jsonData.work_id,
          description: jsonData.tag["description"],
          newHtml: htmlNew,
        }),
      });
      const result = await response.json();
      if (result === "unsuccessful") return;
      console.log("Response from Python:", result);
      let option_selector = cssSelector(result.element_to_select);
      console.log("selector");
      console.log(option_selector);
      await scrollAndClickElement(jsonData, option_selector);
      console.log("Option selected");
      // await delay(2000);
    } catch (error) {
      console.error("Error sending request to Python:", error);
    }
  });
});

socket.on("select_option", (data) => {
  const jsonData = typeof data === "string" ? JSON.parse(data) : data;
  queue.add(async () => {
    console.log(data);
    let selector = cssSelector(jsonData.tag);
    console.log("selector");
    console.log(selector);
    await handleSelectOptionByValue(data.work_id, data.tag, selector);
  });
});

function findNewLines(oldLines, newLines) {
  const oldSet = new Set(oldLines);
  return newLines.filter((line) => !oldSet.has(line));
}

function cssSelector(tag) {
  const tagType = tag.tag_type || "input";
  const selectorParts = [tagType];

  // Define allowed attributes (assuming HTMLHandler.allowed_attrs equivalent)
  const allowedAttrs = [
    "id",
    "class",
    "name",
    "aria-describedby",
    "aria-label",
    "type",
    "value",
    "placeholder",
    "href",
    "src",
    "alt",
    "title",
    "role",
    "aria-label",
  ]; // Add or modify attributes as needed

  // Add allowed attributes to the selector
  for (const attr of allowedAttrs) {
    if (tag.hasOwnProperty(attr) && tag[attr] !== null) {
      let attrValue = tag[attr];

      // If the attribute value is an array, join it into a single string
      if (Array.isArray(attrValue)) {
        attrValue = attrValue.join(" "); // You can change the separator if needed
      }

      // Append the attribute to the selector
      selectorParts.push(`[${attr}="${attrValue}"]`);
    }
  }

  // Join parts to form the full selector
  const cssSelector = selectorParts.join("");
  return cssSelector;
}

// ////////////////////Get Latest HTML//////////////////////
function getLatestHtmlPromise(tabId) {
  return new Promise((resolve) => {
    getLatestHtml(tabId, (result) => {
      resolve(result);
    });
  });
}

function getLatestHtml(tabId, callback) {
  chrome.scripting.executeScript(
    {
      target: { tabId: tabId }, // Target the current tab
      function: extractRenderedHTML, // Execute the function in the page context
    },
    (results) => {
      if (chrome.runtime.lastError) {
        console.error("Error extracting HTML:", chrome.runtime.lastError);
        callback(null); // Pass `null` to indicate an error
        return;
      }
      const renderedHTML = results[0].result;
      callback(renderedHTML); // Pass the HTML back through the callback
    }
  );
}

// ////////////////////Get Latest lines of text//////////////////////
function getLinesOfTextPromise(tabId) {
  return new Promise((resolve) => {
    getLinesOfText(tabId, (result) => {
      resolve(result);
    });
  });
}
function getLinesOfText(tabId, callback) {
  chrome.scripting.executeScript(
    {
      target: { tabId: tabId },
      function: extractTextLines,
    },
    (results) => {
      if (chrome.runtime.lastError) {
        console.error("Error extracting text lines:", chrome.runtime.lastError);
        callback(null);
        return;
      }
      const textLines = results[0].result;
      callback(textLines);
    }
  );
}

// Function to be injected into the page
function extractTextLines() {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );

  const texts = [];
  let node;

  while ((node = walker.nextNode())) {
    const trimmedText = node.textContent.trim();
    if (trimmedText) {
      texts.push(trimmedText);
    }
  }

  return texts;
}

////////////////////////////////////////////////

async function clickElement(data) {
  try {
    const jsonData = typeof data === "string" ? JSON.parse(data) : data;
    let page = globalStateManager.getWorkState(data.work_id).page;
    await page.click(data.selector);
  } catch (error) {}
}

// Create a delay function
function delay(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

async function scrollAndClickElement(data, selector) {
  try {
    console.log("Starting scrollAndClickElement function...");
    const jsonData = typeof data === "string" ? JSON.parse(data) : data;
    let page = globalStateManager.getWorkState(jsonData.work_id).page;

    // First, try to find the element without scrolling
    try {
      await page.waitForSelector(selector, { timeout: 1000 });
      await page.click(selector);
      console.log(`Element found and clicked directly: "${selector}"`);
      return;
    } catch (e) {
      // Element not immediately visible, proceed with scrolling
    }

    // Optimized scroll and click
    await page.evaluate(async (sel) => {
      return new Promise((resolve, reject) => {
        // Function to find and click element
        const findAndClick = () => {
          const element = document.querySelector(sel);
          if (element) {
            element.scrollIntoView({ behavior: "instant", block: "center" });
            return true;
          }
          return false;
        };

        // Try to find element immediately
        if (findAndClick()) {
          resolve();
          return;
        }

        // If not found, use IntersectionObserver for efficient scrolling
        let scrollHeight = 0;
        const maxScroll = document.body.scrollHeight;
        const scrollStep = window.innerHeight;

        const scroll = () => {
          if (findAndClick()) {
            resolve();
            return;
          }

          scrollHeight += scrollStep;
          if (scrollHeight >= maxScroll) {
            reject(new Error(`Element with selector "${sel}" not found`));
            return;
          }

          window.scrollTo({
            top: scrollHeight,
            behavior: "instant",
          });

          requestAnimationFrame(scroll);
        };

        requestAnimationFrame(scroll);
      });
    }, selector);

    // Final click after element is found and scrolled into view
    await page.click(selector);
    console.log(`Successfully clicked element: "${selector}"`);
  } catch (error) {
    console.error("Error in scrollAndClickElement:", error.message);
    throw error;
  }
}

// Listen for a command (or trigger this function programmatically)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "scrollAndClick") {
    const { tabId, selector } = message;
    scrollAndClick(tabId, selector);
    sendResponse({ success: true, message: "Scroll and click initiated." });
  }
});

// Task handlers
async function handleFillTextInput(data) {
  try {
    // Ensure the data is in JSON format
    const jsonData = typeof data === "string" ? JSON.parse(data) : data;
    console.log("Filling input text: ", jsonData);
    let page = globalStateManager.getWorkState(data.work_id).page;
    // Wait for the selector and type the input
    await page.waitForSelector(jsonData.selector);
    await page.$eval(
      jsonData.selector,
      (input, value) => {
        input.value = value;
      },
      jsonData.value
    );
    // await page.type(jsonData.selector, String(jsonData.value));
  } catch (error) {
    console.error("Error processing data:", error);
  }
}

async function handleFillCheckBox(data) {
  try {
    // Ensure the data is in JSON format
    const jsonData = typeof data === "string" ? JSON.parse(data) : data;
    console.log("Filling input text: ", jsonData);
    let page = globalStateManager.getWorkState(data.work_id).page;
    // Wait for the selector and type the input
    // Define the checkbox selector
    const checkboxSelector = jsonData.selector; // Replace with your checkbox selector

    // Wait for the checkbox to appear in the DOM
    await page.waitForSelector(checkboxSelector);

    // Check if the checkbox is already selected
    const isChecked = await page.$eval(
      checkboxSelector,
      (checkbox) => checkbox.checked
    );

    if (!isChecked) {
      // Click the checkbox if it is not already checked
      await page.click(checkboxSelector);
      console.log("Checkbox selected.");
    } else {
      console.log("Checkbox was already selected.");
    }
  } catch (error) {
    console.error("Error processing data:", error);
  }
}

async function handleRadioButton(data) {
  try {
    // Ensure the data is in JSON format
    const jsonData = typeof data === "string" ? JSON.parse(data) : data;
    console.log("Filling radio btn: ", jsonData);
    // Define the checkbox selector
    const radioBtnSelector = jsonData.selector; // Replace with your checkbox selector
    await scrollAndClickElement(jsonData, radioBtnSelector);
  } catch (error) {
    console.error("Error processing data:", error);
  }
}

async function handleSelectOptionByValue(work_id, tag, selectSelector) {
  try {
    // Ensure the data is in JSON format
    const jsonData = typeof data === "string" ? JSON.parse(tag) : tag;
    console.log("Selecting option by value: ", jsonData);

    // Retrieve the Puppeteer page instance
    let page = globalStateManager.getWorkState(work_id).page;

    // Wait for the <select> element to appear in the DOM
    await page.waitForSelector(selectSelector);

    // Select the desired option by value
    const selectedValues = await page.select(
      selectSelector,
      tag.select_option_value
    );

    console.log(`Option selected. Selected value(s): ${selectedValues}`);
  } catch (error) {
    console.error("Error while selecting option:", error);
  }
}

// Debugging the queue
queue.onEmpty().then(() => console.log("All tasks completed!"));

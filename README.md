# Aplora: Leveraging LLM-Driven Semantic Web Parsing for Automated Form Filling and Optimization of Workflows

## Overview
Aplora is a cutting-edge Chrome extension designed to streamline the process of filling web forms, such as job applications. By leveraging Large Language Models (LLMs) and context-aware web parsing, Aplora automatically fills in form fields with precision and efficiency based on information provided in a context document (`context.txt`). While optimized for job applications, Aplora is flexible and can be adapted for other types of forms.

### Key Features
- **Automated Form Filling**: Reduces manual effort by completing forms using information extracted from a predefined context document.
- **LLM-Driven Intelligence**: Executes semantic understanding to ensure accurate and contextually relevant entries.
- **Workflow Optimization**: Minimizes repetitive tasks, saving significant time and effort.
- **User-Friendly**: Easy-to-use interface with just one click to fill forms.
- **Versatile**: Capable of handling various types of online forms with minimal configuration.

### Form Filling in Action
Watch how Aplora automatically fills out a job application form using information from the context document in the following video:

![Aplora Form Filling Demo](demo.gif)

The demonstration above shows Aplora's seamless form-filling capabilities, including:
- Automatic field detection and mapping
- Intelligent content extraction from context
- Real-time form completion

---

## Prerequisites

### 1. Extension Code Environment
- **Node.js**: Ensure you have Node.js installed on your system.
- **Chrome Browser**: Required to run the extension.

### 2. Python Server Environment
- **Docker**: Required for running the Aplora backend server.

---

## Installation and Setup

### 1. Setting Up the Chrome Extension
1. Clone the repository or download the source code for the Chrome extension.
2. Navigate to the project directory.
3. Install required dependencies:
   ```bash
   npm install
   ```
4. Build the extension:
   ```bash
   npm run build
   ```
   This creates an `out` directory containing the extension code.
5. Load the extension into Chrome:
   - Open `chrome://extensions/` in your Chrome browser.
   - Enable "Developer Mode" (top-right corner).
   - Click on "Load unpacked" and select the `out` directory.
6. The extension should now be available in your Chrome extensions bar.

### 2. Setting Up the Python Server
The Python server is responsible for processing the context document and integrating with the LLM for parsing and filling forms.

1. Clone the repository containing the Python server.
2. Build the Docker image:
   ```bash
   docker build -t aplora-app .
   ```
3. Run the Docker container with the required OpenAI API key:
   ```bash
   docker run -v $(pwd):/app -p 5001:5001 -e OPENAI_API_KEY=your-key aplora-app
   ```
4. **Update context.txt**: Place the information to be used for form filling in the `context.txt` file.

---

## How to Use the Extension

1. Open the webpage where you need to fill a form (e.g., job application form).
2. Ensure the Python server is running and the context document at (backend/context.txt) has been updated.
3. Click on the Aplora Chrome extension icon in the top-right corner of the browser.
4. Click on the **"Fill Content"** button.
5. A spinner will appear while the extension works. **Do not navigate away from the page** while the spinner is active.
6. Form filling is complete when you see the message: **"Run finished!"**

---

## Notes
1. **OpenAI API Key**: You must have a valid OpenAI API key to use the backend server. Replace `your-key` with your actual API key in the `docker run` command.
2. **Supported Browsers**: Currently, this extension is developed for and tested on Google Chrome.
3. **Context Document**: The `context.txt` file should be updated with accurate and complete information for optimal results. Ensure the JSON fields or plain text format aligns with the expected form structure.

---

## Troubleshooting
- **Form Not Filled Correctly**: Check that the `context.txt` contains the relevant data and is formatted correctly.
- **Extension Not Working**: Verify that the `out` directory was loaded as an unpacked Chrome extension.
- **Server Issues**: Confirm the Docker container is running and the OpenAI API key is valid.
- **Spinner Doesn't Stop**: Ensure you haven't navigated away from the page and that the Python server is running.

---

## Contribution
We welcome contributions to improve Aplora! Please feel free to submit pull requests or raise issues to report bugs or suggest new features.

---

## License
Aplora is licensed under the [MIT License](./LICENSE).

---

Enjoy automated form filling with Aplora! 🎉
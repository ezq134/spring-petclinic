# ARCA Agent: Development Roadmap
**Project Name**: Automated Root Cause Analysis (ARCA) Agent  
**Language**: Python 3.x

This roadmap breaks down the development of the AI DevOps agent into educational phases. Each phase builds a functional piece of the agent while explaining Python concepts.

---

## Phase 1: The Foundation - [COMPLETED] 
**Goal**: Create a script that can "listen" to GitHub Actions.
*   **What we do**: 
    *   Setup the Python environment.
    *   Use the `argparse` library to allow the script to accept inputs like `--run-id` and `--repo`.
*   **Concepts Learned**: Imports, Variables, Functions, and CLI Arguments.
*   **Outcome**: You can run `python agent.py --run-id 123` and the script prints: *"Analyzing Run 123"*.

## Phase 2: The Researcher - [COMPLETED]
**Goal**: Connect to GitHub and "read" the results of the failed build.
*   **What we do**:
    *   Use the `requests` library to talk to the GitHub REST API.
    *   Use the `zipfile` library to open the logs GitHub sends us.
    *   Filter the logs to find the "smoking gun" (the error message).
*   **Concepts Learned**: HTTP Requests (GET), Error Handling (Try/Except), and File Streams.
*   **Outcome**: The script downloads the logs for a specific run and finds the exact line where the error occurred.

## Phase 3: The Brain - [COMPLETED]
**Goal**: Send the error to an AI and ask for a fix.
*   **What we do**:
    *   Setup the OpenAI or Anthropic SDK.
    *   Create a "System Prompt" (The Personality: "You are a DevOps Expert").
    *   Send the filtered logs to the AI and receive a JSON or Text response.
*   **Concepts Learned**: API Keys, String Formatting, and JSON parsing.
*   **Outcome**: The script prints a human-readable explanation of the error and a `kubectl` or `mvn` command to fix it.

## Phase 4: The Messenger - [COMPLETED]
**Goal**: Get the answer into the hands of the developer.
*   **What we do**:
    *   Use Python's built-in `smtplib` to connect to Gmail/SMTP.
    *   Format a "Beautiful" email using HTML.
*   **Concepts Learned**: String Templates and Networking.
*   **Outcome**: A developer receives an email with the subject "🚨 ARCA Analysis: Here is your fix".

## Phase 5: The Loop - [COMPLETED]
**Goal**: Make it fully autonomous and portable.
*   **What we do**:
    *   Create `requirements.txt` and `Dockerfile.arca`.
    *   Use `ENTRYPOINT` to allow dynamic argument passing to the container.
*   **Outcome**: A "Self-Healing Ready" container that runs the agent anywhere.

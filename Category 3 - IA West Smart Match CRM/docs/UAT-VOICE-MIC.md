# Voice/Mic UAT Guide -- IA West SmartMatch CRM

## Overview

This guide enables a reviewer to independently walk through the live voice/mic coordinator path, verifying intent parsing, human approval gating, and agent action execution. No prior implementation knowledge required. A reviewer following only this guide can trigger voice input, observe intent parsing produce an approval card, approve or reject the proposed action, and confirm that agent execution is gated by that decision -- without any developer assistance.

---

## Prerequisites

Before starting, confirm the following:

1. **Python 3.10+** installed with project dependencies:
   ```
   pip install -r requirements.txt
   ```
2. **streamlit-webrtc** installed -- required for microphone (Path A):
   ```
   python -c "import streamlit_webrtc; print('OK')"
   ```
   If this fails, the UI will show: `"streamlit-webrtc not installed. Use text commands."` Voice input (Path A) will be unavailable, but text input (Path B) fully works.

3. **Browser:** Chrome or Chromium recommended. Firefox may block WebRTC audio and prevent the microphone from activating.

4. **Microphone:** Built-in or external mic connected and not muted (only required for Path A: Voice Input). Path B (text input) does not require a microphone.

5. **Gemini API key (optional):** Set `GEMINI_API_KEY` as an environment variable for LLM-based intent parsing. Without it, keyword fallback is used automatically. Both modes produce identical approval cards -- the only difference is the reasoning field, which reads `"Matched keyword in: '...'"` instead of a natural-language LLM explanation. All approve/reject behavior is identical either way.

---

## Starting the Application

1. Open a terminal and navigate to the project directory:
   ```
   cd "Category 3 - IA West Smart Match CRM"
   ```

2. Start the Streamlit app:
   ```
   streamlit run src/app.py
   ```

3. Open a browser and navigate to:
   ```
   http://localhost:8501
   ```

4. **Note:** The FastAPI backend (`:8000`) is **NOT required** for the voice/mic coordinator path. Only the Streamlit app (`:8501`) is needed for this guide.

5. **Expected on first load:** Two loading spinners appear in sequence:
   - `"Loading voice model (first use)..."` (TTS model initializing)
   - `"Loading speech recognition..."` (STT model initializing)
   Wait for both spinners to complete before proceeding.

6. Navigate to the **Command Center** tab (2nd tab in the Coordinator Dashboard section).

7. **Expected initial state:**
   - Page heading reads: `"Jarvis -- Voice Command Center"`
   - Conversation area shows: `"No conversation yet"` with three demo hint chips:
     - `"Find new events"`
     - `"Rank speakers for CPP Career Fair"`
     - `"Prepare full outreach campaign"`

---

## Path A: Voice Input

Use this path to test the microphone-to-approval-card flow.

1. **Action:** Click the microphone button (located on the right side of the voice panel, in the narrow column to the right of the text input field).

   **Expected:** The browser shows a microphone permission prompt. In Chrome, this appears as a small popup near the address bar reading "localhost:8501 wants to use your microphone."

2. **Action:** Click **Allow** in the browser permission prompt.

   **Expected:** The WebRTC widget becomes active -- the START/STOP button activates, indicating the microphone is now recording. Audio is being captured.

3. **Action:** Speak clearly into the microphone: **"Find new events"**. Then click the **STOP** button on the WebRTC widget to end the recording.

   **Expected:** A spinner appears reading `"Transcribing..."`. After 2-5 seconds, the transcript appears in the conversation history as a user message, and an approval card appears directly below it.

4. **Action:** Examine the approval card that appeared.

   **Expected:** The card displays the following:
   - Agent name: **Discovery Agent**
   - Status: `proposed`
   - Description: "Scrape universities for new events"
   - Reasoning line (either an LLM explanation if Gemini key is set, or `"Matched keyword in: 'find new events'"` in keyword fallback mode)
   - Two action buttons: **Approve** (blue/primary) and **Reject**

5. **Action:** Click the **Approve** button on the Discovery Agent card.

   **Expected:** The status changes from `proposed` to `executing` (briefly shows `"Status: executing..."`), then transitions to `completed`. A green success box appears showing a result such as `"Found N event(s) (source: ...)"`.

6. **Action:** Observe the conversation history scroll area.

   **Expected:** The completed action card remains in the conversation history with status `completed` and the result text visible. The state machine has transitioned: proposed -> approved -> executing -> completed.

---

## Path B: Text Input (Fallback)

Use this path if the microphone is unavailable, or to test the text-input approval flow independently.

1. **Action:** In the text input field (placeholder text reads `"Type a command or use the mic..."`), type:
   ```
   Rank speakers for CPP Career Fair
   ```

2. **Action:** Click the **Send Command** button (blue/primary button below the text input field).

   **Expected:** A new user message appears in the conversation history, followed immediately by an approval card.

3. **Action:** Examine the approval card.

   **Expected:** The card displays:
   - Agent name: **Matching Agent**
   - Status: `proposed`
   - Description: "Rank speakers for a target event"
   - Reasoning line with LLM or keyword explanation
   - **Approve** and **Reject** buttons

4. **Action:** Click the **Reject** button.

   **Expected:** The card updates to show an orange/yellow warning box reading `"Action rejected by coordinator."` The status changes to `rejected`. No agent execution occurs. The state machine has transitioned: proposed -> rejected.

---

## Multi-Step Workflow: Prepare Campaign

This section verifies that the `prepare_campaign` intent spawns independent sub-proposals for each step of the campaign pipeline.

1. **Action:** Type `Prepare full outreach campaign` in the text input and click **Send Command**.
   (Alternatively, if the conversation is still empty, click the `"Prepare full outreach campaign"` demo hint chip.)

   **Expected:** THREE separate approval cards appear in the conversation history (not one combined card), because `prepare_campaign` is a multi-step intent that spawns 3 sub-proposals in parallel.

2. **Action:** Examine the three approval cards.

   **Expected:** The cards appear in this order:
   - **Discovery Agent** -- Description: "Scrape universities for new events" -- Status: `proposed`
   - **Matching Agent** -- Description: "Rank speakers for a target event" -- Status: `proposed`
   - **Outreach Agent** -- Description: "Draft outreach emails for a match" -- Status: `proposed`

   Each card has independent **Approve** and **Reject** buttons. The reasoning for all three reads: `"Part of 'Prepare full outreach campaign' campaign orchestration."`

3. **Action:** Approve one card (for example, the Discovery Agent card) and reject another (for example, the Outreach Agent card). Leave the third card (Matching Agent) untouched in `proposed` state.

   **Expected:**
   - The approved card (Discovery Agent) transitions through `executing` to `completed` with a result.
   - The rejected card (Outreach Agent) shows `"Action rejected by coordinator."` with status `rejected`. No execution occurs.
   - The third card (Matching Agent) remains in `proposed` state with **Approve** and **Reject** buttons still active.
   - This confirms independent approval gating: each sub-action is controlled separately. Approving one does not approve the others; rejecting one does not affect the others.

---

## Edge Cases

### Microphone Permission Blocked

**Symptom:** No mic permission prompt appears after clicking the mic button, or the WebRTC widget does not activate.

**Fix:**
- In Chrome, click the lock/info icon in the address bar > Site settings > Microphone > change to "Allow".
- Or navigate directly to `chrome://settings/content/microphone` and remove `localhost:8501` from the Blocked list.
- Reload the page after changing the permission.
- If the issue persists, check the OS-level microphone privacy settings (Windows: Settings > Privacy > Microphone; macOS: System Preferences > Security & Privacy > Microphone).

---

### STT Model Load Failure

**Symptom:** A yellow warning appears at the top of the Command Center tab reading:
`"Speech recognition unavailable. Please use text commands."`

**Cause:** The faster-whisper model failed to download (network issue) or a dependency is missing.

**Handling:** Switch to Path B (text input). All approval card behavior -- intent parsing, agent names, Approve/Reject buttons, status transitions -- is identical whether the command arrives via voice or text. The review can be completed fully using the text input path.

**Note on TTS:** If the text-to-speech model also fails to load, an additional warning appears:
`"Voice synthesis unavailable. Jarvis response shown as text above."`
This only affects audio playback of Jarvis responses -- all visual outputs (approval cards, status transitions, result text) remain fully functional.

---

### No Speech Detected

**Symptom:** After stopping the mic recording, a warning appears:
`"No speech detected. Please try again."`

**Fix:**
- Re-press the mic START button, speak louder and closer to the microphone, then press STOP.
- Check the OS-level microphone input level in system audio settings.
- In Chrome, verify that the correct microphone device is selected if multiple devices are available (click the lock icon > Microphone > choose the active device).

---

### streamlit-webrtc Not Installed

**Symptom:** A warning appears in the mic column reading:
`"streamlit-webrtc not installed. Use text commands."`

**Fix:** Install the missing package and restart:
```
pip install streamlit-webrtc
streamlit run src/app.py
```
Until the package is installed, use Path B (text input). All approval card behavior is identical.

---

### Gemini API Key Not Set (Keyword Fallback Mode)

**Symptom:** Approval cards appear as expected, but the reasoning field reads `"Matched keyword in: '...'"` instead of a natural-language LLM explanation.

**Impact:** None on functionality. Intent parsing, approval card generation, status transitions (proposed -> approved -> executing -> completed, or proposed -> rejected), and agent execution all work identically in keyword fallback mode. The only visible difference is the reasoning text shown on the approval card.

**Note:** This is the expected behavior in demo environments without a configured Gemini API key.

---

### Unknown Command

**Symptom:** After sending a command via text or voice, instead of an approval card, Jarvis responds with:
`"I couldn't understand that command. You said: '{text}'. Try rephrasing -- for example, 'find new events' or 'rank speakers for event X'."`

**Handling:** Rephrase the command using one of the supported command patterns listed in the Supported Commands Reference section below. The keyword fallback recognizes phrases such as "find events", "rank speakers", "outreach email", "check contacts", and "campaign".

---

## Supported Commands Reference

| Intent | Agent | Sample Commands | Description |
|--------|-------|-----------------|-------------|
| `discover_events` | Discovery Agent | "Find new events", "Discover events", "Scrape for events", "Find new" | Scrape universities for new events |
| `rank_speakers` | Matching Agent | "Rank speakers for CPP Career Fair", "Who should speak at X?", "Top speakers" | Rank speakers for a target event |
| `generate_outreach` | Outreach Agent | "Draft outreach email", "Generate email", "Write email for match" | Draft outreach emails for a match |
| `check_contacts` | Contacts Agent | "Check contacts", "Follow up on POCs", "Contact status" | Review POC contact status |
| `prepare_campaign` | Campaign Orchestrator | "Prepare full outreach campaign", "Launch campaign", "Full outreach" | Multi-step: discover + rank + outreach (3 independent sub-proposals) |

**Intent resolution:** Commands are matched using Gemini LLM (if `GEMINI_API_KEY` is set) or keyword fallback. Both produce identical approval cards. The keyword fallback looks for the phrases shown in Sample Commands within the input text (case-insensitive).

---

## Pass/Fail Checklist

Use this checklist to record the outcome of your UAT session. Each item is an independently testable assertion.

- [ ] Application starts and the Command Center tab loads with heading `"Jarvis -- Voice Command Center"`
- [ ] Voice input: mic button triggers browser microphone permission prompt and begins recording audio
- [ ] Voice input: spoken command is transcribed (spinner shows `"Transcribing..."`) and produces an approval card in conversation history
- [ ] Text input: typed command followed by clicking **Send Command** produces an approval card with the correct agent name
- [ ] Approval card shows: agent name, status `proposed`, description, reasoning, and both **Approve** and **Reject** buttons
- [ ] Clicking **Approve** transitions the status: proposed -> executing -> completed, with a result text visible (e.g., `"Found N event(s) (source: ...)"`)
- [ ] Clicking **Reject** shows `"Action rejected by coordinator."` with status `rejected` and no agent execution
- [ ] Multi-step command "Prepare full outreach campaign" produces exactly 3 separate approval cards (Discovery Agent, Matching Agent, Outreach Agent)
- [ ] Each sub-proposal in the multi-step campaign can be independently approved or rejected without affecting the others
- [ ] Edge case: missing streamlit-webrtc shows the fallback warning `"streamlit-webrtc not installed. Use text commands."` and text input remains fully functional
- [ ] Edge case: no Gemini API key produces keyword-based reasoning (`"Matched keyword in: '...'"`) while the full approval flow (approve/reject/execute) works identically

---

*Generated for IA West SmartMatch CRM v3.1 Demo Readiness milestone.*
*Requirement: VERIFY-03*

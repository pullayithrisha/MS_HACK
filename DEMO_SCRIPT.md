# SalesMind Demo Script

**Total Time: ~60 Seconds**

## Setup before demo
1. Start the FastAPI backend server (`uvicorn backend.main:app --reload`).
2. Open `frontend/index.html` in your browser.
3. Make sure the dropdown is set to "Stark Industries".
4. The Memory Log on the right should be empty ("No memories stored for this deal").

## The Live Demo

**Step 1: The First Interaction (No Memory)**
- **Say**: "I'm a sales rep. I need to write a follow up email to Stark Industries. Let's see what a standard, stateless AI does."
- **Action**: Type the following into the chat box and hit Enter:
  > *Draft an email to Stark Industries.*
- **Point out**: "It gives me a generic, boring email. It doesn't know anything about the client."

**Step 2: Feeding the Memory**
- **Say**: "Let's fix that. I just got off a call with them and I'm going to feed those notes to SalesMind. Hindsight memory will persist this forever."
- **Action**: Type the following into the chat box and hit Enter:
  > *They are really worried about implementation time and they use AWS. Also, I prefer my emails to be short.*
- **Point out**: Highlight the right sidebar (Memory Log). "Look at the right. The Hindsight memory layer instantly captured and stored these facts for the Stark Industries session."

**Step 3: The Recall (With Memory)**
- **Say**: "Now, let's fast forward. It's next week. I need to send that follow-up."
- **Action**: Type the following into the chat box and hit Enter:
  > *Draft a follow up email to Stark Industries.*
- **Point out**: Highlight the right sidebar (Currently Recalled Context). "The agent queried Hindsight and instantly recalled my preference for short emails and their AWS implementation concern. Because of that, it drafted a perfectly tailored, two-sentence email addressing deployment speed directly. That is the power of persistent memory."

## Optional Bonus Step (Behavior Change)
- **Say**: "Does it remember my global preferences?"
- **Action**: Change the dropdown in the sidebar to "Wayne Enterprises".
- **Action**: Type into the chat box:
  > *Draft a follow up to Wayne Enterprises.*
- **Point out**: "It still remembers my preference for *short* emails from the previous session, but it doesn't mention AWS because that was specific to Stark. It adapts dynamically."

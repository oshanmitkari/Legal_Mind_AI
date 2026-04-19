# 🧪 F6 AI Case Assistant - Complete Testing Guide

## 📋 Test Case: Murder Case 302

**Case Details**:
- **Case Number**: CJ/1010
- **Client**: oshan
- **Type**: Criminal
- **Description**: murder case 302
- **Status**: Open
- **Risk Score**: 0.0
- **Deadline**: April 20, 2026, 23:41 (DUE SOON - Amber Alert)

---

## ✅ Test 1: Dashboard Display (Bootstrap)

### Steps:
1. Navigate to: `http://localhost:5000/cases/dashboard`
2. Locate the case table

### Expected Results:
```
╔══════════════════════════════════════════════════════════════════╗
║ Case #     │ Client │ Type     │ Status │ Risk │ Deadline  │ Actions ║
╠══════════════════════════════════════════════════════════════════╣
║ CJ/1010    │ oshan  │ Criminal │ Open   │  0   │ Apr 20,   │ 👁 🤖 🧮 ║
║            │        │  (blue)  │ (green)│      │  23:41    │         ║
║            │        │          │        │      │  (amber)  │         ║
╚══════════════════════════════════════════════════════════════════╝
```

**Verify**:
- [x] Case number displays: `CJ/1010`
- [x] Client name displays: `oshan`
- [x] Case type badge is blue with text "Criminal"
- [x] Status badge is green with text "Open"
- [x] Risk gauge shows `0`
- [x] Deadline shows `Apr 20, 23:41` with amber/yellow badge
- [x] Three action buttons visible: Eye (👁), Robot (🤖), Calculator (🧮)

---

## ✅ Test 2: Tooltip Functionality

### Steps:
1. Hover over the robot icon (🤖)
2. Wait 0.5 seconds

### Expected Results:
- Tooltip appears above the icon
- Text reads: **"Open AI Case Assistant (F6)"**
- Tooltip has cyan border
- Dark background with cyan text
- Tooltip disappears when mouse moves away

---

## ✅ Test 3: AI Chat Navigation

### Steps:
1. Click the robot icon (🤖) on the dashboard

### Expected Results:
1. **URL Changes**: 
   - From: `http://localhost:5000/cases/dashboard`
   - To: `http://localhost:5000/cases/1#chatContainer`

2. **Page Loads**: Case detail page appears

3. **Auto-Scroll**:
   - Page smoothly scrolls down to chat interface
   - Scroll animation is smooth (not instant)
   - Chat container comes to center of viewport

4. **Visual Highlight**:
   - Chat container gets cyan ring border (4px width)
   - Ring has 50% opacity
   - Ring fades out after 2 seconds

5. **Chat Interface Ready**:
   - Message input box visible
   - Chat history loaded (if any exists)
   - Send button enabled

---

## ✅ Test 4: Context-Aware AI Response

### Steps:
1. After navigating to chat (from Test 3)
2. Type in chat input: **"What are the next steps in this case?"**
3. Click "Send" or press Enter
4. Wait for AI response

### Expected Response Should Include:
- ✅ Reference to **Case CJ/1010**
- ✅ Reference to client **oshan**
- ✅ Mention of **murder case** or **Section 302 IPC**
- ✅ **Urgent deadline warning**: "Court hearing on April 20, 2026 at 23:41"
- ✅ Specific next steps (e.g., gather evidence, prepare witnesses)
- ✅ Not generic legal advice

**Example Expected Response**:
```
Based on Case CJ/1010 for client oshan regarding the murder case under 
Section 302 IPC, here are your immediate next steps:

⚠️ URGENT: You have a critical deadline on April 20, 2026 at 23:41 
(in 2 days). This appears to be a court hearing.

Immediate Actions:
1. Review all evidence collected so far
2. Prepare witness statements
3. Draft defense strategy under Section 302 IPC
4. File any pending motions before the deadline
5. Prepare for the court hearing

[Continues with case-specific advice...]
```

---

## ✅ Test 5: Conversation Persistence

### Steps:
1. Send message: **"What evidence should I collect?"**
2. Get AI response
3. Refresh the page (F5 or Ctrl+R)
4. Scroll to chat interface

### Expected Results:
- [x] Previous conversation still visible
- [x] Both user message and AI response are loaded
- [x] Messages appear in chronological order
- [x] Timestamps visible on messages
- [x] Can continue conversation from where it left off

---

## ✅ Test 6: Document Context Retrieval

### Steps:
1. Upload a document to Case CJ/1010 (if not already uploaded)
2. Go to chat interface
3. Ask: **"Summarize the uploaded documents"**

### Expected Results:
- AI retrieves document content via FAISS
- Response includes specific text from documents
- Citations show: 
  - Document filename
  - Document type
  - Chunk index
- Sources panel shows document references

---

## ✅ Test 7: Deadline Awareness

### Steps:
1. In chat, ask: **"What deadlines do I need to watch?"**

### Expected Response Should Include:
```
Based on your case deadlines:

⚠️ URGENT DEADLINE:
- Court Hearing
- Due: April 20, 2026 at 23:41
- Status: DUE SOON (in 2 days)
- Priority: HIGH

This is your most critical deadline. Make sure you:
1. Prepare all necessary documents
2. Brief your witnesses
3. File any pending motions
4. [More case-specific advice]
```

---

## ✅ Test 8: Tailwind Dashboard (Alternative)

### Steps:
1. Navigate to Tailwind dashboard version
2. Find the case card for "oshan"

### Expected Results:
**Case Card Display**:
```
┌─────────────────────────────────────────┐
│ CRIMINAL                         Open   │
│ CJ/1010                                 │
│ oshan                                   │
│                                         │
│ Risk score                      0.0/100 │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░         │
│                                         │
│ [Open case workspace] [🤖 AI Chat]     │
└─────────────────────────────────────────┘
```

**Verify**:
- [x] Case type at top: `CRIMINAL`
- [x] Case number: `CJ/1010` (bold, white)
- [x] Client: `oshan` (slate-400)
- [x] Status badge: `Open` (emerald)
- [x] Risk bar shows at 0%
- [x] Two buttons: "Open case workspace" and "AI Chat" (with robot icon)
- [x] AI Chat button has cyan color scheme

---

## ✅ Test 9: Responsive Design (Mobile)

### Steps:
1. Open dashboard in mobile view (or resize browser to < 640px)
2. Locate the AI Chat button

### Expected Results:
**Bootstrap Dashboard**:
- Robot icon (🤖) still visible
- Tooltip still works

**Tailwind Dashboard**:
- Robot icon (🤖) visible
- Text "AI Chat" is hidden (icon only)
- Button still clickable

---

## ✅ Test 10: Multiple Cases

### Steps:
1. Create another case (e.g., theft case)
2. Go back to dashboard
3. Verify each case has its own AI Chat icon
4. Click robot icon on different cases

### Expected Results:
- Each case has a robot icon
- Clicking different icons navigates to different case chats
- Each chat has different context (case-specific)
- No conversation mixing between cases

---

## 🎯 Success Criteria

All tests should pass with:
- ✅ Proper case data display
- ✅ Working AI Chat shortcuts
- ✅ Smooth navigation and scrolling
- ✅ Context-aware AI responses
- ✅ Conversation persistence
- ✅ Document retrieval
- ✅ Deadline awareness
- ✅ Responsive design
- ✅ Isolated case conversations

---

## 🚀 Quick Test Command

```bash
# Start server
cd backend
python run.py

# Open browser
http://localhost:5000/cases/dashboard

# Test flow
1. See case "CJ/1010" with robot icon
2. Hover → See tooltip
3. Click → Navigate to chat
4. Ask → Get context-aware response
5. Refresh → See conversation persisted
```

---

**All features implemented and ready to test!** 🎉

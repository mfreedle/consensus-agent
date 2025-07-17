# Manual Test Plan for Socket.IO Follow-up Message Fix

## Test Scenario: Follow-up Message in Existing Session

### Prerequisites
- Deployed app is accessible at: https://consensus-agent.up.railway.app/
- User has valid login credentials

### Test Steps

#### Step 1: Login and Initial Setup
1. Navigate to https://consensus-agent.up.railway.app/
2. Log in with your credentials
3. Ensure you're on the main chat interface

#### Step 2: Send First Message (Should Work)
1. Select a **single model** (e.g., GPT-4o)
2. Type a simple message: "Hello, can you help me with a question?"
3. Click Send
4. **Expected Result**: 
   - Message should send successfully
   - AI should respond
   - No error messages in browser console or UI

#### Step 3: Send Follow-up Message (Previously Failed)
1. **Do NOT navigate away from the session**
2. Type a follow-up message: "Can you tell me more about that?"
3. Click Send
4. **Expected Result**: 
   - Message should send successfully
   - AI should respond
   - NO Socket.IO error
   - NO browser console errors

#### Step 4: Test Session Persistence
1. Navigate to another session or create a new one
2. Go back to the original session (if it's in the sidebar)
3. Send another follow-up message: "Thanks for the help!"
4. **Expected Result**: 
   - Message should work in the existing session
   - Previous conversation history should be visible

#### Step 5: Test Multi-Model Consensus (Regression Test)
1. In the same session or a new one
2. Select **2+ models** (e.g., GPT-4o + Grok)
3. Send a message: "What do you think about renewable energy?"
4. **Expected Result**:
   - Should show consensus thinking indicator
   - Should get consensus response
   - No errors

### Browser Console Monitoring
Open Browser Developer Tools (F12) and monitor the Console tab for:
- ❌ **Red error messages** (especially Socket.IO related)
- ⚠️ **Yellow warnings** (note but may be acceptable)
- ℹ️ **Blue info messages** (normal)

### Success Criteria
✅ **Test PASSES if:**
- All follow-up messages send successfully
- No Socket.IO errors appear in console
- Chat history persists correctly
- Both single model and consensus modes work

❌ **Test FAILS if:**
- Follow-up messages trigger Socket.IO errors
- Messages fail to send after the first one
- Console shows connection or authentication errors

### If Test Fails
1. Check browser console for specific error messages
2. Try refreshing the page and retesting
3. Check if the issue is specific to certain browsers
4. Note the exact sequence of actions that trigger the error

### Additional Browser Testing
Test in multiple browsers if possible:
- Chrome/Edge (Chromium-based)
- Firefox
- Safari (if on Mac)

### Expected Logs in Backend
With the new fix, the backend logs should show:
```
Socket.IO send_message: session_id=123 (type: <class 'int'>), message_length=25, use_consensus=False, models=['gpt-4o']
Socket.IO authenticated user: 1 (test_user)
```

If there are still issues, the logs will show more specific error details.

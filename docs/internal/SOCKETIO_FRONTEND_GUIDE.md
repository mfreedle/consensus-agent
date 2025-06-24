# Socket.IO Frontend Integration - Testing Guide

## Overview

The frontend Socket.IO integration has been successfully implemented with the following features:

- Real-time bidirectional communication with the backend
- Authentication-aware connection management
- Automatic fallback to HTTP API when Socket.IO is unavailable
- Connection status indicators in the UI
- Seamless integration with existing chat interface

## New Components Added

### 1. Socket Service (`src/services/socket.ts`)
- Manages Socket.IO connection lifecycle
- Handles authentication with JWT tokens
- Provides methods for joining sessions and sending messages
- Event listener management for incoming messages and errors

### 2. useSocket Hook (`src/hooks/useSocket.ts`)
- React hook for Socket.IO integration
- Automatic connection/disconnection based on auth state
- Session room management
- Message sending with authentication

### 3. Authentication Context (`src/contexts/AuthContext.tsx`)
- Centralized authentication state management
- Token persistence in localStorage
- User session management across the app

## Key Features

### Real-time Connection Status
- **Header**: Shows real-time connection status with visual indicators
- **Chat Input**: Displays connection status and adapts placeholder text
- **Automatic Fallback**: Gracefully falls back to HTTP API when Socket.IO unavailable

### Message Flow
1. User types message in chat interface
2. If Socket.IO connected: Message sent via WebSocket with authentication
3. If Socket.IO disconnected: Falls back to HTTP API
4. Real-time responses appear instantly when Socket.IO is working
5. Visual indicators show current connection state

### Authentication Integration
- Socket.IO connections authenticated with JWT tokens
- Automatic reconnection when user logs in
- Clean disconnection when user logs out
- Token validation on each message send

## Testing the Integration

### Prerequisites
1. Backend running on `http://localhost:8000` with Socket.IO enabled
2. Frontend running on `http://localhost:3000`

### Test Scenarios

#### 1. Basic Real-time Chat
1. Start both backend and frontend
2. Login to the application
3. Check header shows "Real-time Connected" (green indicator)
4. Send a message - should see immediate response via Socket.IO
5. Open browser dev tools and check console for Socket.IO connection logs

#### 2. Connection Status Testing
1. Start frontend without backend running
2. Login should show "Connecting..." (red indicator) in header
3. Input area should show "Real-time mode unavailable - using HTTP fallback"
4. Start backend - connection should automatically establish
5. Indicators should change to green "Real-time Connected"

#### 3. Authentication Flow
1. Login and verify Socket.IO connects
2. Logout and verify Socket.IO disconnects
3. Login again and verify automatic reconnection
4. Send messages to ensure authentication is working

#### 4. Session Management
1. Create a new chat session
2. Verify Socket.IO joins the session room
3. Switch to different session
4. Verify room switching works correctly

### Debug Information

Check browser console for these logs:
- `Socket.IO connected` - Successful connection
- `Joining session room: [sessionId]` - Session room joining
- `Sending message via Socket.IO: [message]` - Message sending
- `Received Socket.IO message:` - Incoming messages

### Backend Socket.IO Events

The frontend listens for these events:
- `connect` - Connection established
- `disconnect` - Connection lost
- `new_message` - Incoming chat message
- `error` - Error messages

The frontend emits these events:
- `join` - Join session room
- `send_message` - Send chat message

## Next Steps

1. **Error Handling**: Add user-friendly error notifications
2. **Typing Indicators**: Show when other users are typing
3. **Message Status**: Show delivery/read receipts
4. **Reconnection Logic**: Improve automatic reconnection handling
5. **Performance**: Optimize message synchronization and duplicate prevention

## Troubleshooting

### Common Issues

1. **"Socket.IO not connecting"**
   - Check backend is running on correct port (8000)
   - Verify CORS settings in backend
   - Check browser console for connection errors

2. **"Messages not sending"**
   - Verify authentication token is valid
   - Check session ID is set correctly
   - Ensure Socket.IO connection is established

3. **"Duplicate messages"**
   - This is expected during development with mock data
   - Real backend integration will resolve this

4. **"TypeScript errors"**
   - Run `npm run build` to check for compilation errors
   - Ensure all types are properly imported

The Socket.IO frontend integration is now complete and ready for testing with the backend!

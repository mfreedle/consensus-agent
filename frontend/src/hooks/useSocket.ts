import { useEffect, useRef, useCallback, useState } from 'react';
import { socketService } from '../services/socket';
import { SocketMessage, SocketError, ProcessingStatus } from '../types';

interface UseSocketProps {
  isAuthenticated: boolean;
  token?: string;
  sessionId?: string | null;
  onNewMessage?: (message: SocketMessage) => void;
  onError?: (error: SocketError) => void;
  onSessionCreated?: (data: { session_id: number; title: string }) => void;
  onProcessingStatus?: (status: ProcessingStatus) => void;
}

export const useSocket = ({
  isAuthenticated,
  token,
  sessionId,
  onNewMessage,
  onError,
  onSessionCreated,
  onProcessingStatus,
}: UseSocketProps) => {
  const socketRef = useRef(socketService);
  const currentSessionRef = useRef<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Update connection status when socket status changes
  useEffect(() => {
    const checkConnection = () => {
      const connected = socketRef.current.isSocketConnected();
      setIsConnected(connected);
    };

    // Check initial state
    checkConnection();

    // Set up interval to check connection status
    const interval = setInterval(checkConnection, 1000);

    return () => clearInterval(interval);
  }, []);
  // Connect to socket when authenticated
  useEffect(() => {
    const socketInstance = socketRef.current;
    
    console.log('useSocket effect triggered:', { isAuthenticated, token: !!token });
    
    if (isAuthenticated && token) {
      console.log('Connecting to Socket.IO...');
      const socket = socketInstance.connect(token);

      // Set up connection event listeners
      socket.on('connect', () => {
        console.log('Socket connected, updating state');
        setIsConnected(true);
      });

      socket.on('disconnect', () => {
        console.log('Socket disconnected, updating state');
        setIsConnected(false);
      });

      // Set up message listener
      if (onNewMessage) {
        socketInstance.onNewMessage(onNewMessage);
      }

      // Set up error listener
      if (onError) {
        socketInstance.onError(onError);
      }

      // Set up session created listener
      if (onSessionCreated) {
        socketInstance.onSessionCreated(onSessionCreated);
      }

      // Set up processing status listener
      if (onProcessingStatus) {
        socketInstance.onProcessingStatus(onProcessingStatus);
      }

      return () => {
        console.log('Cleaning up Socket.IO listeners...');
        socketInstance.removeAllListeners();
        socket.off('connect');
        socket.off('disconnect');
      };
    } else {
      console.log('Not authenticated or no token, disconnecting...');
      // Disconnect when not authenticated
      socketInstance.disconnect();
      setIsConnected(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, token]); // onNewMessage and onError are handled in separate effect
  
  // Separate effect to handle callback updates without reconnecting
  useEffect(() => {
    const socketInstance = socketRef.current;
    
    if (socketInstance.isSocketConnected()) {
      // Update listeners when callbacks change
      socketInstance.removeAllListeners();
      if (onNewMessage) {
        socketInstance.onNewMessage(onNewMessage);
      }
      if (onError) {
        socketInstance.onError(onError);
      }
      if (onSessionCreated) {
        socketInstance.onSessionCreated(onSessionCreated);
      }
      if (onProcessingStatus) {
        socketInstance.onProcessingStatus(onProcessingStatus);
      }
    }
  }, [onNewMessage, onError, onSessionCreated, onProcessingStatus]);

  // Join session room when session changes
  useEffect(() => {
    if (isAuthenticated && socketRef.current.isSocketConnected() && sessionId) {
      // Leave previous session room if exists
      if (currentSessionRef.current && currentSessionRef.current !== sessionId) {
        // Note: We don't have a leave event in the backend, but Socket.IO will handle it
        console.log(`Leaving session room: ${currentSessionRef.current}`);
      }

      // Join new session room
      console.log(`Joining session room: ${sessionId}`);
      socketRef.current.joinSession(sessionId);
      currentSessionRef.current = sessionId;
    }
  }, [isAuthenticated, sessionId]);
  // Send message function
  const sendMessage = useCallback((message: string, attachedFileIds?: string[], useConsensus?: boolean, selectedModels?: string[], userName?: string) => {
    if (isAuthenticated && token && socketRef.current.isSocketConnected()) {
      console.log(`Sending message via Socket.IO: ${message}`, 
        attachedFileIds?.length ? `with ${attachedFileIds.length} attached files` : "",
        `use_consensus: ${useConsensus}, models: ${selectedModels?.join(', ')}, user: ${userName}`);
      socketRef.current.sendMessage(sessionId || null, message, token, attachedFileIds, useConsensus, selectedModels, userName);
      return true;
    } else {
      console.warn('Cannot send message: not connected or missing credentials');
      return false;
    }
  }, [isAuthenticated, token, sessionId]);

  // Cleanup on unmount
  useEffect(() => {
    const socketInstance = socketRef.current;
    return () => {
      socketInstance.disconnect();
    };
  }, []);

  return {
    sendMessage,
    isConnected: () => isConnected,
    socket: socketRef.current.getSocket(),
  };
};

import { io, Socket } from 'socket.io-client';
import { SocketMessage, SocketError, ProcessingStatus } from '../types';

// Use environment variable or current domain for socket connection
const SOCKET_URL = process.env.REACT_APP_API_URL 
  ? process.env.REACT_APP_API_URL.replace('/api', '') 
  : (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000');

class SocketService {
  private socket: Socket | null = null;
  private isConnected = false;
  private isConnecting = false;

  connect(token?: string): Socket {
    if (this.socket && this.isConnected) {
      console.log('Socket already connected, returning existing socket');
      return this.socket;
    }

    if (this.isConnecting) {
      console.log('Connection already in progress, waiting...');
      return this.socket!;
    }

    this.isConnecting = true;
    console.log('Creating new Socket.IO connection...');
    console.log('Socket URL:', SOCKET_URL);

    // Disconnect any existing socket first
    if (this.socket) {
      this.socket.disconnect();
    }
    this.socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      autoConnect: false,
      auth: token ? { token } : undefined,
    });
    this.socket.on('connect', () => {
      console.log('Socket.IO connected with ID:', this.socket?.id);
      this.isConnected = true;
      this.isConnecting = false;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket.IO disconnected, reason:', reason);
      this.isConnected = false;
      this.isConnecting = false;
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error);
      this.isConnected = false;
      this.isConnecting = false;
    });

    console.log('Attempting to connect...');
    this.socket.connect();
    return this.socket;
  }
  disconnect(): void {
    if (this.socket) {
      console.log('Disconnecting Socket.IO...');
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  joinSession(sessionId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('join', { session_id: sessionId });
    }
  }

  sendMessage(sessionId: string | null, message: string, token: string, attachedFileIds?: string[], useConsensus?: boolean, selectedModels?: string[], userName?: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('send_message', {
        session_id: sessionId,
        message,
        token,
        attached_file_ids: attachedFileIds || [],
        use_consensus: useConsensus,
        selected_models: selectedModels || [],
        user_name: userName || ""
      });
    }
  }

  onNewMessage(callback: (message: SocketMessage) => void): void {
    if (this.socket) {
      this.socket.on('new_message', callback);
    }
  }

  onProcessingStatus(callback: (status: ProcessingStatus) => void): void {
    if (this.socket) {
      this.socket.on('processing_status', callback);
    }
  }

  onError(callback: (error: SocketError) => void): void {
    if (this.socket) {
      this.socket.on('error', callback);
    }
  }

  onSessionCreated(callback: (data: { session_id: number; title: string }) => void): void {
    if (this.socket) {
      this.socket.on('session_created', callback);
    }
  }

  removeAllListeners(): void {
    if (this.socket) {
      this.socket.removeAllListeners('new_message');
      this.socket.removeAllListeners('error');
      this.socket.removeAllListeners('session_created');
      this.socket.removeAllListeners('processing_status');
    }
  }

  getSocket(): Socket | null {
    return this.socket;
  }

  isSocketConnected(): boolean {
    return this.isConnected && this.socket?.connected === true;
  }
}

export const socketService = new SocketService();
export default socketService;

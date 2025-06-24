import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContext";
import ChatApp from "./components/ChatApp";
import "./App.css";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <div className="App min-h-screen bg-bg-dark">
          <ChatApp />
        </div>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;

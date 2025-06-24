import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChatApp from "./components/ChatApp";
import "./App.css";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="App min-h-screen bg-bg-dark">
        <ChatApp />
      </div>
    </QueryClientProvider>
  );
}

export default App;

import React, { useState } from "react";
import { FileText, MessageSquare, Sparkles } from "lucide-react";

export const GoogleDriveLLMDemo: React.FC = () => {
  const [demoStep, setDemoStep] = useState(0);

  const demoSteps = [
    {
      title: "Connect Google Drive",
      description:
        "First, connect your Google Drive account to enable LLM file operations.",
      icon: <FileText className="h-6 w-6 text-blue-500" />,
      action: "Connect in the sidebar under Google Drive section",
    },
    {
      title: "Chat with LLMs about your files",
      description:
        "Ask the AI to read, edit, or create Google Drive documents.",
      icon: <MessageSquare className="h-6 w-6 text-green-500" />,
      action: "Try: 'Read my latest Google Doc and summarize it'",
    },
    {
      title: "Watch the magic happen",
      description:
        "LLMs can now access your Drive files, make edits, and create new documents.",
      icon: <Sparkles className="h-6 w-6 text-purple-500" />,
      action: "Try: 'Create a meeting agenda in Google Docs'",
    },
  ];

  const examplePrompts = [
    "List my Google Drive files",
    "Read my latest Google Doc and summarize the key points",
    "Create a new Google Doc with a project proposal template",
    "Edit my spreadsheet to add a new budget category",
    "Create a presentation about our Q4 results",
    "Find all documents containing 'meeting notes' and create a summary",
    "Update my task list in Google Sheets with new priorities",
    "Create a collaborative document for team brainstorming",
  ];

  return (
    <div className="google-drive-llm-demo max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Google Drive + LLM Integration
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Your AI assistants can now read, edit, and create Google Drive files
          seamlessly.
        </p>
      </div>

      {/* Demo Steps */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {demoSteps.map((step, index) => (
          <div
            key={index}
            className={`p-6 rounded-lg border transition-all cursor-pointer ${
              demoStep === index
                ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
            }`}
            onClick={() => setDemoStep(index)}
          >
            <div className="flex items-center space-x-3 mb-3">
              {step.icon}
              <h3 className="font-semibold text-gray-900 dark:text-white">
                {step.title}
              </h3>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
              {step.description}
            </p>
            <p className="text-xs font-medium text-blue-600 dark:text-blue-400">
              {step.action}
            </p>
          </div>
        ))}
      </div>

      {/* Example Prompts */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Try These Prompts:
        </h3>
        <div className="grid md:grid-cols-2 gap-3">
          {examplePrompts.map((prompt, index) => (
            <div
              key={index}
              className="flex items-start space-x-3 p-3 bg-white dark:bg-gray-700 rounded-md border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 transition-colors cursor-pointer"
              onClick={() => {
                navigator.clipboard.writeText(prompt);
                // Could trigger chat input here
              }}
            >
              <MessageSquare className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                "{prompt}"
              </span>
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
          Click any prompt to copy it, then paste in the chat to try it out!
        </p>
      </div>

      {/* Features List */}
      <div className="mt-8 grid md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
            What LLMs Can Do:
          </h4>
          <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
            <li>✅ List and browse your Google Drive files</li>
            <li>✅ Read content from Google Docs, Sheets, and Slides</li>
            <li>✅ Edit existing documents with new content</li>
            <li>✅ Create new files with custom content</li>
            <li>✅ Add slides to presentations</li>
            <li>✅ Update spreadsheet data and formulas</li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
            Integration Features:
          </h4>
          <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
            <li>🔐 Secure OAuth authentication</li>
            <li>🔄 Real-time file access in chat context</li>
            <li>🛡️ Permission-based access control</li>
            <li>⚡ Function calling for seamless integration</li>
            <li>📱 Mobile-friendly sidebar interface</li>
            <li>🎯 Smart file type detection and handling</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

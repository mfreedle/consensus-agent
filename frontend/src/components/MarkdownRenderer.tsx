import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownRendererProps {
  content: string;
  className?: string;
  size?: "sm" | "base" | "lg";
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  className = "",
  size = "sm",
}) => {
  const sizeClasses = {
    sm: {
      h1: "text-base font-semibold mb-2 mt-3",
      h2: "text-sm font-semibold mb-2 mt-3",
      h3: "text-sm font-semibold mb-1 mt-2",
      p: "mb-2 leading-relaxed text-sm",
      list: "text-sm leading-relaxed",
      code: "text-xs",
      table: "text-xs",
    },
    base: {
      h1: "text-lg font-semibold mb-2 mt-3",
      h2: "text-base font-semibold mb-2 mt-3",
      h3: "text-base font-semibold mb-1 mt-2",
      p: "mb-3 leading-relaxed",
      list: "leading-relaxed",
      code: "text-sm",
      table: "text-sm",
    },
    lg: {
      h1: "text-xl font-semibold mb-3 mt-4",
      h2: "text-lg font-semibold mb-3 mt-4",
      h3: "text-lg font-semibold mb-2 mt-3",
      p: "mb-4 leading-relaxed text-base",
      list: "text-base leading-relaxed",
      code: "text-base",
      table: "text-base",
    },
  };

  const sizes = sizeClasses[size];

  return (
    <div className={`${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className={`${sizes.h1} text-gray-100`}>{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className={`${sizes.h2} text-gray-100`}>{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className={`${sizes.h3} text-gray-100`}>{children}</h3>
          ),
          p: ({ children }) => <p className={sizes.p}>{children}</p>,
          ul: ({ children }) => (
            <ul className="list-disc ml-4 mb-2 space-y-1">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal ml-4 mb-2 space-y-1">{children}</ol>
          ),
          li: ({ children }) => <li className={sizes.list}>{children}</li>,
          code: ({ children, className }) => {
            const isInline = !className?.includes("language-");
            return (
              <code
                className={
                  isInline
                    ? `bg-gray-700 text-cyan-400 px-1 py-0.5 rounded ${sizes.code}`
                    : `block bg-gray-700 text-cyan-400 p-2 rounded ${sizes.code} overflow-x-auto`
                }
              >
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre
              className={`bg-gray-700 p-2 rounded ${sizes.code} overflow-x-auto mb-2`}
            >
              {children}
            </pre>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-gray-500 pl-3 italic text-gray-400 mb-2">
              {children}
            </blockquote>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-100">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-200">{children}</em>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-cyan-400 hover:text-cyan-300 underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          table: ({ children }) => (
            <table
              className={`w-full border-collapse border border-gray-600 ${sizes.table} mb-2`}
            >
              {children}
            </table>
          ),
          th: ({ children }) => (
            <th className="border border-gray-600 bg-gray-700 p-2 text-left font-medium">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-gray-600 p-2">{children}</td>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;

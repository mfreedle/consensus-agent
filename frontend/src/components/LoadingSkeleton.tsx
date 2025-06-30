import React from "react";

interface LoadingSkeletonProps {
  variant?: "text" | "header" | "button" | "avatar" | "card" | "chat-message";
  lines?: number;
  className?: string;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = "text",
  lines = 1,
  className = "",
}) => {
  const renderSkeleton = () => {
    switch (variant) {
      case "header":
        return <div className={`skeleton skeleton-header ${className}`} />;

      case "button":
        return <div className={`skeleton skeleton-button ${className}`} />;

      case "avatar":
        return <div className={`skeleton skeleton-avatar ${className}`} />;

      case "card":
        return (
          <div className={`skeleton skeleton-card ${className}`}>
            <div className="skeleton skeleton-header mb-3" />
            <div className="skeleton skeleton-text mb-2" />
            <div
              className="skeleton skeleton-text mb-2"
              style={{ width: "80%" }}
            />
            <div
              className="skeleton skeleton-text-sm"
              style={{ width: "60%" }}
            />
          </div>
        );

      case "chat-message":
        return (
          <div className={`flex space-x-3 ${className}`}>
            <div className="skeleton skeleton-avatar" />
            <div className="flex-1">
              <div
                className="skeleton skeleton-text mb-2"
                style={{ width: "90%" }}
              />
              <div
                className="skeleton skeleton-text mb-2"
                style={{ width: "75%" }}
              />
              <div
                className="skeleton skeleton-text-sm"
                style={{ width: "50%" }}
              />
            </div>
          </div>
        );

      case "text":
      default:
        return (
          <>
            {Array.from({ length: lines }).map((_, index) => (
              <div
                key={index}
                className={`skeleton skeleton-text ${className}`}
                style={{
                  width: index === lines - 1 ? "70%" : "100%",
                }}
              />
            ))}
          </>
        );
    }
  };

  return (
    <div role="status" aria-label="Loading content">
      {renderSkeleton()}
    </div>
  );
};

export default LoadingSkeleton;

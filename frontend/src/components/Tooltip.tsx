import React, { useState, useRef, useEffect } from "react";

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  delay?: number;
  className?: string;
}

const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = "top",
  delay = 500,
  className = "",
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const showTooltip = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    const id = setTimeout(() => {
      setIsVisible(true);
    }, delay);
    setTimeoutId(id);
  };

  const hideTooltip = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      setTimeoutId(null);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [timeoutId]);

  const getPositionClasses = () => {
    switch (position) {
      case "bottom":
        return "top-full left-1/2 transform -translate-x-1/2 mt-2";
      case "left":
        return "right-full top-1/2 transform -translate-y-1/2 mr-2";
      case "right":
        return "left-full top-1/2 transform -translate-y-1/2 ml-2";
      case "top":
      default:
        return "bottom-full left-1/2 transform -translate-x-1/2 mb-2";
    }
  };

  const getArrowClasses = () => {
    switch (position) {
      case "bottom":
        return "bottom-full left-1/2 transform -translate-x-1/2 border-b-color: var(--bg-dark-secondary)";
      case "left":
        return "left-full top-1/2 transform -translate-y-1/2 border-l-color: var(--bg-dark-secondary)";
      case "right":
        return "right-full top-1/2 transform -translate-y-1/2 border-r-color: var(--bg-dark-secondary)";
      case "top":
      default:
        return "top-full left-1/2 transform -translate-x-1/2 border-t-color: var(--bg-dark-secondary)";
    }
  };

  return (
    <div
      className={`tooltip relative inline-block ${className}`}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {children}

      {isVisible && (
        <div
          ref={tooltipRef}
          className={`tooltip-content absolute z-50 ${getPositionClasses()}`}
          role="tooltip"
          aria-hidden={!isVisible}
        >
          {content}

          {/* Arrow */}
          <div
            className={`absolute w-0 h-0 ${getArrowClasses()}`}
            style={{
              borderWidth: "4px",
              borderStyle: "solid",
              borderColor:
                position === "top"
                  ? "var(--bg-dark-secondary) transparent transparent transparent"
                  : position === "bottom"
                  ? "transparent transparent var(--bg-dark-secondary) transparent"
                  : position === "left"
                  ? "transparent transparent transparent var(--bg-dark-secondary)"
                  : "transparent var(--bg-dark-secondary) transparent transparent",
            }}
          />
        </div>
      )}
    </div>
  );
};

export default Tooltip;

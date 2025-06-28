import React, { useRef, useEffect, useState, useCallback } from "react";
import { useViewportHeight } from "../hooks/useResponsive";

interface MobileOptimizedTextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  onHeightChange?: (height: number) => void;
}

export const MobileOptimizedTextarea: React.FC<
  MobileOptimizedTextareaProps
> = ({ onHeightChange, className = "", ...props }) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const viewportHeight = useViewportHeight();

  // Auto-resize textarea
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    const scrollHeight = textarea.scrollHeight;
    const maxHeight = Math.min(120, viewportHeight * 0.3); // Max 30% of viewport or 120px

    textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;

    if (onHeightChange) {
      onHeightChange(Math.min(scrollHeight, maxHeight));
    }
  }, [viewportHeight, onHeightChange]);

  useEffect(() => {
    adjustHeight();
  }, [props.value, adjustHeight]);

  // Handle iOS keyboard behavior
  useEffect(() => {
    if (!isFocused) return;

    const handleResize = () => {
      // Small delay to let the keyboard animation complete
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
        }
      }, 300);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [isFocused]);

  const handleFocus = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    setIsFocused(true);
    if (props.onFocus) props.onFocus(e);
  };

  const handleBlur = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    setIsFocused(false);
    if (props.onBlur) props.onBlur(e);
  };

  const handleInput = (e: React.FormEvent<HTMLTextAreaElement>) => {
    adjustHeight();
    if (props.onInput) props.onInput(e);
  };

  return (
    <textarea
      ref={textareaRef}
      className={`resize-none overflow-hidden ${className}`}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onInput={handleInput}
      {...props}
    />
  );
};

export default MobileOptimizedTextarea;

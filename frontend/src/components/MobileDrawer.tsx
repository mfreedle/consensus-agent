import React, { useState, useEffect, useRef } from "react";
import { X, ChevronRight } from "lucide-react";

interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
}

export const MobileDrawer: React.FC<MobileDrawerProps> = ({
  isOpen,
  onClose,
  children,
  className = "",
}) => {
  const [startX, setStartX] = useState<number | null>(null);
  const [currentX, setCurrentX] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);

  // Handle touch events for swipe-to-close
  const handleTouchStart = (e: React.TouchEvent) => {
    setStartX(e.touches[0].clientX);
    setIsDragging(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!startX || !isDragging) return;
    setCurrentX(e.touches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!startX || !currentX || !isDragging) {
      setIsDragging(false);
      setStartX(null);
      setCurrentX(null);
      return;
    }

    const diffX = startX - currentX;
    const threshold = 100; // Minimum swipe distance

    if (diffX > threshold) {
      onClose();
    }

    setIsDragging(false);
    setStartX(null);
    setCurrentX(null);
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        ref={drawerRef}
        className={`
          fixed inset-y-0 right-0 z-50 w-80 sm:w-96 bg-bg-dark-secondary 
          border-l border-primary-teal/20 transform transition-transform 
          duration-300 ease-in-out flex flex-col lg:hidden
          ${isOpen ? "translate-x-0" : "translate-x-full"}
          ${className}
        `}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Swipe indicator */}
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-2 bg-primary-teal/20 rounded-l-lg p-1">
          <ChevronRight className="w-3 h-3 text-primary-cyan" />
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-primary-teal/10 transition-colors z-10"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>

        {/* Content */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </div>
    </>
  );
};

export default MobileDrawer;

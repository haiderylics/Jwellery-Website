import React, { useEffect, useState } from "react";
import { Sparkles, X } from "lucide-react";
import { Popup } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { ResponsiveImage } from "@/components/ui/ResponsiveImage";

const POPUP_SEEN_KEY = "zirconia_popup_seen_session";

export interface ActivePopupModalProps {
  popup: Popup | null;
  onNavigate: (path: string) => void;
}

export const ActivePopupModal: React.FC<ActivePopupModalProps> = ({ popup, onNavigate }) => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!popup) return;

    // Check if user already saw popup in this browser session
    const seen = sessionStorage.getItem(POPUP_SEEN_KEY);
    if (seen) return;

    const delayMs = (popup.delay_seconds || 3) * 1000;
    const timer = setTimeout(() => {
      setIsOpen(true);
      sessionStorage.setItem(POPUP_SEEN_KEY, "true");
    }, delayMs);

    return () => clearTimeout(timer);
  }, [popup]);

  useEffect(() => {
    if (!isOpen) return;
    const previousOverflow = document.body.style.overflow;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsOpen(false);
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [isOpen]);

  if (!isOpen || !popup) return null;

  const handleCta = () => {
    setIsOpen(false);
    if (popup.cta_url) {
      if (popup.cta_url.startsWith("/")) {
        onNavigate(popup.cta_url);
      } else {
        window.open(popup.cta_url, "_blank", "noopener,noreferrer");
      }
    }
  };

  return (
    <div
      className="modal-backdrop popup-backdrop"
      onClick={() => setIsOpen(false)}
      role="dialog"
      aria-modal="true"
      aria-labelledby="popup-title"
      aria-describedby="popup-message"
    >
      <div className="popup-modal-content" onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          className="popup-close-btn"
          onClick={() => setIsOpen(false)}
          aria-label="Close special announcement"
          autoFocus
        >
          <X size={20} />
        </button>

        {popup.image_url && (
          <div className="popup-image-wrapper">
            <ResponsiveImage
              src={popup.image_url}
              alt={popup.title}
              aspectRatio="16/9"
              priority={true}
            />
          </div>
        )}

        <div className="popup-body">
          <div className="popup-badge">
            <Sparkles size={14} />
            <span>SPECIAL INVITATION</span>
          </div>
          <h2 id="popup-title" className="popup-title">{popup.title}</h2>
          <p id="popup-message" className="popup-message">{popup.message}</p>

          <div className="popup-actions">
            {popup.cta_label ? (
              <Button variant="primary" size="md" onClick={handleCta} className="w-full">
                {popup.cta_label}
              </Button>
            ) : (
              <Button variant="primary" size="md" onClick={() => setIsOpen(false)} className="w-full">
                Explore Collection
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

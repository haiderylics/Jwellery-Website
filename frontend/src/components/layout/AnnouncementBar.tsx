import React from "react";
import { Sparkles } from "lucide-react";
import { Promotion } from "@/types/api";

export interface AnnouncementBarProps {
  announcements: Promotion[];
  onNavigate: (path: string) => void;
}

export const AnnouncementBar: React.FC<AnnouncementBarProps> = ({
  announcements,
  onNavigate,
}) => {
  if (!announcements || announcements.length === 0) return null;

  const topPromo = announcements[0];
  const message = topPromo.announcement_text || topPromo.title;

  const handleClick = () => {
    if (topPromo.cta_url) {
      if (topPromo.cta_url.startsWith("/")) {
        onNavigate(topPromo.cta_url);
      } else {
        window.open(topPromo.cta_url, "_blank", "noopener,noreferrer");
      }
    }
  };

  return (
    <aside className="announcement-bar" role="region" aria-label="Announcement">
      <div className="announcement-content">
        <Sparkles size={14} className="announcement-icon" />
        <span className="announcement-text">{message}</span>
        {topPromo.cta_label && (
          <button
            type="button"
            className="announcement-cta"
            onClick={handleClick}
          >
            {topPromo.cta_label} &rarr;
          </button>
        )}
      </div>
    </aside>
  );
};

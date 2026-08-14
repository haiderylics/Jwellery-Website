import React, { useState } from "react";
import { AlertCircle, Film } from "lucide-react";
import { ProductVideo } from "@/types/api";

export interface ProductVideoPlayerProps {
  video: ProductVideo;
  className?: string;
}

export const ProductVideoPlayer: React.FC<ProductVideoPlayerProps> = ({ video, className = "" }) => {
  const [loadError, setLoadError] = useState(false);

  if (!video.video_url) return null;

  return (
    <div className={`product-video-player-container ${className}`}>
      <div className="video-header">
        <Film size={16} className="video-icon" />
        <span className="video-title">{video.title || "Atelier Video Demonstration"}</span>
      </div>

      {loadError ? (
        <div className="video-error-box">
          <AlertCircle size={20} className="error-icon" />
          <span>Video demonstration currently unavailable.</span>
        </div>
      ) : (
        <video
          controls
          playsInline
          preload="metadata"
          controlsList="nodownload"
          className="product-video-element"
          onError={() => setLoadError(true)}
          aria-label={video.title || "Product video demonstration"}
        >
          <source src={video.video_url} type="video/mp4" />
          <source src={video.video_url} type="video/webm" />
          Your browser does not support HTML5 video playback.
        </video>
      )}
    </div>
  );
};

import React, { useState } from "react";
import { Sparkles } from "lucide-react";
import { ProductImage } from "@/types/api";
import { useSiteSettings } from "@/context/SiteSettingsContext";

export interface ResponsiveImageProps {
  image?:
    | ProductImage
    | {
        image_url?: string | null;
        thumbnail_url?: string | null;
        medium_url?: string | null;
        large_url?: string | null;
        alt_text?: string;
      }
    | null;
  src?: string | null;
  alt?: string;
  className?: string;
  aspectRatio?: "1/1" | "4/3" | "16/9" | "auto";
  priority?: boolean;
  sizes?: string;
  fallbackText?: string;
}

export const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  image,
  src,
  alt,
  className = "",
  aspectRatio = "1/1",
  priority = false,
  sizes = "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw",
  fallbackText,
}) => {
  const [hasError, setHasError] = useState(false);
  const { brandName } = useSiteSettings();

  const mainSrc = src || image?.image_url;
  const thumbSrc = image?.thumbnail_url;
  const medSrc = image?.medium_url;
  const lrgSrc = image?.large_url;
  const altText =
    alt ||
    image?.alt_text ||
    "Fine Jewellery Piece";

  const displayFallbackText = (
    fallbackText ||
    brandName ||
    "FINE JEWELLERY"
  ).toUpperCase();

  // Build responsive srcSet if variant URLs are present
  const srcSetEntries: string[] = [];
  if (thumbSrc) srcSetEntries.push(`${thumbSrc} 300w`);
  if (medSrc) srcSetEntries.push(`${medSrc} 800w`);
  if (lrgSrc) srcSetEntries.push(`${lrgSrc} 1600w`);
  const srcSet = srcSetEntries.length > 0 ? srcSetEntries.join(", ") : undefined;

  if (!mainSrc || hasError) {
    return (
      <div
        className={`responsive-image-placeholder aspect-${aspectRatio.replace("/", "-")} ${className}`}
      >
        <Sparkles size={24} className="placeholder-sparkle" />
        <span className="placeholder-brand">{displayFallbackText}</span>
      </div>
    );
  }

  return (
    <div
      className={`responsive-image-wrapper aspect-${aspectRatio.replace("/", "-")} ${className}`}
    >
      <img
        src={medSrc || mainSrc}
        srcSet={srcSet}
        sizes={sizes}
        alt={altText}
        loading={priority ? "eager" : "lazy"}
        fetchPriority={priority ? "high" : "auto"}
        decoding="async"
        onError={() => setHasError(true)}
        className="responsive-img"
      />
    </div>
  );
};

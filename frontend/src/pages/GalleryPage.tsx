import React, { useEffect, useState } from "react";
import { GalleryItem } from "@/types/api";
import { api } from "@/services/api";
import { ErrorState } from "@/components/ui/Feedback";
import { ResponsiveImage } from "@/components/ui/ResponsiveImage";

export const GalleryPage: React.FC = () => {
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("");

  useEffect(() => {
    async function loadGallery() {
      try {
        setLoading(true);
        const data = await api.getGallery(activeTab || undefined);
        setItems(data.results);
      } catch (err: any) {
        setError(err?.message || "Failed to load gallery items.");
      } finally {
        setLoading(false);
      }
    }
    loadGallery();
  }, [activeTab]);

  return (
    <div className="page-container gallery-page">
      <div className="page-header">
        <span className="section-kicker">CURATED EXHIBITIONS &amp; MOMENTS</span>
        <h1 className="page-title">Brand Moments &amp; Expos</h1>
        <p className="page-subtitle">
          Capturing our presence at prestigious jewellery exhibitions, masterclasses, and atelier moments.
        </p>
        <div className="title-divider" />
      </div>

      {/* Filter Tabs */}
      <div className="gallery-tabs-bar" role="tablist">
        <button
          type="button"
          className={`gallery-tab ${!activeTab ? "active" : ""}`}
          onClick={() => setActiveTab("")}
        >
          All Moments
        </button>
        <button
          type="button"
          className={`gallery-tab ${activeTab === "exhibition" ? "active" : ""}`}
          onClick={() => setActiveTab("exhibition")}
        >
          Exhibitions &amp; Expos
        </button>
        <button
          type="button"
          className={`gallery-tab ${activeTab === "seminar" ? "active" : ""}`}
          onClick={() => setActiveTab("seminar")}
        >
          Seminars &amp; Workshops
        </button>
        <button
          type="button"
          className={`gallery-tab ${activeTab === "brand" ? "active" : ""}`}
          onClick={() => setActiveTab("brand")}
        >
          Atelier Moments
        </button>
      </div>

      {loading ? (
        <div className="gallery-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="gallery-card skeleton" style={{ minHeight: "260px" }} />
          ))}
        </div>
      ) : error ? (
        <ErrorState message={error} />
      ) : items.length === 0 ? (
        <p className="text-center text-muted">No exhibition moments found under this category.</p>
      ) : (
        <div className="gallery-grid">
          {items.map((item) => (
            <div key={item.id} className="gallery-card">
              <ResponsiveImage
                image={item}
                alt={item.title}
                aspectRatio="4/3"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
              />
              <div className="gallery-card-meta">
                <span className="gallery-type-badge">{item.item_type.toUpperCase()}</span>
                <h4>{item.title}</h4>
                {item.caption && <p>{item.caption}</p>}
                {item.event_date && <span className="gallery-date">{item.event_date}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

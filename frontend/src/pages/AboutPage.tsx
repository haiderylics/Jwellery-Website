import React, { useEffect, useState } from "react";
import { ArrowRight, Award, Compass, Gem, MessageCircle, ShieldCheck, Sparkles } from "lucide-react";
import { AboutSection } from "@/types/api";
import { api } from "@/services/api";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/Feedback";
import { ResponsiveImage } from "@/components/ui/ResponsiveImage";

export interface AboutPageProps {
  onNavigate: (path: string) => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ onNavigate }) => {
  const [about, setAbout] = useState<AboutSection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAbout() {
      try {
        setLoading(true);
        const data = await api.getAbout();
        setAbout(data);
      } catch (err: any) {
        setError(err?.message || "Failed to load brand narrative.");
      } finally {
        setLoading(false);
      }
    }
    loadAbout();
  }, []);

  return (
    <div className="page-container about-page">
      {/* Editorial Header */}
      <div className="about-hero">
        <span className="section-kicker">HERITAGE &amp; ATELIER CRAFTSMANSHIP</span>
        <h1 className="about-page-title">{about?.title || "A Legacy of Timeless Goldsmithing"}</h1>
        {about?.subtitle && <p className="about-page-subtitle">{about.subtitle}</p>}
        <div className="title-divider" />
      </div>

      {loading ? (
        <div className="about-skeleton-container">
          <div className="skeleton h-64 w-full" />
          <div className="skeleton h-48 w-full mt-6" />
        </div>
      ) : error ? (
        <ErrorState message={error} />
      ) : (
        <div className="about-content-body">
          {/* Main Story & Image Split */}
          <div className="about-narrative-split">
            <div className="narrative-text-box">
              <span className="narrative-label">THE ATELIER PHILOSOPHY</span>
              <h2 className="narrative-heading">Devotion to Purity, Proportion &amp; Radiance</h2>
              <p className="narrative-paragraph">
                {about?.story_text ||
                  "Founded with a passion for architectural purity and traditional heritage, Zirconia Fine Jewels creates bespoke pieces in hallmarked 22K/18K gold and certified gemstones. Every piece represents hours of dedicated mastercraft in our private atelier."}
              </p>
              <div className="narrative-quote">
                <p>
                  &ldquo;True luxury is not merely worn; it is inherited. We forge heirlooms that transcend time and carry intimate family memories across generations.&rdquo;
                </p>
                <cite>&mdash; Atelier Master Goldsmith</cite>
              </div>
            </div>

            <div className="narrative-media-box">
              {about?.image_url ? (
                <div className="narrative-image-frame">
                  <ResponsiveImage
                    src={about.image_url}
                    alt={about.title || "Atelier Mastercraft"}
                    aspectRatio="4/3"
                    className="narrative-img"
                  />
                  <div className="frame-corner frame-tl" />
                  <div className="frame-corner frame-br" />
                </div>
              ) : (
                <div className="narrative-fallback-frame">
                  <Sparkles size={36} className="narrative-fallback-sparkle" />
                  <span className="brand-monogram">Z</span>
                  <span className="fallback-tag">HAUTE JOAILLERIE ATELIER</span>
                </div>
              )}
            </div>
          </div>

          {/* Pillars of Excellence */}
          <div className="about-pillars-section">
            <div className="section-header text-center">
              <span className="section-kicker">OUR STANDARDS</span>
              <h2 className="section-title">The Four Pillars of Excellence</h2>
              <div className="title-divider" />
            </div>

            <div className="pillars-grid">
              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <Gem size={28} />
                </div>
                <h3>Certified Pure Stones</h3>
                <p>
                  Each diamond, ruby, and emerald is rigorously inspected for exceptional color, cut precision, and natural brilliance before setting.
                </p>
              </div>

              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <Award size={28} />
                </div>
                <h3>Master Goldsmithing</h3>
                <p>
                  Handcrafted by master artisans with generational experience in hallmarked 18K, 21K, and 22K yellow and white gold.
                </p>
              </div>

              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <Compass size={28} />
                </div>
                <h3>Bespoke 3D Sizing &amp; CAD</h3>
                <p>
                  From hand-drawn concept sketches to precise 3D wax carving, we ensure a flawless, tailored fit for your exact specifications.
                </p>
              </div>

              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <ShieldCheck size={28} />
                </div>
                <h3>Atelier Guarantee</h3>
                <p>
                  Accompanied by authentic hallmarked certification and insured delivery across Pakistan with private VIP concierge support.
                </p>
              </div>
            </div>
          </div>

          {/* The Mastercraft Journey */}
          <div className="craft-process-section">
            <div className="section-header text-center">
              <span className="section-kicker">THE CREATION PROCESS</span>
              <h2 className="section-title">From Concept to Heirloom</h2>
              <div className="title-divider" />
            </div>

            <div className="process-steps-grid">
              <div className="process-step-card">
                <span className="step-num">01</span>
                <h4>Private Consultation</h4>
                <p>Discuss your vision, stone preferences, metal purity, and budget directly with our jewellery specialists.</p>
              </div>
              <div className="process-step-card">
                <span className="step-num">02</span>
                <h4>Artisanal 3D Modeling</h4>
                <p>Review photorealistic 3D renders and exact dimensional blueprints before crafting begins.</p>
              </div>
              <div className="process-step-card">
                <span className="step-num">03</span>
                <h4>Hand Forging &amp; Setting</h4>
                <p>Master goldsmiths cast the precious gold and microscopically set each gem with secure prong alignment.</p>
              </div>
              <div className="process-step-card">
                <span className="step-num">04</span>
                <h4>Hallmarking &amp; Presentation</h4>
                <p>Finished with high-mirror polishing, rigorous purity assay, and presented in our signature luxury velvet coffret.</p>
              </div>
            </div>
          </div>

          {/* Luxury CTA Banner */}
          <div className="about-cta-banner">
            <div className="cta-banner-content">
              <Sparkles size={28} className="banner-sparkle" />
              <h2 className="cta-title">Begin Your Bespoke Journey</h2>
              <p className="cta-desc">
                Schedule a private consultation for custom engagement solitaires, bridal parures, or heirloom restorations with our master jewellers.
              </p>
              <div className="cta-buttons-row">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => onNavigate("/shop")}
                  rightIcon={<ArrowRight size={18} />}
                >
                  Explore Current Creations
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => onNavigate("/contact")}
                  leftIcon={<MessageCircle size={18} />}
                >
                  Contact Atelier Concierge
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

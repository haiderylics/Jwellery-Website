import React, { useEffect, useState } from "react";
import { ArrowRight, MessageCircle, ShieldCheck, Sparkles, Star } from "lucide-react";
import { HomepagePayload } from "@/types/api";
import { api } from "@/services/api";
import { Button } from "@/components/ui/Button";
import { ProductCard } from "@/components/ui/ProductCard";
import { ErrorState, ProductGridSkeleton } from "@/components/ui/Feedback";
import { ResponsiveImage } from "@/components/ui/ResponsiveImage";

export interface HomePageProps {
  onNavigate: (path: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const [data, setData] = useState<HomepagePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadHomeData = async () => {
    try {
      setLoading(true);
      setError(null);
      const payload = await api.getHomepage();
      setData(payload);
    } catch (err: any) {
      setError(err?.message || "Failed to load storefront data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHomeData();
  }, []);

  if (loading) {
    return (
      <div className="page-container home-page">
        <section className="hero-skeleton skeleton" />
        <div className="section-container">
          <ProductGridSkeleton count={8} />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="page-container">
        <ErrorState
          title="Storefront Temporarily Unavailable"
          message={error || "Could not retrieve storefront catalog."}
          onRetry={loadHomeData}
        />
      </div>
    );
  }

  const {
    site_settings,
    featured_categories,
    featured_products,
    new_arrivals,
    reviews,
    gallery_moments,
    about,
  } = data;

  const whatsappPhone = site_settings?.whatsapp_number?.replace(/[^0-9]/g, "") || "923001234567";

  return (
    <div className="home-page">
      {/* 1. HERO SECTION */}
      <section className="hero-section">
        <div className="hero-overlay" />
        <div className="hero-container">
          <span className="hero-subtitle">
            <Sparkles size={16} />
            <span>ESTABLISHED IN PAKISTAN &bull; LUXURY FINE JEWELLERY</span>
          </span>
          <h1 className="hero-title">
            Elegance Forged in <br />
            <span className="gold-gradient-text">Gold, Diamonds & Grace</span>
          </h1>
          <p className="hero-description">
            Discover artisanal 18K/21K/22K gold, certified solitaires, and bespoke bridal masterpieces
            handcrafted for a lifetime of brilliance.
          </p>
          <div className="hero-actions">
            <Button
              variant="primary"
              size="lg"
              onClick={() => onNavigate("/shop")}
              rightIcon={<ArrowRight size={18} />}
            >
              Explore Collection
            </Button>
            <Button
              variant="whatsapp"
              size="lg"
              onClick={() =>
                window.open(
                  `https://wa.me/${whatsappPhone}?text=Hello%20Zirconia%20Jewels,%20I%20would%20like%20to%20inquire%20about%20your%20collection.`,
                  "_blank"
                )
              }
              leftIcon={<MessageCircle size={18} />}
            >
              WhatsApp Concierge
            </Button>
          </div>
        </div>
      </section>

      {/* 2. CATEGORY DISCOVERY */}
      {featured_categories && featured_categories.length > 0 && (
        <section className="section-container categories-section">
          <div className="section-header">
            <span className="section-kicker">CURATED TAXONOMY</span>
            <h2 className="section-title">Discover By Category</h2>
            <div className="title-divider" />
          </div>

          <div className="categories-grid">
            {featured_categories.map((cat) => (
              <div
                key={cat.id}
                className="category-card"
                onClick={() => onNavigate(`/shop?category=${cat.slug}`)}
                role="button"
                tabIndex={0}
              >
                <div className="category-card-inner">
                  <h3 className="category-name">{cat.name}</h3>
                  <span className="category-count">{cat.product_count} Creations</span>
                  <span className="category-link-text">
                    View Pieces <ArrowRight size={14} />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 3. FEATURED PRODUCTS */}
      {featured_products && featured_products.length > 0 && (
        <section className="section-container featured-section">
          <div className="section-header">
            <span className="section-kicker">TIMELESS HIGHLIGHTS</span>
            <h2 className="section-title">Featured Masterpieces</h2>
            <div className="title-divider" />
          </div>

          <div className="product-grid">
            {featured_products.map((product) => (
              <ProductCard key={product.id} product={product} onNavigate={onNavigate} />
            ))}
          </div>

          <div className="section-footer">
            <Button
              variant="outline"
              size="md"
              onClick={() => onNavigate("/shop?featured=true")}
              rightIcon={<ArrowRight size={16} />}
            >
              View All Featured Pieces
            </Button>
          </div>
        </section>
      )}

      {/* 4. NEW ARRIVALS */}
      {new_arrivals && new_arrivals.length > 0 && (
        <section className="section-container new-arrivals-section">
          <div className="section-header">
            <span className="section-kicker">FRESH FROM THE ATELIER</span>
            <h2 className="section-title">New Arrivals</h2>
            <div className="title-divider" />
          </div>

          <div className="product-grid">
            {new_arrivals.map((product) => (
              <ProductCard key={product.id} product={product} onNavigate={onNavigate} />
            ))}
          </div>

          <div className="section-footer">
            <Button
              variant="outline"
              size="md"
              onClick={() => onNavigate("/shop?new_arrival=true")}
              rightIcon={<ArrowRight size={16} />}
            >
              Explore All New Arrivals
            </Button>
          </div>
        </section>
      )}

      {/* 5. BRAND HERITAGE HIGHLIGHT */}
      {about && (
        <section className="section-container about-highlight-section">
          <div className="about-highlight-card">
            <div className="about-text-col">
              <span className="section-kicker">FOUR DECADES OF DEVOTION</span>
              <h2 className="about-title">{about.title}</h2>
              <p className="about-story-snippet">{about.story_text}</p>
              <Button
                variant="secondary"
                size="md"
                onClick={() => onNavigate("/about")}
                rightIcon={<ArrowRight size={16} />}
              >
                Read Our Story & Craftsmanship
              </Button>
            </div>
            <div className="about-feature-box">
              <ShieldCheck size={36} className="feature-icon" />
              <h3>Bespoke Custom Orders</h3>
              <p>
                Have a dream jewellery piece in mind? Bring your concept to our master craftsmen for bespoke 3D CAD modeling and custom gemstone selection.
              </p>
              <button
                type="button"
                className="btn btn-whatsapp btn-sm mt-3"
                onClick={() =>
                  window.open(
                    `https://wa.me/${whatsappPhone}?text=Hello%20Zirconia%20Jewels,%20I%20would%20like%20to%20discuss%20a%20custom%20order.`,
                    "_blank"
                  )
                }
              >
                Inquire on WhatsApp
              </button>
            </div>
          </div>
        </section>
      )}

      {/* 6. TESTIMONIALS & REVIEWS */}
      {reviews && reviews.length > 0 && (
        <section className="section-container reviews-section">
          <div className="section-header">
            <span className="section-kicker">CLIENT SATISFACTION</span>
            <h2 className="section-title">Words from Our Patrons</h2>
            <div className="title-divider" />
          </div>

          <div className="reviews-grid">
            {reviews.map((rev) => (
              <div key={rev.id} className="review-card">
                <div className="review-stars">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      size={16}
                      className={i < rev.rating ? "star-filled" : "star-empty"}
                    />
                  ))}
                </div>
                <p className="review-quote">&ldquo;{rev.review_text}&rdquo;</p>
                <div className="review-author">
                  <span className="author-name">{rev.customer_name}</span>
                  {rev.is_verified && <span className="verified-chip">Verified Buyer</span>}
                </div>
              </div>
            ))}
          </div>

          <div className="section-footer">
            <Button
              variant="ghost"
              size="md"
              onClick={() => onNavigate("/reviews")}
              rightIcon={<ArrowRight size={16} />}
            >
              Read All Testimonials
            </Button>
          </div>
        </section>
      )}

      {/* 7. EXHIBITION & EVENT MOMENTS */}
      {gallery_moments && gallery_moments.length > 0 && (
        <section className="section-container gallery-section">
          <div className="section-header">
            <span className="section-kicker">EXHIBITIONS &amp; MOMENTS</span>
            <h2 className="section-title">Brand In Action</h2>
            <div className="title-divider" />
          </div>

          <div className="gallery-grid">
            {gallery_moments.map((item) => (
              <div key={item.id} className="gallery-card">
                <ResponsiveImage
                  image={item}
                  alt={item.title}
                  aspectRatio="4/3"
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                />
                <div className="gallery-card-meta">
                  <h4>{item.title}</h4>
                  {item.caption && <p>{item.caption}</p>}
                </div>
              </div>
            ))}
          </div>

          <div className="section-footer">
            <Button
              variant="outline"
              size="md"
              onClick={() => onNavigate("/gallery")}
              rightIcon={<ArrowRight size={16} />}
            >
              View Full Gallery
            </Button>
          </div>
        </section>
      )}
    </div>
  );
};

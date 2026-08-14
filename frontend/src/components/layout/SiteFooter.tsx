import React from "react";
import { MessageCircle, ShieldCheck, Sparkles, Truck } from "lucide-react";
import { DeliverySettings, SiteSettings } from "@/types/api";
import { formatPricePKR } from "@/utils/whatsapp";

export interface SiteFooterProps {
  settings: SiteSettings | null;
  deliverySettings: DeliverySettings | null;
  onNavigate: (path: string) => void;
}

export const SiteFooter: React.FC<SiteFooterProps> = ({
  settings,
  deliverySettings,
  onNavigate,
}) => {
  const brandName = settings?.brand_name || "Zirconia Fine Jewels";
  const tagline = settings?.tagline || "Luxury Handcrafted Jewellery";
  const freeThreshold = deliverySettings ? Number(deliverySettings.free_delivery_threshold) : 5000;

  return (
    <footer className="site-footer">
      <div className="footer-highlights">
        <div className="footer-container highlights-grid">
          <div className="highlight-item">
            <Sparkles className="highlight-icon" size={24} />
            <h4>100% Handcrafted</h4>
            <p>Artisanal gold & gemstone master craftsmanship</p>
          </div>
          <div className="highlight-item">
            <Truck className="highlight-icon" size={24} />
            <h4>Free Shipping in Pakistan</h4>
            <p>On all qualifying orders over {formatPricePKR(freeThreshold)}</p>
          </div>
          <div className="highlight-item">
            <MessageCircle className="highlight-icon" size={24} />
            <h4>Direct WhatsApp Concierge</h4>
            <p>Bespoke sizing, custom orders & personalized assistance</p>
          </div>
          <div className="highlight-item">
            <ShieldCheck className="highlight-icon" size={24} />
            <h4>Authentic Quality</h4>
            <p>Verified purity and premium presentation box</p>
          </div>
        </div>
      </div>

      <div className="footer-container footer-main">
        <div className="footer-col brand-col">
          <h3 className="footer-brand">{brandName}</h3>
          <p className="footer-tagline">{tagline}</p>
          <p className="footer-desc">
            Bespoke bridal sets, diamond solitaires, and heritage jewellery crafted for life's most precious moments.
          </p>
          {settings?.whatsapp_number && (
            <a
              href={`https://wa.me/${settings.whatsapp_number.replace(/[^0-9]/g, "")}`}
              target="_blank"
              rel="noopener noreferrer"
              className="footer-whatsapp-link"
            >
              <MessageCircle size={18} />
              <span>WhatsApp: {settings.whatsapp_number}</span>
            </a>
          )}
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Collections</h4>
          <ul className="footer-links">
            <li>
              <button type="button" onClick={() => onNavigate("/shop?category=rings")}>
                Rings & Solitaires
              </button>
            </li>
            <li>
              <button type="button" onClick={() => onNavigate("/shop?category=necklaces")}>
                Necklaces & Pendants
              </button>
            </li>
            <li>
              <button type="button" onClick={() => onNavigate("/shop?category=earrings")}>
                Earrings & Studs
              </button>
            </li>
            <li>
              <button type="button" onClick={() => onNavigate("/shop?category=bangles")}>
                Bangles & Bracelets
              </button>
            </li>
            <li>
              <button type="button" onClick={() => onNavigate("/shop?category=bridal")}>
                Bridal Sets
              </button>
            </li>
          </ul>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">About Brand</h4>
          <ul className="footer-links">
            <li>
              <button type="button" onClick={() => onNavigate("/about")}>
                Our Craft & Heritage
              </button>
            </li>
            <li>
              <button type="button" onClick={() => onNavigate("/reviews")}>
                Customer Reviews
              </button>
            </li>
            <li>
              <button type="button" onClick={() => onNavigate("/gallery")}>
                Exhibitions & Events
              </button>
            </li>
            <li>
              <button type="button" onClick={() => onNavigate("/contact")}>
                Bespoke Consultation
              </button>
            </li>
          </ul>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Follow Us</h4>
          <ul className="footer-social-list">
            {settings?.social_links && settings.social_links.length > 0 ? (
              settings.social_links.map((link) => (
                <li key={link.id}>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social-link"
                  >
                    {link.platform}
                  </a>
                </li>
              ))
            ) : (
              <>
                <li>
                  <span className="social-link">Instagram</span>
                </li>
                <li>
                  <span className="social-link">Facebook</span>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-container bottom-inner">
          <p>&copy; {new Date().getFullYear()} {brandName}. All rights reserved.</p>
          <p className="footer-disclaimer">
            Secure WhatsApp checkout & concierge delivery across Pakistan and worldwide.
          </p>
        </div>
      </div>
    </footer>
  );
};

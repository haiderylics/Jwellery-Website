import React from "react";
import { Mail, MapPin, MessageCircle, Phone, ShieldCheck, Sparkles } from "lucide-react";
import { SiteSettings } from "@/types/api";
import { Button } from "@/components/ui/Button";

export interface ContactPageProps {
  settings: SiteSettings | null;
}

export const ContactPage: React.FC<ContactPageProps> = ({ settings }) => {
  const whatsappPhone = settings?.whatsapp_number?.replace(/[^0-9]/g, "") || "923001234567";

  return (
    <div className="page-container contact-page">
      <div className="page-header">
        <span className="section-kicker">GET IN TOUCH</span>
        <h1 className="page-title">Bespoke Concierge &amp; Inquiries</h1>
        <p className="page-subtitle">
          Connect directly with our master jewellers for custom bridal consultations, private viewing appointments, and order assistance.
        </p>
        <div className="title-divider" />
      </div>

      <div className="contact-grid">
        {/* Left: Contact Channels */}
        <div className="contact-info-card">
          <h2>Direct Concierge Channels</h2>
          <p className="contact-card-desc">
            We prioritize personal consultation. Our consultants are available on WhatsApp 7 days a week for immediate sizing, customized pricing, and video viewings.
          </p>

          <div className="contact-channel-list">
            <div className="channel-item">
              <div className="channel-icon-wrap whatsapp">
                <MessageCircle size={22} />
              </div>
              <div className="channel-text">
                <span className="channel-label">Official WhatsApp Orders &amp; Inquiries</span>
                <span className="channel-value">{settings?.whatsapp_number || "+92 300 1234567"}</span>
                <a
                  href={`https://wa.me/${whatsappPhone}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="channel-action-link"
                >
                  Open Chat &rarr;
                </a>
              </div>
            </div>

            {settings?.contact_email && (
              <div className="channel-item">
                <div className="channel-icon-wrap">
                  <Mail size={22} />
                </div>
                <div className="channel-text">
                  <span className="channel-label">Concierge Email</span>
                  <a href={`mailto:${settings.contact_email}`} className="channel-value">
                    {settings.contact_email}
                  </a>
                </div>
              </div>
            )}

            {settings?.contact_phone && (
              <div className="channel-item">
                <div className="channel-icon-wrap">
                  <Phone size={22} />
                </div>
                <div className="channel-text">
                  <span className="channel-label">Phone Support</span>
                  <a href={`tel:${settings.contact_phone}`} className="channel-value">
                    {settings.contact_phone}
                  </a>
                </div>
              </div>
            )}

            <div className="channel-item">
              <div className="channel-icon-wrap">
                <MapPin size={22} />
              </div>
              <div className="channel-text">
                <span className="channel-label">Atelier Presence</span>
                <span className="channel-value">Lahore &amp; Karachi, Pakistan</span>
                <span className="channel-subtext">Private appointments available upon request</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Bespoke Inquiry Card */}
        <div className="bespoke-card">
          <div className="bespoke-card-header">
            <Sparkles size={28} className="gold-icon" />
            <h3>Request a Custom Design Consultation</h3>
          </div>
          <p>
            Planning an engagement ring, bridal set, or bespoke gold heirloom? Share your reference photo or vision directly with our master goldsmith on WhatsApp.
          </p>
          <ul className="bespoke-perks">
            <li>
              <ShieldCheck size={18} />
              <span>Complimentary 3D CAD rendering &amp; stone matching</span>
            </li>
            <li>
              <ShieldCheck size={18} />
              <span>Authentic hallmarked gold purity certificate</span>
            </li>
            <li>
              <ShieldCheck size={18} />
              <span>Insured delivery across Pakistan &amp; global shipping</span>
            </li>
          </ul>

          <Button
            variant="whatsapp"
            size="lg"
            onClick={() =>
              window.open(
                `https://wa.me/${whatsappPhone}?text=Hello%20Zirconia%20Jewels,%20I%20am%20interested%20in%20a%20bespoke%20jewellery%20consultation.`,
                "_blank"
              )
            }
            leftIcon={<MessageCircle size={20} />}
            className="w-full mt-6"
          >
            Start WhatsApp Consultation
          </Button>
        </div>
      </div>
    </div>
  );
};

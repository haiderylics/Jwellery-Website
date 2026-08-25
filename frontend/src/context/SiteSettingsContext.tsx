import React, { createContext, useContext, useEffect, useState } from "react";
import { DeliverySettings, SiteSettings, SocialLink } from "@/types/api";
import { api } from "@/services/api";

export interface SiteSettingsContextValue {
  settings: SiteSettings | null;
  deliverySettings: DeliverySettings | null;
  brandName: string;
  tagline: string;
  whatsappNumber: string;
  contactEmail: string;
  contactPhone: string;
  socialLinks: SocialLink[];
  canonicalUrl: string;
  isLoading: boolean;
  refreshSettings: () => Promise<void>;
}

const defaultContextValue: SiteSettingsContextValue = {
  settings: null,
  deliverySettings: null,
  brandName: "AHS Jewellers",
  tagline: "Bespoke Haute Joaillerie & Timeless Gold Craftsmanship",
  whatsappNumber: "+923127674165",
  contactEmail: "concierge@ahsjewellers.pk",
  contactPhone: "+92 312 7674165",
  socialLinks: [],
  canonicalUrl: "https://www.ahsjewellers.pk",
  isLoading: true,
  refreshSettings: async () => {},
};

const SiteSettingsContext = createContext<SiteSettingsContextValue>(defaultContextValue);

export const SiteSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<SiteSettings | null>(null);
  const [deliverySettings, setDeliverySettings] = useState<DeliverySettings | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchSettings = async () => {
    try {
      const [siteData, delData] = await Promise.all([
        api.getSiteSettings(),
        api.getDeliverySettings(),
      ]);
      setSettings(siteData);
      setDeliverySettings(delData);

      // Dynamically update document title and meta tags
      if (siteData?.brand_name) {
        document.title = `${siteData.brand_name} | ${siteData.tagline || "Luxury Handcrafted Jewellery"}`;
      }
    } catch {
      // Retain fallback defaults
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const brandName = settings?.brand_name || "AHS Jewellers";
  const tagline = settings?.tagline || "Bespoke Haute Joaillerie & Timeless Gold Craftsmanship";
  const whatsappNumber = settings?.whatsapp_number || "+923127674165";
  const contactEmail = settings?.contact_email || "concierge@ahsjewellers.pk";
  const contactPhone = settings?.contact_phone || "+92 312 7674165";
  const socialLinks = settings?.social_links || [];
  const canonicalUrl = settings?.canonical_site_url || "https://www.ahsjewellers.pk";

  return (
    <SiteSettingsContext.Provider
      value={{
        settings,
        deliverySettings,
        brandName,
        tagline,
        whatsappNumber,
        contactEmail,
        contactPhone,
        socialLinks,
        canonicalUrl,
        isLoading,
        refreshSettings: fetchSettings,
      }}
    >
      {children}
    </SiteSettingsContext.Provider>
  );
};

export const useSiteSettings = (): SiteSettingsContextValue => {
  return useContext(SiteSettingsContext);
};

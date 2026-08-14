import React, { useEffect, useState } from "react";
import { DeliverySettings, Popup, Promotion, SiteSettings } from "@/types/api";
import { api } from "@/services/api";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";
import { SiteFooter } from "@/components/layout/SiteFooter";
import { SiteHeader } from "@/components/layout/SiteHeader";
import { ActivePopupModal } from "@/features/promotions/ActivePopupModal";
import { AboutPage } from "@/pages/AboutPage";
import { CartPage } from "@/pages/CartPage";
import { ContactPage } from "@/pages/ContactPage";
import { GalleryPage } from "@/pages/GalleryPage";
import { HomePage } from "@/pages/HomePage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ProductDetailPage } from "@/pages/ProductDetailPage";
import { ReviewsPage } from "@/pages/ReviewsPage";
import { ShopPage } from "@/pages/ShopPage";

export const App: React.FC = () => {
  const [currentPath, setCurrentPath] = useState<string>(window.location.pathname || "/");
  const [settings, setSettings] = useState<SiteSettings | null>(null);
  const [deliverySettings, setDeliverySettings] = useState<DeliverySettings | null>(null);
  const [announcements, setAnnouncements] = useState<Promotion[]>([]);
  const [activePopup, setActivePopup] = useState<Popup | null>(null);

  // Sync browser back/forward buttons
  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  // Fetch initial global settings, active announcements & popup
  useEffect(() => {
    async function loadGlobalSettings() {
      try {
        const [siteData, delData, promoData, popupData] = await Promise.all([
          api.getSiteSettings(),
          api.getDeliverySettings(),
          api.getActivePromotions(),
          api.getActivePopup(),
        ]);
        setSettings(siteData);
        setDeliverySettings(delData);
        setAnnouncements(promoData.filter((p) => p.show_in_announcement_bar));
        setActivePopup(popupData?.data || null);
      } catch {
        // Fallback gracefully to default state
      }
    }
    loadGlobalSettings();
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, "", path);
    setCurrentPath(path);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Route Dispatcher
  const renderRoute = () => {
    const [pathOnly, queryString] = currentPath.split("?");
    const searchParams = new URLSearchParams(queryString || "");

    // 1. Home
    if (pathOnly === "/" || pathOnly === "") {
      return <HomePage onNavigate={navigate} />;
    }

    // 2. Shop / Catalog
    if (pathOnly === "/shop" || pathOnly === "/products") {
      const initialCat = searchParams.get("category") || "";
      const initialQ = searchParams.get("q") || "";
      return (
        <ShopPage
          initialCategory={initialCat}
          initialQuery={initialQ}
          onNavigate={navigate}
        />
      );
    }

    // 3. Product Detail: /product/:slug
    if (pathOnly.startsWith("/product/")) {
      const slug = pathOnly.replace("/product/", "").replace(/\/$/, "");
      return <ProductDetailPage slug={slug} settings={settings} onNavigate={navigate} />;
    }

    // 4. Cart
    if (pathOnly === "/cart") {
      return (
        <CartPage
          settings={settings}
          deliverySettings={deliverySettings}
          onNavigate={navigate}
        />
      );
    }

    // 5. About
    if (pathOnly === "/about") {
      return <AboutPage onNavigate={navigate} />;
    }

    // 6. Reviews
    if (pathOnly === "/reviews") {
      return <ReviewsPage />;
    }

    // 7. Gallery
    if (pathOnly === "/gallery") {
      return <GalleryPage />;
    }

    // 8. Contact
    if (pathOnly === "/contact") {
      return <ContactPage settings={settings} />;
    }

    // Fallback 404
    return <NotFoundPage onNavigate={navigate} />;
  };

  return (
    <div className="storefront-app">
      {/* 1. Top Announcement Bar */}
      <AnnouncementBar announcements={announcements} onNavigate={navigate} />

      {/* 2. Site Header */}
      <SiteHeader settings={settings} currentPath={currentPath} onNavigate={navigate} />

      {/* 3. Main Route Body */}
      <main className="storefront-main" role="main">
        {renderRoute()}
      </main>

      {/* 4. Site Footer */}
      <SiteFooter
        settings={settings}
        deliverySettings={deliverySettings}
        onNavigate={navigate}
      />

      {/* 5. Promotional Modal Popup */}
      <ActivePopupModal popup={activePopup} onNavigate={navigate} />
    </div>
  );
};

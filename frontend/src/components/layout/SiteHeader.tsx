import React, { useState } from "react";
import { Menu, ShoppingBag, X } from "lucide-react";
import { SiteSettings } from "@/types/api";
import { useCart } from "@/state/cartStore";

export interface SiteHeaderProps {
  settings: SiteSettings | null;
  currentPath: string;
  onNavigate: (path: string) => void;
}

export const SiteHeader: React.FC<SiteHeaderProps> = ({
  settings,
  currentPath,
  onNavigate,
}) => {
  const { itemCount } = useCart();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const brandName = settings?.brand_name || "Zirconia Fine Jewels";
  const tagline = settings?.tagline || "Luxury Handcrafted Jewellery";

  const navLinks = [
    { label: "Home", path: "/" },
    { label: "Shop All", path: "/shop" },
    { label: "Heritage", path: "/about" },
    { label: "Testimonials", path: "/reviews" },
    { label: "Exhibitions", path: "/gallery" },
    { label: "Contact", path: "/contact" },
  ];

  const handleNav = (path: string) => {
    setMobileMenuOpen(false);
    onNavigate(path);
  };

  return (
    <header className="site-header">
      <div className="header-container">
        {/* Mobile Menu Toggle */}
        <button
          type="button"
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={mobileMenuOpen}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Brand Logo */}
        <div className="brand-logo" onClick={() => handleNav("/")} role="button" tabIndex={0}>
          <span className="brand-title">{brandName}</span>
          <span className="brand-subtitle">{tagline}</span>
        </div>

        {/* Desktop Navigation */}
        <nav className="desktop-nav" aria-label="Main Navigation">
          <ul className="nav-list">
            {navLinks.map((link) => {
              const isActive = currentPath === link.path;
              return (
                <li key={link.path} className="nav-item">
                  <button
                    type="button"
                    className={`nav-link ${isActive ? "active" : ""}`}
                    onClick={() => handleNav(link.path)}
                    aria-current={isActive ? "page" : undefined}
                  >
                    {link.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Header Actions */}
        <div className="header-actions">
          <button
            type="button"
            className="cart-icon-btn"
            onClick={() => handleNav("/cart")}
            aria-label={`Shopping Cart with ${itemCount} items`}
          >
            <ShoppingBag size={22} />
            {itemCount > 0 && <span className="cart-badge">{itemCount}</span>}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-drawer-backdrop" onClick={() => setMobileMenuOpen(false)}>
          <div className="mobile-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="mobile-drawer-header">
              <span className="drawer-brand">{brandName}</span>
              <button
                type="button"
                className="drawer-close-btn"
                onClick={() => setMobileMenuOpen(false)}
                aria-label="Close menu"
              >
                <X size={22} />
              </button>
            </div>
            <nav className="mobile-nav-list">
              {navLinks.map((link) => (
                <button
                  key={link.path}
                  type="button"
                  className={`mobile-nav-item ${currentPath === link.path ? "active" : ""}`}
                  onClick={() => handleNav(link.path)}
                >
                  {link.label}
                </button>
              ))}
            </nav>
            <div className="mobile-drawer-footer">
              <button
                type="button"
                className="btn btn-primary w-full"
                onClick={() => handleNav("/shop")}
              >
                Explore Collection
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

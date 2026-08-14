import React, { useEffect, useState } from "react";
import { RotateCcw, Search, SlidersHorizontal } from "lucide-react";
import { Category, ProductAttributeType, ProductListItem } from "@/types/api";
import { api } from "@/services/api";
import { Button } from "@/components/ui/Button";
import { ProductCard } from "@/components/ui/ProductCard";
import { EmptyState, ErrorState, ProductGridSkeleton } from "@/components/ui/Feedback";

export interface ShopPageProps {
  initialCategory?: string;
  initialQuery?: string;
  onNavigate: (path: string) => void;
}

export const ShopPage: React.FC<ShopPageProps> = ({
  initialCategory = "",
  initialQuery = "",
  onNavigate,
}) => {
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [attributeTypes, setAttributeTypes] = useState<ProductAttributeType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter States
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);
  const [selectedAttribute, setSelectedAttribute] = useState<string>("");
  const [featuredOnly, setFeaturedOnly] = useState(false);
  const [newArrivalOnly, setNewArrivalOnly] = useState(false);
  const [customOrderOnly, setCustomOrderOnly] = useState(false);
  const [searchQuery, setSearchQuery] = useState<string>(initialQuery);
  const [ordering, setOrdering] = useState<string>("priority");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  // Load Categories & Attributes once
  useEffect(() => {
    async function loadTaxonomy() {
      try {
        const [cats, attrs] = await Promise.all([api.getCategories(), api.getAttributes()]);
        setCategories(cats);
        setAttributeTypes(attrs);
      } catch {
        // Fallback silently
      }
    }
    loadTaxonomy();
  }, []);

  // Fetch Products on filter changes
  const fetchProducts = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.getProducts({
        category: selectedCategory || undefined,
        attribute: selectedAttribute || undefined,
        featured: featuredOnly || undefined,
        new_arrival: newArrivalOnly || undefined,
        custom_order: customOrderOnly || undefined,
        q: searchQuery || undefined,
        ordering: ordering || undefined,
        page,
      });

      setProducts(response.results);
      setTotalPages(response.total_pages);
      setTotalCount(response.count);
      setCurrentPage(response.current_page);
    } catch (err: any) {
      setError(err?.message || "Failed to load products.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts(1);
  }, [
    selectedCategory,
    selectedAttribute,
    featuredOnly,
    newArrivalOnly,
    customOrderOnly,
    ordering,
  ]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchProducts(1);
  };

  const handleClearFilters = () => {
    setSelectedCategory("");
    setSelectedAttribute("");
    setFeaturedOnly(false);
    setNewArrivalOnly(false);
    setCustomOrderOnly(false);
    setSearchQuery("");
    setOrdering("priority");
  };

  const hasActiveFilters = Boolean(
    selectedCategory ||
      selectedAttribute ||
      featuredOnly ||
      newArrivalOnly ||
      customOrderOnly ||
      searchQuery ||
      ordering !== "priority"
  );

  return (
    <div className="page-container shop-page">
      <div className="shop-header">
        <span className="section-kicker">CURATED COLLECTION</span>
        <h1 className="shop-title">Bespoke Fine Jewellery</h1>
        <p className="shop-subtitle">
          Explore handcrafted gold, solitaires, bangles, and bridal masterpieces.
        </p>
      </div>

      {/* Search Bar & Mobile Filter Trigger */}
      <div className="shop-toolbar">
        <form className="search-form" onSubmit={handleSearchSubmit}>
          <Search size={18} className="search-icon" />
          <input
            type="search"
            className="search-input"
            placeholder="Search rings, solitaires, bridal sets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search products"
          />
          {searchQuery && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={() => {
                setSearchQuery("");
                setTimeout(() => fetchProducts(1), 50);
              }}
            >
              Clear
            </button>
          )}
        </form>

        <div className="toolbar-actions">
          <button
            type="button"
            className="mobile-filter-btn"
            onClick={() => setMobileFilterOpen(!mobileFilterOpen)}
            aria-label="Toggle filters drawer"
          >
            <SlidersHorizontal size={16} />
            <span>Filters {hasActiveFilters && "(Active)"}</span>
          </button>

          <div className="sort-dropdown-wrapper">
            <label htmlFor="sort-select" className="sr-only">
              Sort Products
            </label>
            <select
              id="sort-select"
              className="sort-select"
              value={ordering}
              onChange={(e) => setOrdering(e.target.value)}
            >
              <option value="priority">Featured & Curated</option>
              <option value="newest">Newest Additions</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Category Pills Bar */}
      <div className="category-pills-bar" role="tablist" aria-label="Product Categories">
        <button
          type="button"
          className={`category-pill ${!selectedCategory ? "active" : ""}`}
          onClick={() => setSelectedCategory("")}
        >
          All Jewellery
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            type="button"
            className={`category-pill ${selectedCategory === cat.slug ? "active" : ""}`}
            onClick={() => setSelectedCategory(cat.slug)}
          >
            {cat.name} ({cat.product_count})
          </button>
        ))}
      </div>

      {/* Main Layout: Sidebar Filters + Products Grid */}
      <div className="shop-layout">
        {/* Desktop Sidebar Filters */}
        <aside className={`shop-sidebar ${mobileFilterOpen ? "mobile-open" : ""}`}>
          <div className="sidebar-header">
            <h3>Filter Collection</h3>
            {hasActiveFilters && (
              <button type="button" className="clear-all-link" onClick={handleClearFilters}>
                <RotateCcw size={12} />
                <span>Reset</span>
              </button>
            )}
          </div>

          {/* Merchandising Flags */}
          <div className="filter-group">
            <h4 className="filter-group-title">Collections & Flags</h4>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={featuredOnly}
                onChange={(e) => setFeaturedOnly(e.target.checked)}
              />
              <span>Featured Creations</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={newArrivalOnly}
                onChange={(e) => setNewArrivalOnly(e.target.checked)}
              />
              <span>New Arrivals</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={customOrderOnly}
                onChange={(e) => setCustomOrderOnly(e.target.checked)}
              />
              <span>Custom Order Designs</span>
            </label>
          </div>

          {/* Secondary Attributes */}
          {attributeTypes.map((attrType) => (
            <div key={attrType.id} className="filter-group">
              <h4 className="filter-group-title">{attrType.name}</h4>
              <div className="attribute-chips">
                {attrType.values.map((val) => (
                  <button
                    key={val.id}
                    type="button"
                    className={`attr-chip ${selectedAttribute === val.slug ? "active" : ""}`}
                    onClick={() =>
                      setSelectedAttribute(selectedAttribute === val.slug ? "" : val.slug)
                    }
                  >
                    {val.value}
                  </button>
                ))}
              </div>
            </div>
          ))}

          {mobileFilterOpen && (
            <Button
              variant="primary"
              size="md"
              onClick={() => setMobileFilterOpen(false)}
              className="w-full mt-4"
            >
              Apply Filters ({totalCount} items)
            </Button>
          )}
        </aside>

        {/* Products Results Container */}
        <main className="shop-results">
          {loading ? (
            <ProductGridSkeleton count={8} />
          ) : error ? (
            <ErrorState message={error} onRetry={() => fetchProducts(currentPage)} />
          ) : products.length === 0 ? (
            <EmptyState
              title="No Jewellery Pieces Found"
              description="Try selecting different filters or clearing your search keywords."
              actionLabel="Clear All Filters"
              onAction={handleClearFilters}
            />
          ) : (
            <>
              <div className="results-count-bar">
                <span>Showing {products.length} of {totalCount} creations</span>
              </div>

              <div className="product-grid">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} onNavigate={onNavigate} />
                ))}
              </div>

              {/* Bounded Pagination Controls */}
              {totalPages > 1 && (
                <nav className="pagination-nav" aria-label="Catalog pagination">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage <= 1}
                    onClick={() => fetchProducts(currentPage - 1)}
                  >
                    &larr; Previous
                  </Button>
                  <span className="pagination-indicator">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage >= totalPages}
                    onClick={() => fetchProducts(currentPage + 1)}
                  >
                    Next &rarr;
                  </Button>
                </nav>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

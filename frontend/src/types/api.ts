/**
 * API Type Contracts for Jewellery Storefront
 * Source of Truth: Backend Django REST Framework Serializers (/api/v1/)
 */

export interface CompactCategory {
  id: number;
  name: string;
  slug: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  sort_order: number;
  product_count: number;
}

export interface ProductAttributeValue {
  id: number;
  value: string;
  slug: string;
  attribute_type_name: string;
  attribute_type_slug: string;
  sort_order: number;
}

export interface ProductAttributeType {
  id: number;
  name: string;
  slug: string;
  sort_order: number;
  values: ProductAttributeValue[];
}

export interface ProductImage {
  id: number;
  image_url: string | null;
  thumbnail_url?: string | null;
  medium_url?: string | null;
  large_url?: string | null;
  is_primary: boolean;
  alt_text: string;
  sort_order: number;
}

export interface ProductVariant {
  id: number;
  name: string;
  sku: string;
  price_override: string | null;
  effective_price: string;
  is_available: boolean;
  stock_status: "in_stock" | "low_stock" | "out_of_stock";
  sort_order: number;
}

export interface ProductVideo {
  id: number;
  video_url: string | null;
  title: string;
}

export interface ProductListItem {
  id: number;
  name: string;
  slug: string;
  base_price: string;
  compare_at_price: string | null;
  primary_image: ProductImage | null;
  category: CompactCategory | null;
  availability_status: "in_stock" | "low_stock" | "out_of_stock" | "made_to_order";
  is_featured: boolean;
  is_new_arrival: boolean;
  is_custom_order: boolean;
  stock_status: "in_stock" | "low_stock" | "out_of_stock";
  updated_at: string;
}

export interface ProductDetail {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  base_price: string;
  compare_at_price: string | null;
  availability_status: "in_stock" | "low_stock" | "out_of_stock" | "made_to_order";
  is_featured: boolean;
  is_new_arrival: boolean;
  is_custom_order: boolean;
  category: CompactCategory | null;
  attributes: ProductAttributeValue[];
  images: ProductImage[];
  variants: ProductVariant[];
  video: ProductVideo | null;
  stock_status: "in_stock" | "low_stock" | "out_of_stock";
  seo: {
    title: string;
    description: string;
  };
  updated_at: string;
}

export interface Review {
  id: number;
  customer_name: string;
  review_text: string;
  rating: number;
  image_url: string | null;
  thumbnail_url?: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface GalleryItem {
  id: number;
  title: string;
  caption: string;
  image_url: string | null;
  thumbnail_url?: string | null;
  medium_url?: string | null;
  item_type: "exhibition" | "seminar" | "brand" | "other";
  event_date: string | null;
  created_at: string;
}

export interface AboutSection {
  id: number;
  title: string;
  subtitle: string;
  story_text: string;
  image_url: string | null;
  updated_at: string;
}

export interface Promotion {
  id: number;
  title: string;
  subtitle: string;
  announcement_text: string;
  image_url: string | null;
  cta_label: string;
  cta_url: string;
  show_in_announcement_bar: boolean;
  priority: number;
}

export interface Popup {
  id: number;
  title: string;
  message: string;
  image_url: string | null;
  cta_label: string;
  cta_url: string;
  delay_seconds: number;
}

export interface SocialLink {
  id: number;
  platform: string;
  url: string;
  sort_order: number;
}

export interface SiteSettings {
  brand_name: string;
  tagline: string;
  contact_email: string;
  contact_phone: string;
  whatsapp_number: string;
  canonical_site_url: string;
  social_links: SocialLink[];
  default_seo: {
    title: string;
    description: string;
  };
  updated_at: string;
}

export interface DeliverySettings {
  pakistan_delivery_enabled: boolean;
  free_delivery_threshold: string;
  pakistan_delivery_charge: string;
  international_delivery_mode: "disabled" | "whatsapp_quote" | "fixed";
  international_delivery_fixed_charge: string | null;
  updated_at: string;
}

export interface HomepagePayload {
  site_settings: SiteSettings;
  delivery_settings: DeliverySettings;
  announcements: Promotion[];
  active_popup: Popup | null;
  featured_categories: Category[];
  featured_products: ProductListItem[];
  new_arrivals: ProductListItem[];
  reviews: Review[];
  gallery_moments: GalleryItem[];
  about: AboutSection | null;
}

export interface PaginatedResponse<T> {
  count: number;
  total_pages: number;
  current_page: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export interface CartItemStored {
  productSlug: string;
  variantId: number | null;
  quantity: number;
}

export interface CartItemResolved {
  product: ProductListItem | ProductDetail;
  variant: ProductVariant | null;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
}

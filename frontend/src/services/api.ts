/**
 * Centralized, typed API Client for Jewellery Storefront
 */

import {
  AboutSection,
  Category,
  DeliverySettings,
  GalleryItem,
  HomepagePayload,
  PaginatedResponse,
  Popup,
  ProductAttributeType,
  ProductDetail,
  ProductListItem,
  Promotion,
  Review,
  SiteSettings,
} from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export class ApiClientError extends Error {
  code: string;
  details?: unknown;
  status: number;

  constructor(message: string, code = "api_error", status = 500, details?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: "application/json",
        ...options.headers,
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorCode = "http_error";
      let errorMessage = `HTTP Error ${response.status}`;
      let errorDetails: unknown = null;

      try {
        const errorJson = await response.json();
        if (errorJson?.error) {
          errorCode = errorJson.error.code || errorCode;
          errorMessage = errorJson.error.message || errorMessage;
          errorDetails = errorJson.error.details || null;
        }
      } catch {
        // Non-JSON error body fallback
      }

      throw new ApiClientError(errorMessage, errorCode, response.status, errorDetails);
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof ApiClientError) {
      throw err;
    }
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiClientError("Request timed out. Please check your internet connection.", "timeout", 408);
    }
    throw new ApiClientError("Network error. Unable to reach storefront server.", "network_error", 0, err);
  }
}

export const api = {
  getHomepage: (): Promise<HomepagePayload> => request<HomepagePayload>("/home/"),

  getProducts: (params: {
    category?: string;
    attribute?: string;
    featured?: boolean;
    new_arrival?: boolean;
    custom_order?: boolean;
    q?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<PaginatedResponse<ProductListItem>> => {
    const searchParams = new URLSearchParams();
    if (params.category) searchParams.set("category", params.category);
    if (params.attribute) searchParams.set("attribute", params.attribute);
    if (params.featured) searchParams.set("featured", "true");
    if (params.new_arrival) searchParams.set("new_arrival", "true");
    if (params.custom_order) searchParams.set("custom_order", "true");
    if (params.q) searchParams.set("q", params.q);
    if (params.ordering) searchParams.set("ordering", params.ordering);
    if (params.page) searchParams.set("page", String(params.page));
    if (params.page_size) searchParams.set("page_size", String(params.page_size));

    const queryString = searchParams.toString();
    return request<PaginatedResponse<ProductListItem>>(`/products/${queryString ? `?${queryString}` : ""}`);
  },

  getProductDetail: (slug: string): Promise<ProductDetail> =>
    request<ProductDetail>(`/products/${encodeURIComponent(slug)}/`),

  getCategories: (): Promise<Category[]> => request<Category[]>("/categories/"),

  getAttributes: (): Promise<ProductAttributeType[]> => request<ProductAttributeType[]>("/attributes/"),

  getReviews: (page = 1): Promise<PaginatedResponse<Review>> =>
    request<PaginatedResponse<Review>>(`/reviews/?page=${page}`),

  getGallery: (type?: string, page = 1): Promise<PaginatedResponse<GalleryItem>> => {
    const query = type ? `?type=${encodeURIComponent(type)}&page=${page}` : `?page=${page}`;
    return request<PaginatedResponse<GalleryItem>>(`/gallery/${query}`);
  },

  getAbout: (): Promise<AboutSection> => request<AboutSection>("/about/"),

  getActivePromotions: (): Promise<Promotion[]> => request<Promotion[]>("/promotions/active/"),

  getActivePopup: (): Promise<{ data: Popup | null; message?: string }> =>
    request<{ data: Popup | null; message?: string }>("/popups/active/"),

  getSiteSettings: (): Promise<SiteSettings> => request<SiteSettings>("/site-settings/"),

  getDeliverySettings: (): Promise<DeliverySettings> => request<DeliverySettings>("/delivery-settings/"),
};

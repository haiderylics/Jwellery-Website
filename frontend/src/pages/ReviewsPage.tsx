import React, { useEffect, useState } from "react";
import { Star } from "lucide-react";
import { Review } from "@/types/api";
import { api } from "@/services/api";
import { ErrorState } from "@/components/ui/Feedback";

export const ReviewsPage: React.FC = () => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadReviews() {
      try {
        setLoading(true);
        const data = await api.getReviews();
        setReviews(data.results);
      } catch (err: any) {
        setError(err?.message || "Failed to load customer reviews.");
      } finally {
        setLoading(false);
      }
    }
    loadReviews();
  }, []);

  return (
    <div className="page-container reviews-page">
      <div className="page-header">
        <span className="section-kicker">PATRON TESTIMONIALS</span>
        <h1 className="page-title">Client Experiences</h1>
        <p className="page-subtitle">
          Real reviews and kind words from patrons across Pakistan and worldwide.
        </p>
        <div className="title-divider" />
      </div>

      {loading ? (
        <div className="reviews-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="review-card skeleton" style={{ minHeight: "180px" }} />
          ))}
        </div>
      ) : error ? (
        <ErrorState message={error} />
      ) : reviews.length === 0 ? (
        <p className="text-center text-muted">No public reviews available at this time.</p>
      ) : (
        <div className="reviews-grid">
          {reviews.map((rev) => (
            <div key={rev.id} className="review-card">
              <div className="review-stars">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    size={18}
                    className={i < rev.rating ? "star-filled" : "star-empty"}
                  />
                ))}
              </div>
              <p className="review-quote">&ldquo;{rev.review_text}&rdquo;</p>
              <div className="review-author">
                <span className="author-name">{rev.customer_name}</span>
                {rev.is_verified && <span className="verified-chip">Verified Direct Purchaser</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

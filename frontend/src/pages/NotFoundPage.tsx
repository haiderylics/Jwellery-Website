import React from "react";
import { ArrowLeft, Compass } from "lucide-react";
import { Button } from "@/components/ui/Button";

export interface NotFoundPageProps {
  onNavigate: (path: string) => void;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({ onNavigate }) => {
  return (
    <div className="page-container not-found-page">
      <div className="not-found-card">
        <Compass size={56} className="not-found-icon" />
        <span className="section-kicker">PAGE NOT FOUND</span>
        <h1 className="not-found-title">404</h1>
        <p className="not-found-desc">
          The jewellery piece or page you are looking for has been relocated or is no longer available.
        </p>
        <div className="not-found-actions">
          <Button variant="primary" size="md" onClick={() => onNavigate("/")}>
            Return to Homepage
          </Button>
          <Button
            variant="outline"
            size="md"
            onClick={() => onNavigate("/shop")}
            leftIcon={<ArrowLeft size={16} />}
          >
            Explore Collection
          </Button>
        </div>
      </div>
    </div>
  );
};

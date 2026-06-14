import React, { useEffect, useState } from 'react';
import { authHeaders } from '../utils/api';

export default function AuthenticatedImage({ src, token, alt, className }) {
  const [blobUrl, setBlobUrl] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!src || !token) return undefined;

    let objectUrl = null;
    let cancelled = false;

    fetch(src, { headers: authHeaders(token) })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load image');
        return res.blob();
      })
      .then((blob) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setBlobUrl(objectUrl);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [src, token]);

  if (failed || !src) {
    return (
      <div className={`auth-image-placeholder ${className || ''}`}>
        <span>No image</span>
      </div>
    );
  }

  if (!blobUrl) {
    return <div className={`auth-image-loading ${className || ''}`} />;
  }

  return <img src={blobUrl} alt={alt} className={className} />;
}

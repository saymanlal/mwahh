'use client';

import { useState, useEffect } from 'react';

interface UseFetchOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: unknown;
  shouldFetch?: boolean;
  token?: string;
}

export function useFetch<T>(
  url: string | null,
  options: UseFetchOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!!url);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!url) {
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
          ...options.headers,
        };

        if (options.token) {
          headers['Authorization'] = `Bearer ${options.token}`;
        }

        const response = await fetch(url, {
          method: options.method || 'GET',
          headers,
          body: options.body ? JSON.stringify(options.body) : undefined,
          signal: controller.signal,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const result = await response.json();
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          if (isMounted) {
            setError(err);
            console.log('[v0] Fetch error:', err.message);
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [url, options.token]);

  return { data, loading, error };
}

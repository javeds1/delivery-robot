import { useCallback, useEffect, useRef, useState } from "react";
import { fetchVendorContext, patchVendor, type RawVendor } from "../api/vendor";

export interface VendorState {
  vendorId: number | null;
  vendorName: string;
  isPaused: boolean;
  isLoading: boolean;
  error: string | null;
  togglePause: () => Promise<void>;
  updateVendorName: (name: string) => Promise<void>;
}

export function useVendor(): VendorState {
  const [vendorId, setVendorId] = useState<number | null>(null);
  const [vendorName, setVendorName] = useState("Campus Eats");
  const [isPaused, setIsPaused] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Keep a ref so togglePause always sees the current id without re-subscribing
  const vendorRef = useRef<RawVendor | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);

    fetchVendorContext()
      .then(({ vendor }) => {
        if (cancelled) return;
        vendorRef.current = vendor;
        setVendorId(vendor.id);
        setVendorName(vendor.name);
        setIsPaused(vendor.intake_paused);
      })
      .catch((err) => {
        if (cancelled) return;
        console.error("Failed to load vendor context:", err);
        setError("Could not load vendor profile.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const togglePause = useCallback(async () => {
    const vendor = vendorRef.current;
    if (!vendor) return;

    const next = !vendor.intake_paused;
    // Optimistic update
    setIsPaused(next);
    vendorRef.current = { ...vendor, intake_paused: next };

    try {
      const updated = await patchVendor(vendor.id, { intake_paused: next });
      vendorRef.current = updated;
      setIsPaused(updated.intake_paused);
    } catch (err) {
      console.error("Failed to update pause state:", err);
      // Revert
      setIsPaused(vendor.intake_paused);
      vendorRef.current = vendor;
    }
  }, []);

  const updateVendorName = useCallback(async (name: string) => {
    const vendor = vendorRef.current;
    if (!vendor) return;

    setVendorName(name);
    vendorRef.current = { ...vendor, name };

    try {
      const updated = await patchVendor(vendor.id, { name });
      vendorRef.current = updated;
      setVendorName(updated.name);
    } catch (err) {
      console.error("Failed to update vendor name:", err);
      // Revert
      setVendorName(vendor.name);
      vendorRef.current = vendor;
    }
  }, []);

  return {
    vendorId,
    vendorName,
    isPaused,
    isLoading,
    error,
    togglePause,
    updateVendorName,
  };
}

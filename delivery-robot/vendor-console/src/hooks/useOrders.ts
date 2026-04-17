import { useState, useEffect, useCallback, useRef } from "react";
import type { Order, OrderStatus } from "../types";
import { generateMockOrder, INITIAL_ORDERS } from "../data/mockOrders";

const WS_INTERVAL_MS = 18000;

interface UseOrdersOptions {
  autoAcceptOrders?: boolean;
}

export function useOrders(options: UseOrdersOptions = {}) {
  const { autoAcceptOrders = false } = options;
  const [orders, setOrders] = useState<Order[]>(INITIAL_ORDERS);
  const [isPaused, setIsPaused] = useState(false);
  const [newOrderIds, setNewOrderIds] = useState<Set<string>>(new Set());
  const isPausedRef = useRef(isPaused);
  isPausedRef.current = isPaused;

  // Simulate incoming WebSocket orders
  useEffect(() => {
    const interval = setInterval(() => {
      if (isPausedRef.current) return;
      const newOrder = generateMockOrder();
      if (autoAcceptOrders) {
        newOrder.status = "ACCEPTED";
      }
      setOrders((prev) => [newOrder, ...prev]);
      setNewOrderIds((prev) => new Set(prev).add(newOrder.id));
      setTimeout(() => {
        setNewOrderIds((prev) => {
          const next = new Set(prev);
          next.delete(newOrder.id);
          return next;
        });
      }, 4000);
    }, WS_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  const updateOrderStatus = useCallback((orderId: string, status: OrderStatus) => {
    setOrders((prev) =>
      prev.map((o) =>
        o.id === orderId ? { ...o, status, updatedAt: new Date() } : o
      )
    );
  }, []);

  const togglePause = useCallback(() => setIsPaused((prev) => !prev), []);

  return {
    allOrders: orders,
    newOrders:      orders.filter((o) => o.status === "NEW"),
    acceptedOrders: orders.filter((o) => o.status === "ACCEPTED"),
    preparingOrders:orders.filter((o) => o.status === "PREPARING"),
    readyOrders:    orders.filter((o) => o.status === "READY"),
    isPaused,
    newOrderIds,
    updateOrderStatus,
    togglePause,
  };
}

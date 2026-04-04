import type { Order, OrderStatus } from "../types";
import OrderCard from "./OrderCard";

interface StatusColumnProps {
  title: string;
  accentClass: string;        // border colour class e.g. "border-orange-500"
  countBgClass: string;       // bg colour class  e.g. "bg-orange-500"
  orders: Order[];
  newOrderIds: Set<string>;
  onUpdateStatus: (id: string, status: OrderStatus) => void;
  emptyMessage?: string;
}

export default function StatusColumn({
  title,
  accentClass,
  countBgClass,
  orders,
  newOrderIds,
  onUpdateStatus,
  emptyMessage = "No orders",
}: StatusColumnProps) {
  return (
    <div className="flex flex-col bg-zinc-950 overflow-hidden">
      {/* Column header */}
      <div className={`flex items-center justify-between px-3.5 py-3 bg-zinc-900 border-b-2 ${accentClass} shrink-0`}>
        <span className="font-mono text-[11px] font-semibold text-zinc-400 uppercase tracking-widest">
          {title}
        </span>
        <span className={`inline-flex items-center justify-center min-w-[22px] h-[22px] px-1.5 rounded-full font-mono text-[11px] font-bold text-black ${countBgClass}`}>
          {orders.length}
        </span>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto px-2.5 py-2.5 flex flex-col gap-2 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-zinc-700">
        {orders.length === 0 ? (
          <p className="py-8 text-center font-mono text-[11px] text-zinc-600 tracking-wide">
            {emptyMessage}
          </p>
        ) : (
          orders.map((order) => (
            <OrderCard
              key={order.id}
              order={order}
              isNew={newOrderIds.has(order.id)}
              onUpdateStatus={onUpdateStatus}
            />
          ))
        )}
      </div>
    </div>
  );
}

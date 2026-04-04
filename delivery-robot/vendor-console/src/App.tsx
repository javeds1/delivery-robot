import { useOrders } from "./hooks/useOrders";
import StatusColumn from "./components/StatusColumn";

export default function App() {
  const {
    newOrders,
    acceptedOrders,
    preparingOrders,
    readyOrders,
    isPaused,
    newOrderIds,
    updateOrderStatus,
    togglePause,
  } = useOrders();

  const totalActive =
    newOrders.length + acceptedOrders.length + preparingOrders.length;

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100 font-sans overflow-hidden">
      {/* ── Top bar ── */}
      <header className="grid grid-cols-3 items-center px-5 h-13 bg-zinc-900 border-b border-zinc-800 shrink-0">
        {/* Left: Live / Paused indicator */}
        <div className="flex items-center">
          <div className="flex items-center gap-1.5 font-mono text-[11px] text-zinc-500">
            <span
              className={[
                "w-1.5 h-1.5 rounded-full",
                isPaused
                  ? "bg-amber-400"
                  : "bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.7)] animate-pulse",
              ].join(" ")}
            />
            {isPaused ? "Intake paused" : "Live"}
          </div>
        </div>

        {/* Center: Brand */}
        <div className="flex items-center justify-center gap-2">
          <span className="w-2 h-2 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.7)]" />
          <span className="font-mono text-[18px] font-bold tracking-wide text-zinc-100">
            Campus Eats
          </span>
        </div>

        {/* Right: Controls */}
        <div className="flex items-center justify-end gap-3">
          <div className="flex items-baseline gap-1 px-2.5 py-1.5 bg-zinc-800 border border-zinc-700 rounded">
            <span className="font-mono text-base font-semibold text-zinc-100">{totalActive}</span>
            <span className="text-[11px] text-zinc-500">active</span>
          </div>
          <div className="flex items-baseline gap-1 px-2.5 py-1.5 bg-zinc-800 border border-zinc-700 rounded">
            <span className="font-mono text-base font-semibold text-zinc-100">{readyOrders.length}</span>
            <span className="text-[11px] text-zinc-500">ready</span>
          </div>

          <button
            onClick={togglePause}
            className={[
              "flex items-center gap-1.5 px-3.5 py-1.5 rounded text-[12px] font-semibold transition-colors",
              isPaused
                ? "bg-green-400 text-black hover:bg-green-300"
                : "bg-zinc-800 text-amber-400 border border-zinc-700 hover:bg-zinc-700",
            ].join(" ")}
          >
            {isPaused ? (
              <>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                Resume Intake
              </>
            ) : (
              <>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16" />
                  <rect x="14" y="4" width="4" height="16" />
                </svg>
                Pause Intake
              </>
            )}
          </button>
        </div>
      </header>

      {isPaused && (
        <div className="flex items-center justify-center gap-2 py-2 bg-amber-400/10 border-b border-amber-400/25 text-amber-400 font-mono text-[12px] font-medium tracking-wide shrink-0">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16" />
            <rect x="14" y="4" width="4" height="16" />
          </svg>
          Order intake is paused — no new orders are being accepted
        </div>
      )}

      <main className={`grid grid-cols-4 flex-1 gap-px bg-zinc-800 overflow-hidden transition-opacity duration-300 ${isPaused ? "opacity-70" : "opacity-100"}`}>
        <StatusColumn
          title="New Orders"
          accentClass="border-orange-500"
          countBgClass="bg-orange-500"
          orders={newOrders}
          newOrderIds={newOrderIds}
          onUpdateStatus={updateOrderStatus}
          emptyMessage="No new orders"
        />
        <StatusColumn
          title="Accepted"
          accentClass="border-blue-500"
          countBgClass="bg-blue-500"
          orders={acceptedOrders}
          newOrderIds={newOrderIds}
          onUpdateStatus={updateOrderStatus}
          emptyMessage="No accepted orders"
        />
        <StatusColumn
          title="Preparing"
          accentClass="border-purple-500"
          countBgClass="bg-purple-500"
          orders={preparingOrders}
          newOrderIds={newOrderIds}
          onUpdateStatus={updateOrderStatus}
          emptyMessage="No orders in prep"
        />
        <StatusColumn
          title="Ready"
          accentClass="border-green-500"
          countBgClass="bg-green-500"
          orders={readyOrders}
          newOrderIds={newOrderIds}
          onUpdateStatus={updateOrderStatus}
          emptyMessage="No orders ready"
        />
      </main>
    </div>
  );
}

import { useMemo, useState } from "react";
import type { MenuItem } from "../types";

interface MenuPageProps {
  items: MenuItem[];
  isLight?: boolean;
  onChange: (items: MenuItem[]) => void;
}

const EMPTY_FORM: Omit<MenuItem, "id"> = {
  name: "",
  category: "",
  price: 0,
  description: "",
  imageUrl: "",
  prepTimeMins: 5,
  isAvailable: true,
};

export default function MenuPage({ items, isLight = false, onChange }: MenuPageProps) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const kioskPayload = useMemo(
    () =>
      JSON.stringify(
        items
          .filter((item) => item.isAvailable)
          .map((item) => ({
            id: item.id,
            name: item.name,
            category: item.category,
            price: item.price,
            description: item.description,
            imageUrl: item.imageUrl,
            prepTimeMins: item.prepTimeMins,
          })),
        null,
        2
      ),
    [items]
  );

  function addItem() {
    if (!form.name.trim() || !form.category.trim()) return;
    const next: MenuItem = {
      id: `menu-${Date.now()}`,
      ...form,
      price: Number(form.price),
      prepTimeMins: Number(form.prepTimeMins),
    };
    onChange([next, ...items]);
    setForm(EMPTY_FORM);
    setShowAddForm(false);
  }

  function removeItem(id: string) {
    onChange(items.filter((item) => item.id !== id));
  }

  function toggleAvailable(id: string) {
    onChange(
      items.map((item) =>
        item.id === id ? { ...item, isAvailable: !item.isAvailable } : item
      )
    );
  }

  function startEdit(item: MenuItem) {
    setEditingId(item.id);
    setForm({
      name: item.name,
      category: item.category,
      price: item.price,
      description: item.description,
      imageUrl: item.imageUrl,
      prepTimeMins: item.prepTimeMins,
      isAvailable: item.isAvailable,
    });
    setShowAddForm(true);
  }

  function saveEdit() {
    if (!editingId) return;
    onChange(
      items.map((item) =>
        item.id === editingId
          ? {
              ...item,
              ...form,
              price: Number(form.price),
              prepTimeMins: Number(form.prepTimeMins),
            }
          : item
      )
    );
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowAddForm(false);
  }

  return (
    <div className="p-5 h-full overflow-y-auto space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="font-mono text-lg font-semibold">Menu Management</h2>
        <button
          onClick={() => {
            setEditingId(null);
            setForm(EMPTY_FORM);
            setShowAddForm((prev) => !prev);
          }}
          className="px-4 py-2 rounded bg-orange-500 hover:bg-orange-400 text-black font-semibold text-sm"
        >
          {showAddForm ? "Hide Form" : "Add New Item"}
        </button>
      </div>

      {showAddForm && (
        <div className={`rounded p-4 grid md:grid-cols-2 gap-3 border ${isLight ? "bg-white border-zinc-300" : "bg-zinc-900 border-zinc-800"}`}>
          <input
            className={`px-3 py-2 rounded border ${isLight ? "bg-white border-zinc-300" : "bg-zinc-800 border-zinc-700"}`}
            placeholder="Item name"
            value={form.name}
            onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
          />
          <input
            className={`px-3 py-2 rounded border ${isLight ? "bg-white border-zinc-300" : "bg-zinc-800 border-zinc-700"}`}
            placeholder="Category"
            value={form.category}
            onChange={(e) => setForm((prev) => ({ ...prev, category: e.target.value }))}
          />
          <input
            type="number"
            className={`px-3 py-2 rounded border ${isLight ? "bg-white border-zinc-300" : "bg-zinc-800 border-zinc-700"}`}
            placeholder="Price"
            value={form.price}
            onChange={(e) => setForm((prev) => ({ ...prev, price: Number(e.target.value) }))}
          />
          <input
            type="number"
            className={`px-3 py-2 rounded border ${isLight ? "bg-white border-zinc-300" : "bg-zinc-800 border-zinc-700"}`}
            placeholder="Prep time mins"
            value={form.prepTimeMins}
            onChange={(e) => setForm((prev) => ({ ...prev, prepTimeMins: Number(e.target.value) }))}
          />
          <input
            className={`px-3 py-2 rounded border md:col-span-2 ${isLight ? "bg-white border-zinc-300" : "bg-zinc-800 border-zinc-700"}`}
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
          />
          <input
            className={`px-3 py-2 rounded border md:col-span-2 ${isLight ? "bg-white border-zinc-300" : "bg-zinc-800 border-zinc-700"}`}
            placeholder="Image URL (for kiosk)"
            value={form.imageUrl}
            onChange={(e) => setForm((prev) => ({ ...prev, imageUrl: e.target.value }))}
          />
          <div className="md:col-span-2 flex gap-2">
            {editingId ? (
              <button onClick={saveEdit} className="px-4 py-2 rounded bg-blue-500 hover:bg-blue-400 text-white font-semibold text-sm">
                Save Item
              </button>
            ) : (
              <button onClick={addItem} className="px-4 py-2 rounded bg-orange-500 hover:bg-orange-400 text-black font-semibold text-sm">
                Add Menu Item
              </button>
            )}
            <button
              onClick={() => {
                setEditingId(null);
                setForm(EMPTY_FORM);
                setShowAddForm(false);
              }}
              className={`px-4 py-2 rounded border text-sm ${isLight ? "border-zinc-300 hover:bg-zinc-100" : "border-zinc-700 hover:bg-zinc-800"}`}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className={`rounded overflow-hidden border ${isLight ? "bg-white border-zinc-300" : "bg-zinc-900 border-zinc-800"}`}>
        <table className="w-full text-sm">
          <thead className={isLight ? "bg-zinc-100 text-zinc-600" : "bg-zinc-800 text-zinc-400"}>
            <tr>
              <th className="text-left px-3 py-2">Name</th>
              <th className="text-left px-3 py-2">Category</th>
              <th className="text-left px-3 py-2">Image</th>
              <th className="text-left px-3 py-2">Price</th>
              <th className="text-left px-3 py-2">Available</th>
              <th className="text-left px-3 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className={`border-t ${isLight ? "border-zinc-200" : "border-zinc-800"}`}>
                <td className="px-3 py-2">{item.name}</td>
                <td className="px-3 py-2">{item.category}</td>
                <td className="px-3 py-2">
                  {item.imageUrl ? (
                    <img src={item.imageUrl} alt={item.name} className="w-10 h-10 object-cover rounded border border-zinc-300" />
                  ) : (
                    <span className="text-xs text-zinc-500">No image</span>
                  )}
                </td>
                <td className="px-3 py-2">${item.price.toFixed(2)}</td>
                <td className="px-3 py-2">{item.isAvailable ? "Yes" : "No"}</td>
                <td className="px-3 py-2 flex gap-2">
                  <button onClick={() => startEdit(item)} className="px-2 py-1 rounded border border-blue-500/40 text-blue-300 text-xs">
                    Edit
                  </button>
                  <button onClick={() => toggleAvailable(item.id)} className="px-2 py-1 rounded border border-zinc-600 text-xs">
                    Toggle
                  </button>
                  <button onClick={() => removeItem(item.id)} className="px-2 py-1 rounded border border-red-500/40 text-red-300 text-xs">
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h3 className="font-mono text-sm text-zinc-300 mb-2">Kiosk payload preview</h3>
        <pre className={`border rounded p-3 text-xs overflow-x-auto ${isLight ? "bg-white border-zinc-300" : "bg-zinc-900 border-zinc-800"}`}>{kioskPayload}</pre>
      </div>
    </div>
  );
}

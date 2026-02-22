import { useState, useEffect } from 'react';
import api from '../services/api';

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  shipped: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const NEXT_STATUSES = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['shipped', 'cancelled'],
  shipped: ['delivered'],
  delivered: [],
  cancelled: [],
};

export default function AdminPage() {
  const [tab, setTab] = useState('orders');
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editProduct, setEditProduct] = useState(null);

  useEffect(() => {
    api.get('/categories').then((res) => setCategories(res.data));
    fetchOrders();
    fetchProducts();
  }, []);

  const fetchOrders = () => api.get('/admin/orders').then((res) => setOrders(res.data));
  const fetchProducts = () => api.get('/products', { params: { limit: 100 } }).then((res) => setProducts(res.data.items));

  const updateStatus = async (orderId, status) => {
    try {
      await api.put(`/admin/orders/${orderId}/status`, { status });
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error');
    }
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const data = {
      name: form.get('name'),
      description: form.get('description'),
      price: parseFloat(form.get('price')),
      stock: parseInt(form.get('stock')),
      category_id: parseInt(form.get('category_id')),
      image_url: form.get('image_url'),
    };

    try {
      if (editProduct) {
        await api.put(`/products/${editProduct.id}`, data);
      } else {
        await api.post('/products', data);
      }
      setShowForm(false);
      setEditProduct(null);
      fetchProducts();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error');
    }
  };

  const deleteProduct = async (id) => {
    if (!confirm('Delete this product?')) return;
    await api.delete(`/products/${id}`);
    fetchProducts();
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin Panel</h1>

      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setTab('orders')}
          className={`px-4 py-2 rounded cursor-pointer ${tab === 'orders' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
        >
          Orders
        </button>
        <button
          onClick={() => setTab('products')}
          className={`px-4 py-2 rounded cursor-pointer ${tab === 'products' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
        >
          Products
        </button>
      </div>

      {tab === 'orders' && (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <span className="font-semibold">Order #{order.id}</span>
                  <span className="text-gray-500 ml-2">User #{order.user_id}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[order.status]}`}>
                    {order.status}
                  </span>
                  <span className="font-bold">${order.total.toFixed(2)}</span>
                </div>
              </div>
              <div className="text-sm text-gray-500 mb-3">
                {order.items.map((i) => `${i.product.name} x${i.quantity}`).join(', ')}
              </div>
              {NEXT_STATUSES[order.status]?.length > 0 && (
                <div className="flex gap-2">
                  {NEXT_STATUSES[order.status].map((s) => (
                    <button
                      key={s}
                      onClick={() => updateStatus(order.id, s)}
                      className={`text-sm px-3 py-1 rounded cursor-pointer ${
                        s === 'cancelled' ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {orders.length === 0 && <p className="text-gray-500">No orders.</p>}
        </div>
      )}

      {tab === 'products' && (
        <div>
          <button
            onClick={() => { setShowForm(true); setEditProduct(null); }}
            className="mb-4 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 cursor-pointer"
          >
            Add Product
          </button>

          {showForm && (
            <form onSubmit={handleProductSubmit} className="bg-white p-6 rounded-lg shadow mb-6 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input name="name" required defaultValue={editProduct?.name || ''} className="border rounded w-full px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Price</label>
                <input name="price" type="number" step="0.01" required defaultValue={editProduct?.price || ''} className="border rounded w-full px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Stock</label>
                <input name="stock" type="number" required defaultValue={editProduct?.stock ?? 0} className="border rounded w-full px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <select name="category_id" required defaultValue={editProduct?.category_id || ''} className="border rounded w-full px-3 py-2">
                  <option value="">Select...</option>
                  {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea name="description" rows="2" defaultValue={editProduct?.description || ''} className="border rounded w-full px-3 py-2" />
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Image URL</label>
                <input name="image_url" defaultValue={editProduct?.image_url || ''} className="border rounded w-full px-3 py-2" />
              </div>
              <div className="col-span-2 flex gap-2">
                <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 cursor-pointer">
                  {editProduct ? 'Update' : 'Create'}
                </button>
                <button type="button" onClick={() => { setShowForm(false); setEditProduct(null); }} className="border px-4 py-2 rounded cursor-pointer">
                  Cancel
                </button>
              </div>
            </form>
          )}

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-medium">Name</th>
                  <th className="text-left px-4 py-3 text-sm font-medium">Category</th>
                  <th className="text-left px-4 py-3 text-sm font-medium">Price</th>
                  <th className="text-left px-4 py-3 text-sm font-medium">Stock</th>
                  <th className="text-right px-4 py-3 text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {products.map((p) => (
                  <tr key={p.id}>
                    <td className="px-4 py-3">{p.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{p.category.name}</td>
                    <td className="px-4 py-3">${p.price}</td>
                    <td className="px-4 py-3">{p.stock}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => { setEditProduct(p); setShowForm(true); }}
                        className="text-indigo-600 hover:underline mr-3 cursor-pointer"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteProduct(p.id)}
                        className="text-red-600 hover:underline cursor-pointer"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

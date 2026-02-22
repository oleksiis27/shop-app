import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function CartPage() {
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchCart = () => {
    api.get('/cart').then((res) => {
      setCart(res.data);
      setLoading(false);
    });
  };

  useEffect(() => { fetchCart(); }, []);

  const updateQuantity = async (itemId, quantity) => {
    try {
      await api.put(`/cart/items/${itemId}`, { quantity });
      fetchCart();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error');
    }
  };

  const removeItem = async (itemId) => {
    await api.delete(`/cart/items/${itemId}`);
    fetchCart();
  };

  const clearCart = async () => {
    await api.delete('/cart');
    fetchCart();
  };

  const checkout = async () => {
    try {
      await api.post('/orders');
      navigate('/orders');
    } catch (err) {
      alert(err.response?.data?.detail || 'Checkout failed');
    }
  };

  if (loading) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Shopping Cart</h1>

      {cart.items.length === 0 ? (
        <p className="text-gray-500">Your cart is empty.</p>
      ) : (
        <>
          <div className="space-y-4">
            {cart.items.map((item) => (
              <div key={item.id} className="flex items-center gap-4 bg-white p-4 rounded-lg shadow">
                <img
                  src={item.product.image_url}
                  alt={item.product.name}
                  className="w-20 h-20 object-cover rounded bg-gray-100"
                />
                <div className="flex-1">
                  <h3 className="font-semibold">{item.product.name}</h3>
                  <p className="text-gray-500">${item.product.price}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    disabled={item.quantity <= 1}
                    className="w-8 h-8 border rounded disabled:opacity-50 cursor-pointer disabled:cursor-default"
                  >
                    -
                  </button>
                  <span className="w-8 text-center">{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    className="w-8 h-8 border rounded cursor-pointer"
                  >
                    +
                  </button>
                </div>
                <p className="font-semibold w-24 text-right">
                  ${(item.product.price * item.quantity).toFixed(2)}
                </p>
                <button
                  onClick={() => removeItem(item.id)}
                  className="text-red-600 hover:text-red-800 cursor-pointer"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <button
              onClick={clearCart}
              className="text-red-600 hover:text-red-800 cursor-pointer"
            >
              Clear Cart
            </button>
            <div className="text-right">
              <p className="text-2xl font-bold mb-2">Total: ${cart.total.toFixed(2)}</p>
              <button
                onClick={checkout}
                className="bg-indigo-600 text-white px-8 py-3 rounded hover:bg-indigo-700 cursor-pointer"
              >
                Checkout
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

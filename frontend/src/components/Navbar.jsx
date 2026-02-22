import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-indigo-600">ShopApp</Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-gray-700 hover:text-indigo-600">Products</Link>
          {user ? (
            <>
              <Link to="/cart" className="text-gray-700 hover:text-indigo-600">Cart</Link>
              <Link to="/orders" className="text-gray-700 hover:text-indigo-600">Orders</Link>
              {user.role === 'admin' && (
                <Link to="/admin" className="text-gray-700 hover:text-indigo-600">Admin</Link>
              )}
              <span className="text-sm text-gray-500">{user.name}</span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800 cursor-pointer"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-indigo-600">Login</Link>
              <Link to="/register" className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

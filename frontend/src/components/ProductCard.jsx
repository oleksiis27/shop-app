import { Link } from 'react-router-dom';

export default function ProductCard({ product }) {
  return (
    <Link
      to={`/products/${product.id}`}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow overflow-hidden"
    >
      <img
        src={product.image_url}
        alt={product.name}
        className="w-full h-48 object-cover bg-gray-100"
      />
      <div className="p-4">
        <p className="text-xs text-indigo-600 mb-1">{product.category.name}</p>
        <h3 className="font-semibold text-gray-900 mb-1 truncate">{product.name}</h3>
        <p className="text-sm text-gray-500 mb-2 line-clamp-2">{product.description}</p>
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-gray-900">${product.price}</span>
          <span className={`text-xs ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {product.stock > 0 ? `In stock (${product.stock})` : 'Out of stock'}
          </span>
        </div>
      </div>
    </Link>
  );
}

import React from 'react';
import './ProductGrid.css'; // Подключаем стили


const ProductCard = ({ item }) => (
  <div className="product-card">
    <img src={item.image_url} alt={item.item_id} />
    <h4>{item.description}</h4>
  </div>
);


const ProductGrid = ({ items }) => {
  return (
    <div className="product-grid">
      {items && items.length > 0 ? (
        items.map((item) => (
          <ProductCard key={item.item_id} item={item} />
        ))
      ) : (
        <p>Загрузка товаров...</p>
      )}
    </div>
  );
};




export default ProductGrid;
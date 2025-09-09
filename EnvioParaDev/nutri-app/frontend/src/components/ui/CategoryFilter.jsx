import React from 'react';

const CategoryFilter = ({ categories, selectedCategory, onChange }) => {
  const handleChange = (e) => {
    // Converter para número ou nulo
    const value = e.target.value ? parseInt(e.target.value, 10) : null;
    onChange(value);
  };

  return (
    <div className="w-full">
      <select
        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        value={selectedCategory || ''}
        onChange={handleChange}
      >
        <option value="">Todas as categorias</option>
        {categories && categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.nome}
          </option>
        ))}
      </select>
    </div>
  );
};

export default CategoryFilter;

import React from 'react';
import Link from 'next/link';

const AlimentoCard = ({ alimento }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">
          {alimento.nome}
        </h3>
        <p className="text-sm text-gray-500 mb-3">
          Código: {alimento.codigo}
        </p>
        
        <div className="grid grid-cols-2 gap-2 mb-4">
          <div className="text-sm">
            <span className="text-gray-600 block">Energia</span>
            <span className="font-medium">{alimento.kcal} kcal</span>
          </div>
          <div className="text-sm">
            <span className="text-gray-600 block">Carboidratos</span>
            <span className="font-medium">{alimento.carboidratos}g</span>
          </div>
          <div className="text-sm">
            <span className="text-gray-600 block">Proteínas</span>
            <span className="font-medium">{alimento.proteina}g</span>
          </div>
          <div className="text-sm">
            <span className="text-gray-600 block">Gorduras</span>
            <span className="font-medium">{alimento.gordura}g</span>
          </div>
        </div>
        
        <Link href={`/alimentos/${alimento.id}`}>
          <a className="block w-full text-center py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors duration-300">
            Ver Detalhes
          </a>
        </Link>
      </div>
    </div>
  );
};

export default AlimentoCard;

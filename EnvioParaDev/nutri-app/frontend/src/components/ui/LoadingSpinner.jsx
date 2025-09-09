import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex justify-center items-center">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-700"></div>
      <span className="sr-only">Carregando...</span>
    </div>
  );
};

export default LoadingSpinner;

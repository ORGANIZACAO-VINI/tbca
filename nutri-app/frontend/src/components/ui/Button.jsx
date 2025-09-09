import React from 'react';

const Button = ({ children, onClick, primary, disabled, className }) => {
  const baseClasses = 'px-4 py-2 rounded-md transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2';
  const primaryClasses = 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500';
  const secondaryClasses = 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-400';
  const disabledClasses = 'opacity-50 cursor-not-allowed';

  const combinedClasses = `
    ${baseClasses}
    ${primary ? primaryClasses : secondaryClasses}
    ${disabled ? disabledClasses : ''}
    ${className || ''}
  `.trim();

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={combinedClasses}
    >
      {children}
    </button>
  );
};

export default Button;

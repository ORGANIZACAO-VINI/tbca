import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';

import { fetchAlimentos, calcularNutricional } from '../../services/api';
import { formatNutrient } from '../../utils/formatters';
import SearchBar from '../../components/ui/SearchBar';
import Button from '../../components/ui/Button';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

export default function Calculadora() {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [calculoResults, setCalculoResults] = useState(null);
  const [calculando, setCalculando] = useState(false);
  
  // Buscar alimentos quando o termo de busca mudar
  useEffect(() => {
    const searchTimeout = setTimeout(async () => {
      if (searchTerm.length >= 2) {
        try {
          setLoading(true);
          const results = await fetchAlimentos(searchTerm);
          setSearchResults(results);
        } catch (err) {
          console.error('Erro ao buscar alimentos:', err);
        } finally {
          setLoading(false);
        }
      } else {
        setSearchResults([]);
      }
    }, 300);
    
    return () => clearTimeout(searchTimeout);
  }, [searchTerm]);
  
  // Adicionar item à lista
  const addItem = (alimento) => {
    const newItem = {
      id: Date.now(),
      alimento_id: alimento.id,
      nome: alimento.nome,
      quantidade_g: 100,
      codigo: alimento.codigo,
      categoria: alimento.categoria_nome
    };
    
    setSelectedItems([...selectedItems, newItem]);
    setSearchTerm('');
  };
  
  // Atualizar quantidade
  const updateQuantidade = (id, quantidade) => {
    const updatedItems = selectedItems.map(item => {
      if (item.id === id) {
        return { ...item, quantidade_g: Number(quantidade) };
      }
      return item;
    });
    
    setSelectedItems(updatedItems);
  };
  
  // Remover item
  const removeItem = (id) => {
    setSelectedItems(selectedItems.filter(item => item.id !== id));
  };
  
  // Calcular valores nutricionais
  const calcular = async () => {
    if (selectedItems.length === 0) return;
    
    try {
      setCalculando(true);
      
      // Formatar dados para a API
      const requestData = selectedItems.map(item => ({
        alimento_id: item.alimento_id,
        quantidade_g: item.quantidade_g
      }));
      
      const results = await calcularNutricional(requestData);
      setCalculoResults(results);
    } catch (err) {
      console.error('Erro ao calcular valores:', err);
      alert('Ocorreu um erro ao calcular os valores nutricionais');
    } finally {
      setCalculando(false);
    }
  };
  
  // Limpar calculadora
  const limparCalculadora = () => {
    setSelectedItems([]);
    setCalculoResults(null);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <Head>
        <title>Calculadora Nutricional | NutriApp TBCA</title>
        <meta name="description" content="Calculadora de valores nutricionais baseada na TBCA" />
      </Head>
      
      <header className="mb-10">
        <div className="flex justify-between items-center mb-4">
          <Link href="/">
            <a className="text-green-600 hover:text-green-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
              Voltar para a página inicial
            </a>
          </Link>
        </div>
        
        <h1 className="text-3xl font-bold text-green-700 mb-2">Calculadora Nutricional</h1>
        <p className="text-gray-600">
          Calcule os valores nutricionais de refeições e combinações de alimentos.
        </p>
      </header>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Adicionar Alimentos</h2>
            
            <SearchBar 
              value={searchTerm} 
              onChange={setSearchTerm} 
              placeholder="Buscar alimento..." 
            />
            
            {loading ? (
              <div className="py-8 flex justify-center">
                <LoadingSpinner />
              </div>
            ) : (
              <div className="mt-4 max-h-96 overflow-y-auto">
                {searchResults.length > 0 ? (
                  <ul className="divide-y divide-gray-200">
                    {searchResults.map(alimento => (
                      <li key={alimento.id} className="py-3">
                        <div className="flex justify-between">
                          <div>
                            <h3 className="font-medium">{alimento.nome}</h3>
                            <p className="text-sm text-gray-500">{alimento.categoria_nome}</p>
                          </div>
                          <button 
                            onClick={() => addItem(alimento)}
                            className="text-green-600 hover:text-green-800"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  searchTerm.length >= 2 && (
                    <p className="py-4 text-center text-gray-500">
                      Nenhum alimento encontrado.
                    </p>
                  )
                )}
                
                {searchTerm.length < 2 && (
                  <p className="py-4 text-center text-gray-500">
                    Digite pelo menos 2 caracteres para buscar.
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Itens Selecionados</h2>
              {selectedItems.length > 0 && (
                <Button onClick={limparCalculadora}>
                  Limpar
                </Button>
              )}
            </div>
            
            {selectedItems.length > 0 ? (
              <div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Alimento
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Categoria
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Quantidade (g)
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Ações
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {selectedItems.map(item => (
                        <tr key={item.id}>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{item.nome}</div>
                            <div className="text-sm text-gray-500">{item.codigo}</div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="text-sm text-gray-500">{item.categoria}</div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <input
                              type="number"
                              className="w-20 p-1 border border-gray-300 rounded text-center"
                              value={item.quantidade_g}
                              onChange={(e) => updateQuantidade(item.id, e.target.value)}
                              min="1"
                            />
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <button 
                              onClick={() => removeItem(item.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                              </svg>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                <div className="mt-6 flex justify-end">
                  <Button 
                    primary 
                    onClick={calcular}
                    disabled={calculando}
                  >
                    {calculando ? 'Calculando...' : 'Calcular'}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-gray-500">
                <p>Nenhum item adicionado.</p>
                <p className="mt-2">Busque e adicione alimentos para calcular os valores nutricionais.</p>
              </div>
            )}
          </div>
          
          {calculoResults && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">Resultado</h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Energia</p>
                  <p className="text-xl font-bold text-green-800">{formatNutrient(calculoResults.kcal, ' kcal')}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Carboidratos</p>
                  <p className="text-xl font-bold text-green-800">{formatNutrient(calculoResults.carboidratos)}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Proteínas</p>
                  <p className="text-xl font-bold text-green-800">{formatNutrient(calculoResults.proteina)}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Gorduras</p>
                  <p className="text-xl font-bold text-green-800">{formatNutrient(calculoResults.gordura)}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Fibras</p>
                  <p className="text-xl font-bold text-green-800">{formatNutrient(calculoResults.fibras)}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Cálcio</p>
                  <p className="text-xl font-bold text-green-800">{formatNutrient(calculoResults.calcio, ' mg')}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Ferro</p>
                  <p className="text-xl font-bold text-green-800">{formatNutrient(calculoResults.ferro, ' mg')}</p>
                </div>
              </div>
              
              <div className="mt-6 flex justify-end space-x-4">
                <Button onClick={() => window.print()}>
                  Imprimir
                </Button>
                <Button primary>
                  Salvar no Diário
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

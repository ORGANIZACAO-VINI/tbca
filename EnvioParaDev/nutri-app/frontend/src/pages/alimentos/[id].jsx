import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';

import { fetchAlimento } from '../../services/api';
import { formatNutrient, generateColorFromName } from '../../utils/formatters';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Button from '../../components/ui/Button';

export default function AlimentoDetail() {
  const router = useRouter();
  const { id } = router.query;
  
  const [alimento, setAlimento] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // Buscar dados do alimento quando o ID estiver disponível
    if (id) {
      async function loadAlimento() {
        try {
          setLoading(true);
          const data = await fetchAlimento(id);
          setAlimento(data);
          setError(null);
        } catch (err) {
          console.error('Erro ao carregar alimento:', err);
          setError('Não foi possível carregar os dados do alimento.');
        } finally {
          setLoading(false);
        }
      }
      
      loadAlimento();
    }
  }, [id]);
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="flex justify-center my-12">
          <LoadingSpinner />
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="bg-red-100 text-red-700 p-6 rounded-lg">
          <h2 className="text-xl font-bold mb-2">Erro</h2>
          <p>{error}</p>
          <Button onClick={() => router.push('/')} className="mt-4">
            Voltar para a página inicial
          </Button>
        </div>
      </div>
    );
  }
  
  if (!alimento) {
    return null;
  }
  
  // Cor gerada com base na categoria
  const categoryColor = generateColorFromName(alimento.categoria_nome);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <Head>
        <title>{alimento.nome} | NutriApp TBCA</title>
        <meta name="description" content={`Informações nutricionais de ${alimento.nome}`} />
      </Head>
      
      <div className="mb-6">
        <Link href="/">
          <a className="text-green-600 hover:text-green-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Voltar para a busca
          </a>
        </Link>
      </div>
      
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="p-6">
          <div className="flex items-center mb-4">
            <span 
              className="px-3 py-1 text-sm rounded-full text-white mr-3"
              style={{ backgroundColor: categoryColor }}
            >
              {alimento.categoria_nome}
            </span>
            <span className="text-gray-600 text-sm">
              Código: {alimento.codigo}
            </span>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            {alimento.nome}
          </h1>
          
          {alimento.nome_cientifico && (
            <p className="text-gray-600 italic mb-4">
              {alimento.nome_cientifico}
            </p>
          )}
          
          <hr className="my-6" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4 text-green-700">
                Informações Nutricionais
              </h2>
              
              <div className="bg-green-50 rounded-lg p-4">
                <table className="w-full">
                  <tbody>
                    <tr className="border-b border-green-100">
                      <th className="text-left py-3">Energia</th>
                      <td className="text-right font-medium">{formatNutrient(alimento.kcal, ' kcal')}</td>
                    </tr>
                    <tr className="border-b border-green-100">
                      <th className="text-left py-3">Carboidratos</th>
                      <td className="text-right font-medium">{formatNutrient(alimento.carboidratos)}</td>
                    </tr>
                    <tr className="border-b border-green-100">
                      <th className="text-left py-3">Proteínas</th>
                      <td className="text-right font-medium">{formatNutrient(alimento.proteina)}</td>
                    </tr>
                    <tr className="border-b border-green-100">
                      <th className="text-left py-3">Gorduras</th>
                      <td className="text-right font-medium">{formatNutrient(alimento.gordura)}</td>
                    </tr>
                    <tr className="border-b border-green-100">
                      <th className="text-left py-3">Fibras</th>
                      <td className="text-right font-medium">{formatNutrient(alimento.fibras)}</td>
                    </tr>
                    <tr className="border-b border-green-100">
                      <th className="text-left py-3">Cálcio</th>
                      <td className="text-right font-medium">{formatNutrient(alimento.calcio, ' mg')}</td>
                    </tr>
                    <tr>
                      <th className="text-left py-3">Ferro</th>
                      <td className="text-right font-medium">{formatNutrient(alimento.ferro, ' mg')}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <p className="text-sm text-gray-600 mt-2">
                * Valores por 100g de alimento
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-4 text-green-700">
                Composição Nutricional
              </h2>
              
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                {/* Aqui seria inserido um gráfico com Chart.js */}
                <p className="text-gray-500">Gráfico de composição nutricional</p>
              </div>
              
              <div className="mt-8">
                <h2 className="text-xl font-semibold mb-4 text-green-700">
                  Adicionar à Calculadora
                </h2>
                
                <div className="flex space-x-4">
                  <input
                    type="number"
                    className="border border-gray-300 rounded px-3 py-2 w-24"
                    placeholder="Gramas"
                    min="1"
                  />
                  <Button primary>
                    Adicionar
                  </Button>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-10">
            <h2 className="text-xl font-semibold mb-4 text-green-700">
              Alimentos Similares
            </h2>
            
            <div className="bg-gray-100 p-8 rounded-lg text-center">
              <p className="text-gray-500">Lista de alimentos similares aparecerá aqui</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Página inicial do aplicativo web de nutrição TBCA

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';

// Componentes
import AlimentoCard from '../components/alimentos/AlimentoCard';
import SearchBar from '../components/ui/SearchBar';
import CategoryFilter from '../components/ui/CategoryFilter';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';

// Serviços API
import { fetchAlimentos, fetchCategorias } from '../services/api';

export default function Home() {
  // Estados
  const [alimentos, setAlimentos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategoria, setSelectedCategoria] = useState(null);
  const [pagina, setPagina] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Buscar dados iniciais
  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoading(true);
        
        // Buscar categorias
        const categoriasData = await fetchCategorias();
        setCategorias(categoriasData);
        
        // Buscar alimentos
        const alimentosData = await fetchAlimentos();
        setAlimentos(alimentosData);
        
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
        setError('Não foi possível carregar os dados. Tente novamente mais tarde.');
      } finally {
        setLoading(false);
      }
    }
    
    loadInitialData();
  }, []);
  
  // Buscar alimentos quando os filtros mudam
  useEffect(() => {
    async function loadFilteredData() {
      try {
        setLoading(true);
        const alimentosData = await fetchAlimentos(searchTerm, selectedCategoria, pagina);
        setAlimentos(alimentosData);
        setError(null);
      } catch (err) {
        console.error('Erro ao filtrar dados:', err);
        setError('Não foi possível aplicar os filtros. Tente novamente mais tarde.');
      } finally {
        setLoading(false);
      }
    }
    
    // Adicionar um pequeno delay para evitar muitas requisições durante digitação
    const timeoutId = setTimeout(() => {
      loadFilteredData();
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedCategoria, pagina]);
  
  // Manipuladores de eventos
  const handleSearch = (term) => {
    setSearchTerm(term);
    setPagina(1); // Resetar para a primeira página ao pesquisar
  };
  
  const handleCategoryChange = (categoryId) => {
    setSelectedCategoria(categoryId);
    setPagina(1); // Resetar para a primeira página ao mudar categoria
  };
  
  const handleNextPage = () => {
    setPagina(pagina + 1);
  };
  
  const handlePrevPage = () => {
    if (pagina > 1) {
      setPagina(pagina - 1);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <Head>
        <title>NutriApp TBCA - Tabela Brasileira de Composição de Alimentos</title>
        <meta name="description" content="Aplicativo de nutrição baseado nos dados da TBCA" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-green-700 mb-2">NutriApp TBCA</h1>
        <p className="text-lg text-gray-600">
          Explore os dados nutricionais da Tabela Brasileira de Composição de Alimentos
        </p>
      </header>
      
      <div className="mb-8 bg-green-50 p-6 rounded-lg shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <SearchBar 
              value={searchTerm} 
              onChange={handleSearch} 
              placeholder="Buscar alimentos (ex: arroz, banana, leite...)" 
            />
          </div>
          <div>
            <CategoryFilter 
              categories={categorias} 
              selectedCategory={selectedCategoria}
              onChange={handleCategoryChange}
            />
          </div>
        </div>
        
        <div className="mt-4 flex justify-center gap-4">
          <Link href="/calculadora">
            <Button primary>Calculadora Nutricional</Button>
          </Link>
          <Link href="/diario">
            <Button>Diário Alimentar</Button>
          </Link>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center my-12">
          <LoadingSpinner />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
            {alimentos.length > 0 ? (
              alimentos.map((alimento) => (
                <AlimentoCard key={alimento.id} alimento={alimento} />
              ))
            ) : (
              <div className="col-span-full text-center py-12 text-gray-500">
                Nenhum alimento encontrado com os filtros atuais.
              </div>
            )}
          </div>
          
          <div className="flex justify-center gap-4 mt-8">
            <Button onClick={handlePrevPage} disabled={pagina === 1}>
              Anterior
            </Button>
            <span className="self-center px-4 py-2 bg-gray-100 rounded-md">
              Página {pagina}
            </span>
            <Button onClick={handleNextPage} disabled={alimentos.length < 12}>
              Próxima
            </Button>
          </div>
        </>
      )}
      
      <footer className="mt-16 pt-8 border-t border-gray-200 text-center text-gray-600">
        <p>© 2025 NutriApp TBCA - Dados da Tabela Brasileira de Composição de Alimentos</p>
      </footer>
    </div>
  );
}

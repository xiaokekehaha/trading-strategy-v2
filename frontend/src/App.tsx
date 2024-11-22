import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Portfolio } from './pages/Portfolio';
import { Analysis } from './pages/Analysis';

const queryClient = new QueryClient();

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow-sm">
            <div className="container mx-auto px-4 py-4">
              <div className="flex justify-between items-center">
                <h1 className="text-xl font-semibold">量化交易分析平台</h1>
                <div className="space-x-4">
                  <Link 
                    to="/" 
                    className="text-gray-600 hover:text-gray-900"
                  >
                    投资组合
                  </Link>
                  <Link 
                    to="/analysis" 
                    className="text-gray-600 hover:text-gray-900"
                  >
                    策略分析
                  </Link>
                </div>
              </div>
            </div>
          </nav>
          
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Portfolio />} />
              <Route path="/analysis" element={<Analysis />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}; 
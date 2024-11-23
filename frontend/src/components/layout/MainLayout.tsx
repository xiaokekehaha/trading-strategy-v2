'use client';

import React from 'react';
import Navbar from './Navbar';
import StockList from './StockList';

interface Props {
  children: React.ReactNode;
}

const MainLayout: React.FC<Props> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex pt-16 h-[calc(100vh-4rem)]">
        <StockList />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout; 
'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Bell, Settings, Search, Globe } from 'lucide-react';
import { MARKETS } from '@/lib/constants';

const Navbar = () => {
  const [currentMarket, setCurrentMarket] = useState('US');
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState([]);
  
  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50">
      <div className="h-full max-w-7xl mx-auto px-4 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold text-blue-600">TradeAnalysis</span>
        </Link>
        
        {/* Market Selector */}
        <div className="flex items-center space-x-4">
          {MARKETS.map(market => (
            <button
              key={market.id}
              onClick={() => setCurrentMarket(market.id)}
              className={`px-3 py-1.5 rounded-md transition-colors ${
                currentMarket === market.id
                  ? 'bg-blue-100 text-blue-600'
                  : 'hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center space-x-1">
                <Globe className="w-4 h-4" />
                <span>{market.name}</span>
              </div>
            </button>
          ))}
        </div>
        
        {/* Search Bar */}
        <div className="flex-1 max-w-lg mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索股票代码或公司名称..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        {/* Right Actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="relative p-2 rounded-full hover:bg-gray-100">
            <Bell className="w-6 h-6 text-gray-600" />
            {notifications.length > 0 && (
              <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
                {notifications.length}
              </span>
            )}
          </button>
          
          {/* Settings */}
          <button className="p-2 rounded-full hover:bg-gray-100">
            <Settings className="w-6 h-6 text-gray-600" />
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 
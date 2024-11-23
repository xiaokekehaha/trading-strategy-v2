'use client';

import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable, DroppableProvided, DraggableProvided } from 'react-beautiful-dnd';
import { Plus, X, ChevronDown, ChevronUp } from 'lucide-react';

interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  group?: string;
}

interface StockGroup {
  name: string;
  stocks: Stock[];
  isExpanded: boolean;
}

const StockList = () => {
  const [groups, setGroups] = useState<StockGroup[]>([
    {
      name: '自选股',
      stocks: [],
      isExpanded: true
    },
    {
      name: '关注股',
      stocks: [],
      isExpanded: true
    }
  ]);
  
  const handleDragEnd = (result: any) => {
    if (!result.destination) return;
    
    const { source, destination } = result;
    const sourceGroup = groups.find(g => `group-${g.name}` === source.droppableId);
    const destGroup = groups.find(g => `group-${g.name}` === destination.droppableId);
    
    if (!sourceGroup || !destGroup) return;
    
    const newGroups = [...groups];
    const [movedStock] = sourceGroup.stocks.splice(source.index, 1);
    destGroup.stocks.splice(destination.index, 0, movedStock);
    
    setGroups(newGroups);
  };
  
  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full overflow-y-auto">
      <div className="p-4">
        <button className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
          <Plus className="w-5 h-5" />
          <span>添加股票</span>
        </button>
      </div>
      
      <DragDropContext onDragEnd={handleDragEnd}>
        {groups.map(group => (
          <div key={group.name} className="mb-4">
            <div 
              className="px-4 py-2 flex items-center justify-between cursor-pointer hover:bg-gray-50"
              onClick={() => {
                setGroups(groups.map(g => 
                  g.name === group.name 
                    ? { ...g, isExpanded: !g.isExpanded }
                    : g
                ));
              }}
            >
              <span className="font-medium text-gray-700">{group.name}</span>
              {group.isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {group.isExpanded && (
              <Droppable droppableId={`group-${group.name}`}>
                {(provided: DroppableProvided) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className="space-y-1 p-2"
                  >
                    {group.stocks.map((stock, index) => (
                      <Draggable
                        key={stock.symbol}
                        draggableId={stock.symbol}
                        index={index}
                      >
                        {(provided: DraggableProvided) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className="p-3 bg-white rounded-lg shadow-sm hover:shadow transition-shadow"
                          >
                            <div className="flex justify-between items-start">
                              <div>
                                <div className="font-medium">{stock.symbol}</div>
                                <div className="text-sm text-gray-500">{stock.name}</div>
                              </div>
                              <button 
                                className="p-1 hover:bg-gray-100 rounded-full"
                                onClick={() => {
                                  setGroups(groups.map(g => ({
                                    ...g,
                                    stocks: g.stocks.filter(s => s.symbol !== stock.symbol)
                                  })));
                                }}
                              >
                                <X className="w-4 h-4 text-gray-400" />
                              </button>
                            </div>
                            <div className="mt-2 flex justify-between items-center">
                              <span className="text-lg font-semibold">{stock.price}</span>
                              <span className={`text-sm ${
                                stock.change >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                              </span>
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            )}
          </div>
        ))}
      </DragDropContext>
    </div>
  );
};

export default StockList; 
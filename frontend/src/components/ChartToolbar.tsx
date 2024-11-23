'use client';

import React from 'react';
import { Camera, Download, Share2, BarChart2 } from 'lucide-react';
import { saveAs } from 'file-saver';
import html2canvas from 'html2canvas';

interface Props {
  chartRef: React.RefObject<HTMLDivElement>;
  onCompare: () => void;
}

const ChartToolbar: React.FC<Props> = ({ chartRef, onCompare }) => {
  const handleScreenshot = async () => {
    if (!chartRef.current) return;
    
    try {
      const canvas = await html2canvas(chartRef.current);
      canvas.toBlob((blob: Blob | null) => {
        if (blob) {
          saveAs(blob, 'chart-screenshot.png');
        }
      });
    } catch (error) {
      console.error('截图失败:', error);
    }
  };

  const handleExport = () => {
    // TODO: 实现数据导出功能
  };

  const handleShare = () => {
    // TODO: 实现分享功能
  };

  return (
    <div className="flex items-center space-x-2 p-2 bg-white rounded-lg shadow">
      <button
        onClick={handleScreenshot}
        className="p-2 hover:bg-gray-100 rounded-lg tooltip"
        data-tip="截图"
      >
        <Camera className="w-5 h-5 text-gray-600" />
      </button>
      
      <button
        onClick={handleExport}
        className="p-2 hover:bg-gray-100 rounded-lg tooltip"
        data-tip="导出数据"
      >
        <Download className="w-5 h-5 text-gray-600" />
      </button>
      
      <button
        onClick={handleShare}
        className="p-2 hover:bg-gray-100 rounded-lg tooltip"
        data-tip="分享"
      >
        <Share2 className="w-5 h-5 text-gray-600" />
      </button>
      
      <button
        onClick={onCompare}
        className="p-2 hover:bg-gray-100 rounded-lg tooltip"
        data-tip="图表对比"
      >
        <BarChart2 className="w-5 h-5 text-gray-600" />
      </button>
    </div>
  );
};

export default ChartToolbar; 
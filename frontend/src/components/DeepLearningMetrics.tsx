'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TrainingHistory {
  loss: number[];
  accuracy: number[];
  val_loss?: number[];
  val_accuracy?: number[];
}

interface Props {
  trainingHistory: TrainingHistory;
}

const DeepLearningMetrics: React.FC<Props> = ({ trainingHistory }) => {
  const epochs = Array.from({ length: trainingHistory.loss.length }, (_, i) => i + 1);
  
  const options: ChartOptions<'line'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '模型训练历史'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  const lossData = {
    labels: epochs,
    datasets: [
      {
        label: '训练损失',
        data: trainingHistory.loss,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      ...(trainingHistory.val_loss ? [{
        label: '验证损失',
        data: trainingHistory.val_loss,
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      }] : [])
    ]
  };

  const accuracyData = {
    labels: epochs,
    datasets: [
      {
        label: '训练准确率',
        data: trainingHistory.accuracy,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
      ...(trainingHistory.val_accuracy ? [{
        label: '验证准确率',
        data: trainingHistory.val_accuracy,
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.5)',
      }] : [])
    ]
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">深度学习模型指标</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-base font-medium mb-2">损失函数曲线</h4>
          <Line options={options} data={lossData} />
        </div>
        <div>
          <h4 className="text-base font-medium mb-2">准确率曲线</h4>
          <Line options={options} data={accuracyData} />
        </div>
      </div>
      
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          title="最终训练损失"
          value={trainingHistory.loss[trainingHistory.loss.length - 1]?.toFixed(4) || 'N/A'}
        />
        <MetricCard
          title="最终训练准确率"
          value={`${(trainingHistory.accuracy[trainingHistory.accuracy.length - 1] * 100)?.toFixed(2)}%` || 'N/A'}
        />
        {trainingHistory.val_loss && trainingHistory.val_loss.length > 0 && (
          <MetricCard
            title="最终验证损失"
            value={trainingHistory.val_loss[trainingHistory.val_loss.length - 1]?.toFixed(4) || 'N/A'}
          />
        )}
        {trainingHistory.val_accuracy && trainingHistory.val_accuracy.length > 0 && (
          <MetricCard
            title="最终验证准确率"
            value={`${(trainingHistory.val_accuracy[trainingHistory.val_accuracy.length - 1] * 100)?.toFixed(2)}%` || 'N/A'}
          />
        )}
      </div>
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value }) => {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h5 className="text-sm text-gray-500">{title}</h5>
      <p className="text-xl font-semibold text-gray-900">{value}</p>
    </div>
  );
};

export default DeepLearningMetrics; 
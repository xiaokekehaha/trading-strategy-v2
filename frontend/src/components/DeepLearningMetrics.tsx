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
  Legend
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

interface Props {
  trainingHistory: {
    loss: number[];
    accuracy: number[];
    val_loss?: number[];
    val_accuracy?: number[];
  };
}

const DeepLearningMetrics: React.FC<Props> = ({ trainingHistory }) => {
  const options = {
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

  const data = {
    labels: Array.from({ length: trainingHistory.loss.length }, (_, i) => i + 1),
    datasets: [
      {
        label: '训练损失',
        data: trainingHistory.loss,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: '训练准确率',
        data: trainingHistory.accuracy,
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
      ...(trainingHistory.val_loss ? [{
        label: '验证损失',
        data: trainingHistory.val_loss,
        borderColor: 'rgb(255, 159, 64)',
        backgroundColor: 'rgba(255, 159, 64, 0.5)',
      }] : []),
      ...(trainingHistory.val_accuracy ? [{
        label: '验证准确率',
        data: trainingHistory.val_accuracy,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      }] : [])
    ]
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h3 className="text-lg font-medium text-gray-900 mb-4">深度学习模型性能</h3>
      <Line options={options} data={data} />
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-gray-600">最终训练损失</p>
          <p className="text-lg font-semibold">
            {trainingHistory.loss[trainingHistory.loss.length - 1].toFixed(4)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">最终训练准确率</p>
          <p className="text-lg font-semibold">
            {(trainingHistory.accuracy[trainingHistory.accuracy.length - 1] * 100).toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  );
};

export default DeepLearningMetrics; 
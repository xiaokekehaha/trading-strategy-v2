'use client';

import React, { useState } from 'react';
import { 
  TrendingUp, 
  Type, 
  Image, 
  Square,
  Circle,
  Triangle,
  Minus,
  X
} from 'lucide-react';

type AnnotationType = 'trendline' | 'text' | 'image' | 'shape';
type ShapeType = 'square' | 'circle' | 'triangle';

interface Annotation {
  id: string;
  type: AnnotationType;
  x: number;
  y: number;
  content?: string;
  shape?: ShapeType;
  points?: { x: number; y: number }[];
}

interface Props {
  onAnnotationAdd: (annotation: Annotation) => void;
  onAnnotationRemove: (id: string) => void;
}

const ChartAnnotation: React.FC<Props> = ({
  onAnnotationAdd,
  onAnnotationRemove
}) => {
  const [activeType, setActiveType] = useState<AnnotationType | null>(null);
  const [activeShape, setActiveShape] = useState<ShapeType | null>(null);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentPoints, setCurrentPoints] = useState<{ x: number; y: number }[]>([]);

  const handleToolSelect = (type: AnnotationType) => {
    setActiveType(type === activeType ? null : type);
    setActiveShape(null);
  };

  const handleShapeSelect = (shape: ShapeType) => {
    setActiveShape(shape === activeShape ? null : shape);
    setActiveType('shape');
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!activeType) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (activeType === 'trendline') {
      setIsDrawing(true);
      setCurrentPoints([{ x, y }]);
    } else {
      const newAnnotation: Annotation = {
        id: Date.now().toString(),
        type: activeType,
        x,
        y,
        ...(activeType === 'shape' && { shape: activeShape || 'square' }),
        ...(activeType === 'text' && { content: '' })
      };

      setAnnotations([...annotations, newAnnotation]);
      onAnnotationAdd(newAnnotation);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setCurrentPoints([currentPoints[0], { x, y }]);
  };

  const handleMouseUp = () => {
    if (isDrawing && currentPoints.length === 2) {
      const newAnnotation: Annotation = {
        id: Date.now().toString(),
        type: 'trendline',
        x: currentPoints[0].x,
        y: currentPoints[0].y,
        points: currentPoints
      };

      setAnnotations([...annotations, newAnnotation]);
      onAnnotationAdd(newAnnotation);
    }

    setIsDrawing(false);
    setCurrentPoints([]);
  };

  const handleAnnotationRemove = (id: string) => {
    setAnnotations(annotations.filter(a => a.id !== id));
    onAnnotationRemove(id);
  };

  return (
    <div className="flex flex-col space-y-2">
      <div className="flex items-center space-x-2 p-2 bg-white rounded-lg shadow">
        <button
          onClick={() => handleToolSelect('trendline')}
          className={`p-2 rounded-lg ${
            activeType === 'trendline' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
          }`}
        >
          <TrendingUp className="w-5 h-5" />
        </button>

        <button
          onClick={() => handleToolSelect('text')}
          className={`p-2 rounded-lg ${
            activeType === 'text' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
          }`}
        >
          <Type className="w-5 h-5" />
        </button>

        <button
          onClick={() => handleToolSelect('image')}
          className={`p-2 rounded-lg ${
            activeType === 'image' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
          }`}
        >
          <Image className="w-5 h-5" />
        </button>

        <div className="h-6 w-px bg-gray-200" />

        <button
          onClick={() => handleShapeSelect('square')}
          className={`p-2 rounded-lg ${
            activeShape === 'square' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
          }`}
        >
          <Square className="w-5 h-5" />
        </button>

        <button
          onClick={() => handleShapeSelect('circle')}
          className={`p-2 rounded-lg ${
            activeShape === 'circle' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
          }`}
        >
          <Circle className="w-5 h-5" />
        </button>

        <button
          onClick={() => handleShapeSelect('triangle')}
          className={`p-2 rounded-lg ${
            activeShape === 'triangle' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
          }`}
        >
          <Triangle className="w-5 h-5" />
        </button>
      </div>

      <div 
        className="relative w-full h-[400px] border border-gray-200 rounded-lg"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {annotations.map(annotation => (
          <div
            key={annotation.id}
            className="absolute"
            style={{ left: annotation.x, top: annotation.y }}
          >
            {annotation.type === 'trendline' && annotation.points && (
              <svg
                className="absolute"
                style={{
                  width: Math.abs(annotation.points[1].x - annotation.points[0].x),
                  height: Math.abs(annotation.points[1].y - annotation.points[0].y)
                }}
              >
                <line
                  x1={0}
                  y1={0}
                  x2={annotation.points[1].x - annotation.points[0].x}
                  y2={annotation.points[1].y - annotation.points[0].y}
                  stroke="black"
                  strokeWidth="2"
                />
              </svg>
            )}

            {annotation.type === 'text' && (
              <textarea
                className="border-none bg-transparent resize-none focus:outline-none"
                defaultValue={annotation.content}
                placeholder="输入文字..."
              />
            )}

            {annotation.type === 'shape' && (
              <div
                className={`w-10 h-10 border-2 border-black ${
                  annotation.shape === 'circle' ? 'rounded-full' :
                  annotation.shape === 'triangle' ? 'clip-path-triangle' : ''
                }`}
              />
            )}

            <button
              className="absolute -top-2 -right-2 p-1 bg-red-500 rounded-full text-white"
              onClick={() => handleAnnotationRemove(annotation.id)}
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}

        {isDrawing && currentPoints.length === 2 && (
          <svg
            className="absolute"
            style={{
              left: currentPoints[0].x,
              top: currentPoints[0].y,
              width: Math.abs(currentPoints[1].x - currentPoints[0].x),
              height: Math.abs(currentPoints[1].y - currentPoints[0].y)
            }}
          >
            <line
              x1={0}
              y1={0}
              x2={currentPoints[1].x - currentPoints[0].x}
              y2={currentPoints[1].y - currentPoints[0].y}
              stroke="black"
              strokeWidth="2"
              strokeDasharray="4"
            />
          </svg>
        )}
      </div>
    </div>
  );
};

export default ChartAnnotation; 
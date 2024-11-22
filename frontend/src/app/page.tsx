import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">量化交易分析平台</h1>
        <nav className="space-x-4">
          <Link 
            href="/analysis" 
            className="text-blue-600 hover:text-blue-800 underline"
          >
            策略分析
          </Link>
          <Link 
            href="/portfolio" 
            className="text-blue-600 hover:text-blue-800 underline"
          >
            投资组合
          </Link>
        </nav>
      </div>
    </main>
  );
} 
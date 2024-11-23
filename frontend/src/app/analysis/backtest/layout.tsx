export default function BacktestLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#0F172A] text-white">
      {children}
    </div>
  );
} 
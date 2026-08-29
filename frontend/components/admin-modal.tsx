"use client";

export function Modal({
  title,
  children,
  onClose,
}: {
  title: string;
  children: React.ReactNode;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div className="card w-full max-w-md space-y-4 p-6" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-[15px] font-semibold">{title}</h2>
        {children}
      </div>
    </div>
  );
}

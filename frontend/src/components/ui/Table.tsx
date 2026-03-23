import React from 'react';

export interface Column<T> {
  key: keyof T;
  header: string;
}

interface TableProps<T extends Record<string, unknown>> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptySlot?: React.ReactNode;
}

function SkeletonRow({ cols }: { cols: number }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-slate-200 rounded animate-pulse" />
        </td>
      ))}
    </tr>
  );
}

export function Table<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  emptySlot,
}: TableProps<T>) {
  // Card-based stacked layout for mobile (<640px), table for sm+
  return (
    <div>
      {/* Desktop table */}
      <div className="hidden sm:block overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200" data-testid="table">
          <thead className="bg-slate-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  scope="col"
                  className="px-4 py-3 text-left text-xs font-medium text-[#64748b] uppercase tracking-wider"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-100">
            {loading ? (
              <>
                <SkeletonRow cols={columns.length} />
                <SkeletonRow cols={columns.length} />
                <SkeletonRow cols={columns.length} />
              </>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-[#64748b]">
                  {emptySlot ?? 'No data available'}
                </td>
              </tr>
            ) : (
              data.map((row, rowIdx) => (
                <tr key={rowIdx} className="hover:bg-slate-50">
                  {columns.map((col) => (
                    <td key={String(col.key)} className="px-4 py-3 text-sm text-slate-700">
                      {String(row[col.key] ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile card layout */}
      <div className="sm:hidden space-y-3" data-testid="table-mobile">
        {loading ? (
          <>
            {[0, 1, 2].map((i) => (
              <div key={i} className="rounded-lg border border-slate-200 p-4 space-y-2">
                {columns.map((col) => (
                  <div key={String(col.key)} className="h-4 bg-slate-200 rounded animate-pulse" />
                ))}
              </div>
            ))}
          </>
        ) : data.length === 0 ? (
          <div className="text-center text-[#64748b] py-8">{emptySlot ?? 'No data available'}</div>
        ) : (
          data.map((row, rowIdx) => (
            <div key={rowIdx} className="rounded-lg border border-slate-200 p-4 space-y-1">
              {columns.map((col) => (
                <div key={String(col.key)} className="flex justify-between text-sm">
                  <span className="font-medium text-[#64748b]">{col.header}</span>
                  <span className="text-slate-700">{String(row[col.key] ?? '')}</span>
                </div>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

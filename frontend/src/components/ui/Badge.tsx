import React from 'react';
import type { Role } from './types';

const roleClasses: Record<Role, string> = {
  admin:      'bg-purple-100 text-purple-800 role-admin',
  doctor:     'bg-blue-100 text-blue-800 role-doctor',
  nurse:      'bg-green-100 text-green-800 role-nurse',
  researcher: 'bg-amber-100 text-amber-800 role-researcher',
  patient:    'bg-slate-100 text-slate-800 role-patient',
};

interface BadgeProps {
  role: Role;
  className?: string;
}

export function Badge({ role, className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${roleClasses[role]} ${className}`}
    >
      {role}
    </span>
  );
}

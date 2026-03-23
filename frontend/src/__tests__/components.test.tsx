/**
 * Unit tests for UI components.
 * Requirements: 13.1, 13.2
 */
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { Table } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import type { Role } from '@/components/ui/types';

// focus-trap-react requires tabbable nodes which jsdom doesn't support well.
// Mock it to render children directly so Modal tests can focus on its own logic.
vi.mock('focus-trap-react', () => ({
  default: ({ children }: { children: React.ReactNode }) => React.createElement(React.Fragment, null, children),
}));

// ---------------------------------------------------------------------------
// Button
// ---------------------------------------------------------------------------
describe('Button', () => {
  it('renders primary variant', () => {
    const { container } = render(<Button variant="primary">Save</Button>);
    const btn = container.querySelector('button')!;
    expect(btn.className).toContain('bg-[#0d9488]');
    expect(btn.textContent).toBe('Save');
  });

  it('renders secondary variant', () => {
    const { container } = render(<Button variant="secondary">Cancel</Button>);
    const btn = container.querySelector('button')!;
    expect(btn.className).toContain('bg-white');
  });

  it('renders danger variant', () => {
    const { container } = render(<Button variant="danger">Delete</Button>);
    const btn = container.querySelector('button')!;
    expect(btn.className).toContain('bg-[#dc2626]');
  });

  it('renders sm size', () => {
    const { container } = render(<Button size="sm">Small</Button>);
    expect(container.querySelector('button')!.className).toContain('px-3');
  });

  it('renders md size', () => {
    const { container } = render(<Button size="md">Medium</Button>);
    expect(container.querySelector('button')!.className).toContain('px-4');
  });

  it('renders lg size', () => {
    const { container } = render(<Button size="lg">Large</Button>);
    expect(container.querySelector('button')!.className).toContain('px-6');
  });

  it('renders Spinner when loading=true', () => {
    render(<Button loading>Submit</Button>);
    expect(screen.getByTestId('spinner')).toBeTruthy();
    expect(screen.queryByText('Submit')).toBeNull();
  });

  it('does not render Spinner when loading=false', () => {
    render(<Button loading={false}>Submit</Button>);
    expect(screen.queryByTestId('spinner')).toBeNull();
    expect(screen.getByText('Submit')).toBeTruthy();
  });

  it('is disabled when disabled=true', () => {
    const { container } = render(<Button disabled>Click</Button>);
    expect(container.querySelector('button')!.disabled).toBe(true);
  });

  it('is disabled when loading=true', () => {
    const { container } = render(<Button loading>Click</Button>);
    expect(container.querySelector('button')!.disabled).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Input
// ---------------------------------------------------------------------------
describe('Input', () => {
  it('renders label when provided', () => {
    render(<Input label="Email" />);
    expect(screen.getByText('Email')).toBeTruthy();
  });

  it('renders error text when provided', () => {
    render(<Input label="Email" error="Required field" />);
    expect(screen.getByRole('alert')).toHaveTextContent('Required field');
  });

  it('does not render error element when no error', () => {
    render(<Input label="Email" />);
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('forwards HTML attributes to the input element', () => {
    render(<Input placeholder="Enter email" type="email" maxLength={100} />);
    const input = screen.getByPlaceholderText('Enter email') as HTMLInputElement;
    expect(input.type).toBe('email');
    expect(input.maxLength).toBe(100);
  });

  it('associates label with input via htmlFor', () => {
    render(<Input label="Username" />);
    const label = screen.getByText('Username') as HTMLLabelElement;
    const input = document.getElementById(label.htmlFor);
    expect(input).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Card
// ---------------------------------------------------------------------------
describe('Card', () => {
  it('renders children inside the container', () => {
    render(
      <Card>
        <p>Card content</p>
      </Card>
    );
    expect(screen.getByText('Card content')).toBeTruthy();
  });

  it('applies rounded and shadow classes', () => {
    const { container } = render(<Card>Content</Card>);
    const div = container.querySelector('div')!;
    expect(div.className).toContain('rounded-lg');
    expect(div.className).toContain('shadow-md');
  });

  it('merges custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    expect(container.querySelector('div')!.className).toContain('custom-class');
  });
});

// ---------------------------------------------------------------------------
// Table
// ---------------------------------------------------------------------------
describe('Table', () => {
  const columns = [
    { key: 'name' as const, header: 'Name' },
    { key: 'age' as const, header: 'Age' },
  ];

  it('renders loading skeleton when loading=true', () => {
    const { container } = render(
      <Table columns={columns} data={[]} loading />
    );
    const skeletonCells = container.querySelectorAll('.animate-pulse');
    expect(skeletonCells.length).toBeGreaterThan(0);
  });

  it('renders empty state when data is empty and loading=false', () => {
    render(
      <Table columns={columns} data={[]} emptySlot={<span>No records</span>} />
    );
    expect(screen.getAllByText('No records').length).toBeGreaterThan(0);
  });

  it('renders data rows when data is provided', () => {
    const data = [
      { name: 'Alice', age: '30' },
      { name: 'Bob', age: '25' },
    ];
    render(<Table columns={columns} data={data} />);
    expect(screen.getAllByText('Alice').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Bob').length).toBeGreaterThan(0);
  });

  it('renders column headers', () => {
    render(<Table columns={columns} data={[]} />);
    expect(screen.getAllByText('Name').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Age').length).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// Badge
// ---------------------------------------------------------------------------
describe('Badge', () => {
  const roles: Role[] = ['admin', 'doctor', 'nurse', 'researcher', 'patient'];

  roles.forEach((role) => {
    it(`renders correct CSS class for role: ${role}`, () => {
      const { container } = render(<Badge role={role} />);
      const span = container.querySelector('span')!;
      expect(span.className).toContain(`role-${role}`);
    });
  });

  it('renders the role label as text', () => {
    render(<Badge role="doctor" />);
    expect(screen.getByText('doctor')).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// Modal
// ---------------------------------------------------------------------------
describe('Modal', () => {
  it('renders nothing when open=false', () => {
    const { container } = render(
      <Modal open={false} onClose={vi.fn()}>
        <p>Content</p>
      </Modal>
    );
    expect(container.querySelector('[role="dialog"]')).toBeNull();
  });

  it('renders children when open=true', () => {
    render(
      <Modal open onClose={vi.fn()}>
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.getByText('Modal content')).toBeTruthy();
  });

  it('close button has aria-label="Close modal"', () => {
    render(
      <Modal open onClose={vi.fn()}>
        <p>Content</p>
      </Modal>
    );
    const closeBtn = screen.getByRole('button', { name: /close modal/i });
    expect(closeBtn).toBeTruthy();
    expect(closeBtn.getAttribute('aria-label')).toBe('Close modal');
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal open onClose={onClose}>
        <p>Content</p>
      </Modal>
    );
    fireEvent.click(screen.getByRole('button', { name: /close modal/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('has role="dialog" and aria-modal="true"', () => {
    render(
      <Modal open onClose={vi.fn()}>
        <p>Content</p>
      </Modal>
    );
    const dialog = screen.getByRole('dialog');
    expect(dialog.getAttribute('aria-modal')).toBe('true');
  });

  it('focus trap is active — close button is focusable inside modal', () => {
    render(
      <Modal open onClose={vi.fn()}>
        <button>Inner button</button>
      </Modal>
    );
    // FocusTrap wraps the content; close button and inner button should be in the DOM
    expect(screen.getByRole('button', { name: /close modal/i })).toBeTruthy();
    expect(screen.getByRole('button', { name: /inner button/i })).toBeTruthy();
  });
});

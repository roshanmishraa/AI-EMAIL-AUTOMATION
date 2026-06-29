import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEmails } from '../hooks/useEmails';
import { useTriggerFetch } from '../hooks/useEmails';
import { useEmailStore } from '../store/emailStore';
import Topbar from '../components/layout/Topbar';
import EmailList from '../components/inbox/EmailList';
import EmailFilters from '../components/inbox/EmailFilters';
import { RefreshCw } from 'lucide-react';
export default function InboxPage() {
    const { filter } = useEmailStore();
    const { data, isLoading, isError } = useEmails(filter);
    const triggerFetch = useTriggerFetch();
    const emails = data?.emails ?? [];
    return (_jsxs("div", { className: "flex flex-col h-full", children: [_jsx(Topbar, { title: "Inbox", subtitle: `${data?.total ?? 0} emails`, actions: _jsxs("button", { onClick: () => triggerFetch.mutate(), disabled: triggerFetch.isPending, className: "flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 bg-white px-3 py-1.5 rounded-lg disabled:opacity-60 transition-colors", children: [_jsx(RefreshCw, { size: 14, className: triggerFetch.isPending ? 'animate-spin' : '' }), triggerFetch.isPending ? 'Fetching…' : 'Fetch Gmail'] }) }), _jsx("div", { className: "px-6 py-3 border-b bg-white", children: _jsx(EmailFilters, {}) }), isError && (_jsx("div", { className: "mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700", children: "Failed to load emails \u2014 check that the backend is running on port 8000." })), _jsx("div", { className: "flex-1 overflow-auto bg-white", children: _jsx(EmailList, { emails: emails, loading: isLoading }) })] }));
}

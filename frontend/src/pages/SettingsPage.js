import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// ============================================================
// FILE:  frontend/src/pages/SettingsPage.tsx
// CHANGE: Agent Email field + Email Ping toggle add kiya
//         in Notification Preferences section
//         (poora file replace karo — sirf additions marked with NEW)
// ============================================================
import { useState, useEffect } from 'react';
import { useSettings, useUpdateSettings } from '../hooks/useSettings';
import Topbar from '../components/layout/Topbar';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Save } from 'lucide-react';
const ALL_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
export default function SettingsPage() {
    const { data: settings, isLoading, isError } = useSettings();
    const updateMutation = useUpdateSettings();
    // ── Existing state (UNCHANGED) ────────────────────────────
    const [autoSend, setAutoSend] = useState(false);
    const [threshold, setThreshold] = useState(70);
    const [pollInterval, setPollInterval] = useState(60);
    const [slaResponse, setSlaResponse] = useState(60);
    const [slaEscalation, setSlaEscalation] = useState(30);
    const [workStart, setWorkStart] = useState('09:00');
    const [workEnd, setWorkEnd] = useState('18:00');
    const [workDays, setWorkDays] = useState(['Mon', 'Tue', 'Wed', 'Thu', 'Fri']);
    const [notifyEscalation, setNotifyEscalation] = useState(true);
    const [notifyLegal, setNotifyLegal] = useState(true);
    // ── NEW: Email ping state ─────────────────────────────────
    const [agentEmail, setAgentEmail] = useState('');
    const [emailNotifyEscalation, setEmailNotifyEscalation] = useState(true);
    const [saved, setSaved] = useState(false);
    useEffect(() => {
        if (settings) {
            setAutoSend(settings.auto_send_mode ?? false);
            setThreshold(settings.escalation_confidence_threshold ?? 70);
            setPollInterval(settings.polling_interval_seconds ?? 60);
            setSlaResponse(settings.sla_response_time_minutes ?? 60);
            setSlaEscalation(settings.sla_escalation_time_minutes ?? 30);
            setWorkStart(settings.working_hours_start ?? '09:00');
            setWorkEnd(settings.working_hours_end ?? '18:00');
            setWorkDays(settings.working_days
                ? settings.working_days.split(',')
                : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']);
            setNotifyEscalation(settings.slack_notify_on_escalation ?? true);
            setNotifyLegal(settings.slack_notify_on_legal ?? true);
            // ── NEW ──
            setAgentEmail(settings.agent_email ?? '');
            setEmailNotifyEscalation(settings.email_notify_on_escalation ?? true);
        }
    }, [settings]);
    const toggleDay = (day) => {
        setWorkDays(prev => prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]);
    };
    const handleSave = async () => {
        await updateMutation.mutateAsync({
            auto_send_mode: autoSend,
            escalation_confidence_threshold: threshold,
            polling_interval_seconds: pollInterval,
            sla_response_time_minutes: slaResponse,
            sla_escalation_time_minutes: slaEscalation,
            working_hours_start: workStart,
            working_hours_end: workEnd,
            working_days: workDays.join(','),
            slack_notify_on_escalation: notifyEscalation,
            slack_notify_on_legal: notifyLegal,
            // ── NEW ──
            agent_email: agentEmail,
            email_notify_on_escalation: emailNotifyEscalation,
        });
        setSaved(true);
        setTimeout(() => setSaved(false), 2500);
    };
    return (_jsxs("div", { className: "flex flex-col h-full", children: [_jsx(Topbar, { title: "Settings", subtitle: "Configure pipeline behaviour" }), _jsxs("div", { className: "flex-1 overflow-auto p-6 max-w-xl", children: [isLoading && (_jsx("div", { className: "flex items-center justify-center h-48", children: _jsx(LoadingSpinner, { size: "lg" }) })), isError && (_jsx("div", { className: "px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 mb-4", children: "Failed to load settings \u2014 check backend connection." })), !isLoading && !isError && (_jsxs("div", { className: "space-y-5", children: [_jsx("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-semibold text-gray-800", children: "Auto-Send Mode" }), _jsx("p", { className: "text-xs text-gray-500 mt-0.5", children: "When enabled, AI replies are sent automatically without human approval." })] }), _jsx("button", { onClick: () => setAutoSend(v => !v), className: `relative w-10 h-5 rounded-full transition-colors focus:outline-none ${autoSend ? 'bg-blue-600' : 'bg-gray-200'}`, children: _jsx("span", { className: `absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${autoSend ? 'translate-x-5' : 'translate-x-0'}` }) })] }) }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("p", { className: "text-sm font-semibold text-gray-800 mb-1", children: "Escalation Confidence Threshold" }), _jsx("p", { className: "text-xs text-gray-500 mb-4", children: "Emails where AI confidence falls below this % are escalated for human review." }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("input", { type: "range", min: 30, max: 95, step: 5, value: threshold, onChange: e => setThreshold(Number(e.target.value)), className: "flex-1 accent-blue-600" }), _jsxs("span", { className: "text-sm font-semibold text-blue-600 w-10 text-right", children: [threshold, "%"] })] })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("p", { className: "text-sm font-semibold text-gray-800 mb-1", children: "Gmail Polling Interval" }), _jsx("p", { className: "text-xs text-gray-500 mb-4", children: "How often the system checks Gmail for new emails (in seconds)." }), _jsx("div", { className: "flex items-center gap-3", children: [30, 60, 120, 300].map(secs => (_jsxs("button", { onClick: () => setPollInterval(secs), className: `px-3 py-1.5 rounded-lg text-sm border transition-colors ${pollInterval === secs
                                                ? 'bg-blue-600 text-white border-blue-600'
                                                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'}`, children: [secs, "s"] }, secs))) })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("p", { className: "text-sm font-semibold text-gray-800 mb-1", children: "SLA Targets" }), _jsx("p", { className: "text-xs text-gray-500 mb-4", children: "Target response times for automated replies and escalation acknowledgements." }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-1", children: [_jsx("label", { className: "text-xs text-gray-600", children: "AI Reply SLA" }), _jsxs("span", { className: "text-xs font-semibold text-blue-600", children: [slaResponse, " min"] })] }), _jsx("input", { type: "range", min: 5, max: 240, step: 5, value: slaResponse, onChange: e => setSlaResponse(Number(e.target.value)), className: "w-full accent-blue-600" })] }), _jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-1", children: [_jsx("label", { className: "text-xs text-gray-600", children: "Escalation Acknowledge SLA" }), _jsxs("span", { className: "text-xs font-semibold text-orange-500", children: [slaEscalation, " min"] })] }), _jsx("input", { type: "range", min: 5, max: 120, step: 5, value: slaEscalation, onChange: e => setSlaEscalation(Number(e.target.value)), className: "w-full accent-orange-500" })] })] })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("p", { className: "text-sm font-semibold text-gray-800 mb-1", children: "Working Hours" }), _jsx("p", { className: "text-xs text-gray-500 mb-4", children: "Define active support hours. Emails outside these hours are queued." }), _jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsxs("div", { className: "flex-1", children: [_jsx("label", { className: "text-xs text-gray-500 mb-1 block", children: "Start" }), _jsx("input", { type: "time", value: workStart, onChange: e => setWorkStart(e.target.value), className: "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsx("span", { className: "text-gray-400 text-sm mt-4", children: "to" }), _jsxs("div", { className: "flex-1", children: [_jsx("label", { className: "text-xs text-gray-500 mb-1 block", children: "End" }), _jsx("input", { type: "time", value: workEnd, onChange: e => setWorkEnd(e.target.value), className: "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "text-xs text-gray-500 mb-2 block", children: "Active Days" }), _jsx("div", { className: "flex gap-2 flex-wrap", children: ALL_DAYS.map(day => (_jsx("button", { onClick: () => toggleDay(day), className: `px-3 py-1 rounded-lg text-xs font-medium border transition-colors ${workDays.includes(day)
                                                        ? 'bg-blue-600 text-white border-blue-600'
                                                        : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'}`, children: day }, day))) })] })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("p", { className: "text-sm font-semibold text-gray-800 mb-1", children: "Slack Notifications" }), _jsx("p", { className: "text-xs text-gray-500 mb-4", children: "Choose which events trigger a Slack webhook alert." }), _jsx("div", { className: "space-y-3", children: [
                                            {
                                                label: 'Notify on Escalation',
                                                sublabel: 'Ping Slack whenever any email is escalated for human review.',
                                                value: notifyEscalation,
                                                toggle: () => setNotifyEscalation(v => !v),
                                            },
                                            {
                                                label: 'Notify on Legal',
                                                sublabel: 'Ping Slack immediately when a legal-category email is detected.',
                                                value: notifyLegal,
                                                toggle: () => setNotifyLegal(v => !v),
                                            },
                                        ].map(item => (_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-xs font-medium text-gray-700", children: item.label }), _jsx("p", { className: "text-[11px] text-gray-400", children: item.sublabel })] }), _jsx("button", { onClick: item.toggle, className: `relative w-10 h-5 rounded-full transition-colors focus:outline-none ${item.value ? 'bg-blue-600' : 'bg-gray-200'}`, children: _jsx("span", { className: `absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${item.value ? 'translate-x-5' : 'translate-x-0'}` }) })] }, item.label))) })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("p", { className: "text-sm font-semibold text-gray-800 mb-1", children: "Email Ping on Escalation" }), _jsx("p", { className: "text-xs text-gray-500 mb-4", children: "Send an email notification to your support agent when an email is escalated." }), _jsxs("div", { className: "mb-4", children: [_jsx("label", { className: "text-xs text-gray-600 mb-1.5 block font-medium", children: "Agent Email Address" }), _jsx("input", { type: "email", placeholder: "agent@yourcompany.com", value: agentEmail, onChange: e => setAgentEmail(e.target.value), className: "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700\r\n                             focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-gray-300" }), _jsx("p", { className: "text-[11px] text-gray-400 mt-1", children: "Configure SMTP in your .env file (SMTP_HOST, SMTP_USER, SMTP_PASS)" })] }), _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-xs font-medium text-gray-700", children: "Email on Escalation" }), _jsx("p", { className: "text-[11px] text-gray-400", children: "Email agent whenever any email requires human review." })] }), _jsx("button", { onClick: () => setEmailNotifyEscalation(v => !v), className: `relative w-10 h-5 rounded-full transition-colors focus:outline-none ${emailNotifyEscalation ? 'bg-blue-600' : 'bg-gray-200'}`, children: _jsx("span", { className: `absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${emailNotifyEscalation ? 'translate-x-5' : 'translate-x-0'}` }) })] })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("button", { onClick: handleSave, disabled: updateMutation.isPending, className: "flex items-center gap-2 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-2 rounded-lg transition-colors font-medium", children: updateMutation.isPending ? (_jsxs(_Fragment, { children: [_jsx(LoadingSpinner, { size: "sm" }), " Saving\u2026"] })) : (_jsxs(_Fragment, { children: [_jsx(Save, { size: 14 }), " Save Settings"] })) }), saved && (_jsx("span", { className: "text-sm text-green-600 font-medium", children: "\u2713 Saved" })), updateMutation.isError && (_jsx("span", { className: "text-sm text-red-600", children: "Save failed \u2014 try again." }))] })] }))] })] }));
}

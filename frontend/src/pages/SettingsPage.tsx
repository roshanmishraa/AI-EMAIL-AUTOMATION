import { useState, useEffect } from 'react'
import { useSettings, useUpdateSettings } from '../hooks/useSettings'
import Topbar from '../components/layout/Topbar'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { Save } from 'lucide-react'

// ── Working days options ──
const ALL_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export default function SettingsPage() {
  const { data: settings, isLoading, isError } = useSettings()
  const updateMutation = useUpdateSettings()

  // ── Existing state (unchanged) ──
  const [autoSend,      setAutoSend]      = useState(false)
  const [threshold,     setThreshold]     = useState(70)
  const [pollInterval,  setPollInterval]  = useState(60)

  // ── NEW: SLA state ──
  const [slaResponse,   setSlaResponse]   = useState(60)
  const [slaEscalation, setSlaEscalation] = useState(30)

  // ── NEW: Working hours state ──
  const [workStart,     setWorkStart]     = useState('09:00')
  const [workEnd,       setWorkEnd]       = useState('18:00')
  const [workDays,      setWorkDays]      = useState<string[]>(['Mon','Tue','Wed','Thu','Fri'])

  // ── NEW: Notification state ──
  const [notifyEscalation, setNotifyEscalation] = useState(true)
  const [notifyLegal,      setNotifyLegal]      = useState(true)

  const [saved, setSaved] = useState(false)

  // Sync form state when settings load from backend
  useEffect(() => {
    if (settings) {
      // ── Existing ──
      setAutoSend(settings.auto_send_mode ?? false)
      setThreshold(settings.escalation_confidence_threshold ?? 70)
      setPollInterval(settings.polling_interval_seconds ?? 60)

      // ── NEW ──
      setSlaResponse(settings.sla_response_time_minutes ?? 60)
      setSlaEscalation(settings.sla_escalation_time_minutes ?? 30)
      setWorkStart(settings.working_hours_start ?? '09:00')
      setWorkEnd(settings.working_hours_end ?? '18:00')
      setWorkDays(
        settings.working_days
          ? settings.working_days.split(',')
          : ['Mon','Tue','Wed','Thu','Fri']
      )
      setNotifyEscalation(settings.slack_notify_on_escalation ?? true)
      setNotifyLegal(settings.slack_notify_on_legal ?? true)
    }
  }, [settings])

  // Toggle a working day on/off
  const toggleDay = (day: string) => {
    setWorkDays(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    )
  }

  const handleSave = async () => {
    await updateMutation.mutateAsync({
      // ── Existing ──
      auto_send_mode:                  autoSend,
      escalation_confidence_threshold: threshold,
      polling_interval_seconds:        pollInterval,

      // ── NEW ──
      sla_response_time_minutes:       slaResponse,
      sla_escalation_time_minutes:     slaEscalation,
      working_hours_start:             workStart,
      working_hours_end:               workEnd,
      working_days:                    workDays.join(','),
      slack_notify_on_escalation:      notifyEscalation,
      slack_notify_on_legal:           notifyLegal,
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Settings" subtitle="Configure pipeline behaviour" />

      <div className="flex-1 overflow-auto p-6 max-w-xl">
        {isLoading && (
          <div className="flex items-center justify-center h-48">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {isError && (
          <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 mb-4">
            Failed to load settings — check backend connection.
          </div>
        )}

        {!isLoading && (
          <div className="space-y-6">

            {/* ── Auto-send mode (unchanged) ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-800">Auto-Send Mode</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    When enabled, AI replies are sent automatically without agent approval.
                    <span className="text-red-500 font-medium"> Use with caution.</span>
                  </p>
                </div>
                <button
                  onClick={() => setAutoSend(v => !v)}
                  className={`relative w-11 h-6 rounded-full transition-colors focus:outline-none ${
                    autoSend ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                      autoSend ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* ── Escalation confidence threshold (unchanged) ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <p className="text-sm font-semibold text-gray-800 mb-1">
                Escalation Confidence Threshold
              </p>
              <p className="text-xs text-gray-500 mb-4">
                Emails where AI confidence falls below this value are automatically escalated for human review.
              </p>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min={10}
                  max={100}
                  step={5}
                  value={threshold}
                  onChange={e => setThreshold(Number(e.target.value))}
                  className="flex-1 accent-blue-600"
                />
                <span
                  className={`text-sm font-bold w-12 text-right ${
                    threshold >= 80 ? 'text-green-600'
                    : threshold >= 60 ? 'text-yellow-600'
                    : 'text-red-600'
                  }`}
                >
                  {threshold}%
                </span>
              </div>
            </div>

            {/* ── Gmail polling interval (unchanged) ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <p className="text-sm font-semibold text-gray-800 mb-1">
                Gmail Polling Interval
              </p>
              <p className="text-xs text-gray-500 mb-4">
                How often the system checks Gmail for new emails (in seconds).
              </p>
              <div className="flex items-center gap-3">
                {[30, 60, 120, 300].map(secs => (
                  <button
                    key={secs}
                    onClick={() => setPollInterval(secs)}
                    className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                      pollInterval === secs
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    {secs}s
                  </button>
                ))}
              </div>
            </div>

            {/* ── NEW: SLA Targets ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <p className="text-sm font-semibold text-gray-800 mb-1">SLA Targets</p>
              <p className="text-xs text-gray-500 mb-4">
                Target response times for automated replies and escalation acknowledgements.
              </p>

              <div className="space-y-4">
                {/* AI Response SLA */}
                <div>
                  <div className="flex justify-between mb-1">
                    <label className="text-xs text-gray-600">AI Reply SLA</label>
                    <span className="text-xs font-semibold text-blue-600">{slaResponse} min</span>
                  </div>
                  <input
                    type="range"
                    min={5}
                    max={240}
                    step={5}
                    value={slaResponse}
                    onChange={e => setSlaResponse(Number(e.target.value))}
                    className="w-full accent-blue-600"
                  />
                  <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
                    <span>5 min</span><span>4 hrs</span>
                  </div>
                </div>

                {/* Escalation SLA */}
                <div>
                  <div className="flex justify-between mb-1">
                    <label className="text-xs text-gray-600">Escalation Acknowledge SLA</label>
                    <span className="text-xs font-semibold text-orange-500">{slaEscalation} min</span>
                  </div>
                  <input
                    type="range"
                    min={5}
                    max={120}
                    step={5}
                    value={slaEscalation}
                    onChange={e => setSlaEscalation(Number(e.target.value))}
                    className="w-full accent-orange-500"
                  />
                  <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
                    <span>5 min</span><span>2 hrs</span>
                  </div>
                </div>
              </div>
            </div>

            {/* ── NEW: Working Hours ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <p className="text-sm font-semibold text-gray-800 mb-1">Working Hours</p>
              <p className="text-xs text-gray-500 mb-4">
                Define active support hours. Emails outside these hours are queued for next business day.
              </p>

              {/* Time pickers */}
              <div className="flex items-center gap-3 mb-4">
                <div className="flex-1">
                  <label className="text-xs text-gray-500 mb-1 block">Start</label>
                  <input
                    type="time"
                    value={workStart}
                    onChange={e => setWorkStart(e.target.value)}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <span className="text-gray-400 text-sm mt-4">to</span>
                <div className="flex-1">
                  <label className="text-xs text-gray-500 mb-1 block">End</label>
                  <input
                    type="time"
                    value={workEnd}
                    onChange={e => setWorkEnd(e.target.value)}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Day toggles */}
              <div>
                <label className="text-xs text-gray-500 mb-2 block">Active Days</label>
                <div className="flex gap-2 flex-wrap">
                  {ALL_DAYS.map(day => (
                    <button
                      key={day}
                      onClick={() => toggleDay(day)}
                      className={`px-3 py-1 rounded-lg text-xs font-medium border transition-colors ${
                        workDays.includes(day)
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      {day}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* ── NEW: Notification Preferences ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <p className="text-sm font-semibold text-gray-800 mb-1">
                Slack Notifications
              </p>
              <p className="text-xs text-gray-500 mb-4">
                Choose which events trigger a Slack webhook alert.
              </p>

              <div className="space-y-3">
                {[
                  {
                    label:    'Notify on Escalation',
                    sublabel: 'Ping Slack whenever any email is escalated for human review.',
                    value:    notifyEscalation,
                    toggle:   () => setNotifyEscalation(v => !v),
                  },
                  {
                    label:    'Notify on Legal',
                    sublabel: 'Ping Slack immediately when a legal-category email is detected.',
                    value:    notifyLegal,
                    toggle:   () => setNotifyLegal(v => !v),
                  },
                ].map(item => (
                  <div key={item.label} className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium text-gray-700">{item.label}</p>
                      <p className="text-[11px] text-gray-400">{item.sublabel}</p>
                    </div>
                    <button
                      onClick={item.toggle}
                      className={`relative w-10 h-5 rounded-full transition-colors focus:outline-none ${
                        item.value ? 'bg-blue-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                          item.value ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* ── Save button (unchanged) ── */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleSave}
                disabled={updateMutation.isPending}
                className="flex items-center gap-2 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-2 rounded-lg transition-colors font-medium"
              >
                {updateMutation.isPending ? (
                  <><LoadingSpinner size="sm" /> Saving…</>
                ) : (
                  <><Save size={14} /> Save Settings</>
                )}
              </button>

              {saved && (
                <span className="text-sm text-green-600 font-medium">✓ Saved</span>
              )}

              {updateMutation.isError && (
                <span className="text-sm text-red-600">Save failed — try again.</span>
              )}
            </div>

          </div>
        )}
      </div>
    </div>
  )
}

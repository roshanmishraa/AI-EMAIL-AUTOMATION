import { useState, useEffect } from 'react'
import { useSettings, useUpdateSettings } from '../hooks/useSettings'
import Topbar from '../components/layout/Topbar'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { Save } from 'lucide-react'

export default function SettingsPage() {
  const { data: settings, isLoading, isError } = useSettings()
  const updateMutation = useUpdateSettings()

  const [autoSend, setAutoSend] = useState(false)
  const [threshold, setThreshold] = useState(70)
  const [pollInterval, setPollInterval] = useState(60)
  const [saved, setSaved] = useState(false)

  // Sync form state when settings load from backend
  useEffect(() => {
    if (settings) {
      setAutoSend(settings.auto_send_mode ?? false)
      setThreshold(settings.escalation_confidence_threshold ?? 70)
      setPollInterval(settings.polling_interval_seconds ?? 60)
    }
  }, [settings])

  const handleSave = async () => {
    await updateMutation.mutateAsync({
      auto_send_mode: autoSend,
      escalation_confidence_threshold: threshold,
      polling_interval_seconds: pollInterval,
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

            {/* Auto-send mode */}
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

            {/* Escalation confidence threshold */}
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
                    threshold >= 80
                      ? 'text-green-600'
                      : threshold >= 60
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }`}
                >
                  {threshold}%
                </span>
              </div>
            </div>

            {/* Gmail polling interval */}
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

            {/* Save button */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleSave}
                disabled={updateMutation.isPending}
                className="flex items-center gap-2 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-2 rounded-lg transition-colors font-medium"
              >
                {updateMutation.isPending ? (
                  <>
                    <LoadingSpinner size="sm" /> Saving…
                  </>
                ) : (
                  <>
                    <Save size={14} /> Save Settings
                  </>
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

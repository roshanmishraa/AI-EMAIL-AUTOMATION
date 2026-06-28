import client from './axiosClient'

export const getSettings = () => client.get('/settings/')

export const updateSettings = (payload: {
  // ── Existing fields (unchanged) ──
  auto_send_mode?:                  boolean
  escalation_confidence_threshold?: number
  polling_interval_seconds?:        number

  // ── SLA targets ──
  sla_response_time_minutes?:       number
  sla_escalation_time_minutes?:     number

  // ── Working hours ──
  working_hours_start?:             string   // "09:00"
  working_hours_end?:               string   // "18:00"
  working_days?:                    string   // "Mon,Tue,Wed,Thu,Fri"

  // ── Notification preferences ──
  slack_notify_on_escalation?:      boolean
  slack_notify_on_legal?:           boolean

  // ── NEW: Email ping ──
  agent_email?:                     string   // "agent@company.com"
  email_notify_on_escalation?:      boolean
}) => client.post('/settings/', payload)
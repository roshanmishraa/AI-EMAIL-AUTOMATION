import { RefreshCw } from 'lucide-react'
import Topbar from '../components/layout/Topbar'
import EmailList from '../components/inbox/EmailList'
import EmailFilters from '../components/inbox/EmailFilters'
import { useEmails, useTriggerFetch } from '../hooks/useEmails'
import { useEmailStore } from '../store/emailStore'

export default function InboxPage() {
  const { filter }              = useEmailStore()
  const { data, isLoading }     = useEmails(filter)
  const triggerFetch            = useTriggerFetch()

  const emails = data?.emails ?? []
  const total  = data?.total  ?? 0

  return (
    <div className="flex flex-col h-full">
      <Topbar
        title="Inbox"
        subtitle={isLoading ? 'Loading…' : `${total} email${total !== 1 ? 's' : ''}`}
        actions={
          <button
            onClick={() => triggerFetch.mutate()}
            disabled={triggerFetch.isPending}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw size={14} className={triggerFetch.isPending ? 'animate-spin' : ''} />
            {triggerFetch.isPending ? 'Fetching…' : 'Fetch Gmail'}
          </button>
        }
      />

      <div className="px-6 py-3 border-b bg-white">
        <EmailFilters />
      </div>

      <div className="flex-1 overflow-auto">
        <EmailList emails={emails} loading={isLoading} />
      </div>
    </div>
  )
}
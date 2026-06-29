/**
 * Returns the latest AI-generated (not human) draft reply for an email,
 * or null if none exist. Used by AIReplyPanel.
 */
export function getLatestAIDraft(email) {
    if (!email.replies || email.replies.length === 0)
        return null;
    // Filter to AI-generated drafts, newest first (highest id)
    const aiReplies = email.replies
        .filter(r => r.generated_by === 'ai')
        .sort((a, b) => b.id - a.id);
    return aiReplies[0] ?? null;
}
/**
 * NEW: Returns the latest (open or in_progress) escalation for an email,
 * or null if none/all resolved. Used by AIReplyPanel to show the reason
 * and the Resolve button.
 */
export function getLatestEscalation(email) {
    if (!email.escalations || email.escalations.length === 0)
        return null;
    const sorted = [...email.escalations].sort((a, b) => b.id - a.id);
    return sorted[0] ?? null;
}

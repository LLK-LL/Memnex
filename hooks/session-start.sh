#!/usr/bin/env bash
# ===========================================
# Session Start Hook — Portable version
#
# 1. Prints memory recall hint for current project
# 2. Checks for pending recovery files
# 3. Loads SOUL rules summary
# 4. Shows project knowledge count
# 5. Cleans old error-fix state
#
# Hook: SessionStart (matcher: "")
# ===========================================

source "$(dirname "$0")/lib/common.sh"

CWD=$(hook_get 'cwd')
[ -z "$CWD" ] && CWD="$PWD"
PROJECT=$(hook_project_name)
BRANCH=$(hook_git_branch)
MODEL=$(hook_model_short)
CTX=$(hook_context)
SOURCE=$(hook_get 'source')

# Human-readable source
case "$SOURCE" in
    startup) SOURCE_TEXT="New session" ;;
    resume)  SOURCE_TEXT="Resumed" ;;
    clear)   SOURCE_TEXT="After /clear" ;;
    compact) SOURCE_TEXT="After /compact" ;;
    *)       SOURCE_TEXT="Started" ;;
esac

# Notification
NOTIFY_MSG="$CTX | $SOURCE_TEXT | $MODEL"
hook_notify "$NOTIFY_MSG" "Claude Memory | Session" "Glass"
hook_log "SESSION_START: $NOTIFY_MSG"

echo "Session: $NOTIFY_MSG"
echo ""

# ======= MEMORY HINT =======
HINT="MEMORY_HINT: Project: ${PROJECT}"
[ -n "$BRANCH" ] && HINT="${HINT}, Branch: ${BRANCH}"
HINT="${HINT}. Use memory_recall(query=\"your task\", project=\"${PROJECT}\") to search past knowledge."
HINT="${HINT} Also run rule_context_refresh(project=\"${PROJECT}\", detail=\"compact\", phase=\"build\", event=\"task_start\", latest_user_instruction=\"your task\") to load query-ranked behavioral rules."
echo "$HINT"
echo ""

# ======= RECOVERY CHECK =======
mkdir -p "$HOOK_RECOVERY_DIR"
PENDING_FILES=$(ls -t "$HOOK_RECOVERY_DIR"/pending-*.md 2>/dev/null | head -3)

if [ -n "$PENDING_FILES" ]; then
    RECOVERY_COUNT=$(echo "$PENDING_FILES" | wc -l | tr -d ' ')
    echo "RECOVERY_ALERT: Found $RECOVERY_COUNT pending recovery file(s) from previous session(s)!"
    echo ""

    # Show the most recent recovery file
    LATEST_RECOVERY=$(echo "$PENDING_FILES" | head -1)
    echo "--- LATEST RECOVERY ($LATEST_RECOVERY) ---"
    cat "$LATEST_RECOVERY"
    echo "--- END RECOVERY ---"
    echo ""
    echo "ACTION_REQUIRED: Review the recovery context above and:"
    echo "  1. Save any important knowledge to MCP memory (memory_save)"
    echo "  2. Delete recovery files after processing: rm $HOOK_RECOVERY_DIR/pending-*.md"
    echo ""

    hook_notify "Recovery files found! Check session start output." "Claude Memory | Recovery" "Sosumi"
fi

# ======= SOUL RULES CHECK =======
MEMORY_DB="$CLAUDE_MEMORY_DIR/memory.db"

if [ -f "$MEMORY_DB" ]; then
    # Check active SOUL rules
    RULES_INFO=$("$HOOK_PYTHON" -c "
import sqlite3, os
db_path = '$MEMORY_DB'
try:
    db = sqlite3.connect(db_path)
    # Check if rules table exists
    tables = [r[0] for r in db.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]

    if 'rules' in tables:
        active = db.execute(\"SELECT COUNT(*) FROM rules WHERE status='active'\").fetchone()[0]
        if active > 0:
            print(f'SOUL_RULES: {active} active behavioral rule(s) loaded.')
            rows = db.execute(
                \"SELECT priority, substr(content, 1, 80) FROM rules WHERE status='active' ORDER BY priority DESC LIMIT 5\"
            ).fetchall()
            for p, c in rows:
                print(f'  - [P{p}] {c}')
            print(f'  -> Call rule_context_refresh(project=\"$PROJECT\", detail=\"compact\", phase=\"build\", event=\"task_start\", latest_user_instruction=\"<task>\") at session start')

    # Check error patterns
    if 'errors' in tables:
        patterns = db.execute('''
            SELECT category, COUNT(*) AS cnt FROM errors
            WHERE status != 'insight_extracted' AND created_at > datetime('now', '-30 days')
            GROUP BY category HAVING cnt >= 3
        ''').fetchall()
        if patterns:
            print(f'PATTERN_ALERT: {len(patterns)} error pattern(s) detected (3+ in 30 days).')
            for cat, cnt in patterns[:5]:
                print(f'  - {cat} ({cnt}x)')
            print('  -> Call self_patterns(view=\"full_report\") to analyze')

    # Project knowledge summary
    if 'knowledge' in tables and '$PROJECT' and '$PROJECT' != os.path.basename(os.path.expanduser('~')):
        kcount = db.execute(
            \"SELECT COUNT(*) FROM knowledge WHERE project=? AND status='active'\", ('$PROJECT',)
        ).fetchone()[0]
        scount = db.execute(
            \"SELECT COUNT(*) FROM knowledge WHERE project=? AND status='active' AND type='solution'\", ('$PROJECT',)
        ).fetchone()[0]
        if kcount > 0:
            print(f'PROJECT_MEMORY: \"{PROJECT}\" has {kcount} knowledge records ({scount} solutions)')
            print(f'  -> memory_recall(query=\"<task>\", project=\"$PROJECT\") before starting work')
        else:
            print(f'PROJECT_MEMORY: No prior knowledge for \"{PROJECT}\". Start fresh.')

    db.close()
except Exception as e:
    pass
" 2>/dev/null)

    if [ -n "$RULES_INFO" ]; then
        echo ""
        echo "$RULES_INFO"
    fi
fi

# ======= CLEAN UP OLD STATE =======
if [ -d "$HOOK_STATE_DIR" ]; then
    # Remove error states older than 1 hour
    find "$HOOK_STATE_DIR" -name "last-error-*" -mmin +60 -delete 2>/dev/null
fi

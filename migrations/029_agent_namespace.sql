-- 029_agent_namespace.sql
-- Adds first-class agent namespace ownership for multi-agent memory isolation.
--
-- The current Store bootstrap already adds agent_namespace idempotently before
-- numbered migrations run. Keep this migration focused on the indexes so a
-- fresh install can complete cleanly and record migration 029 as applied.

CREATE INDEX IF NOT EXISTS idx_k_agent_namespace
    ON knowledge(agent_namespace);

CREATE INDEX IF NOT EXISTS idx_k_project_agent_namespace
    ON knowledge(project, agent_namespace);

CREATE INDEX IF NOT EXISTS idx_k_type_agent_namespace
    ON knowledge(type, agent_namespace);

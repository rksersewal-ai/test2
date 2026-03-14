-- =============================================================================
-- FILE: sql/011_saved_views.sql
-- SPRINT 2 | FEATURE #7: Customisable Saved Views / Dashboard Widgets
-- PURPOSE : Per-user saved filter presets pinnable to the sidebar.
--           filter_json stores the exact query-string parameters for the
--           EDMS or WorkLedger list page so the frontend can replay them.
--           widget_config_json stores optional dashboard card settings.
-- DEPENDS : core_user
-- MIGRATION: Run after 010_search_indexes.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_saved_view (
    id                  BIGSERIAL    PRIMARY KEY,
    user_id             BIGINT       NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    view_name           VARCHAR(120) NOT NULL,
    module              VARCHAR(20)  NOT NULL DEFAULT 'EDMS'
                            CHECK (module IN ('EDMS', 'WORKLEDGER', 'DASHBOARD')),
    filter_json         JSONB        NOT NULL DEFAULT '{}',
    -- Example filter_json for EDMS:
    -- {"status": "ACTIVE", "category": 3, "section": 7, "q": "WAG9"}
    -- Example filter_json for WORKLEDGER:
    -- {"status": "OPEN", "work_type": 2, "section": 4}
    widget_config_json  JSONB        NOT NULL DEFAULT '{}',
    -- Example widget_config_json for DASHBOARD widget:
    -- {"chart_type": "bar", "metric": "documents_by_section", "limit": 10}
    is_pinned           BOOLEAN      NOT NULL DEFAULT FALSE,
    sort_order          INT          NOT NULL DEFAULT 0,
    icon                VARCHAR(40)  NULL,     -- optional icon key for sidebar (e.g. 'filter', 'star')
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, view_name, module)
);

COMMENT ON TABLE  user_saved_view IS 'Per-user saved filter presets and dashboard widgets. Pinned views appear in sidebar.';
COMMENT ON COLUMN user_saved_view.filter_json IS 'Serialised query-string params to replay the saved list view filter.';
COMMENT ON COLUMN user_saved_view.widget_config_json IS 'Optional dashboard widget configuration (chart type, metric, limit).';

CREATE INDEX IF NOT EXISTS idx_usv_user       ON user_saved_view(user_id);
CREATE INDEX IF NOT EXISTS idx_usv_module     ON user_saved_view(user_id, module);
CREATE INDEX IF NOT EXISTS idx_usv_pinned     ON user_saved_view(user_id, is_pinned) WHERE is_pinned = TRUE;
CREATE INDEX IF NOT EXISTS idx_usv_filter_gin ON user_saved_view USING GIN (filter_json);

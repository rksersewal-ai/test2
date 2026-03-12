-- Migration 002: Core schema - Section and User tables
-- Applied after Django migrations for reference/documentation

-- Sections
CREATE INDEX IF NOT EXISTS idx_core_section_code ON core_section(code);
CREATE INDEX IF NOT EXISTS idx_core_section_parent ON core_section(parent_id) WHERE parent_id IS NOT NULL;

-- Users
CREATE INDEX IF NOT EXISTS idx_core_user_role ON core_user(role);
CREATE INDEX IF NOT EXISTS idx_core_user_section ON core_user(section_id) WHERE section_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_core_user_employee_code ON core_user(employee_code) WHERE employee_code IS NOT NULL;

-- Comment
COMMENT ON TABLE core_user IS 'PLW EDMS users with RBAC roles';
COMMENT ON TABLE core_section IS 'PLW organizational sections';

# apps/rbac — Intentional Stub

This app directory is reserved for future fine-grained object-level permissions
(e.g. per-document ACLs, section-scoped access).

**The canonical RBAC enforcement for this project is in:**

```
apps/core/permissions.py
```

Do NOT add permission classes here. Import from `apps.core.permissions` instead.

## Why Does This Exist?

`apps.rbac` appears in `INSTALLED_APPS` so that future migrations for fine-grained
object-level permissions can be added here without renaming the app. For now it
contains no models or views.

## When to Implement

If a requirement emerges where different engineers in the same section need different
document-level read/write access (beyond role-level), implement `ObjectPermission`
model here and wire into `has_object_permission()` hooks in the view layer.

# BOM App Setup

## 1. Add to INSTALLED_APPS in `backend/edms/settings.py`
```python
'bom.apps.BomConfig',
```

## 2. Add URL in `backend/edms/urls.py`
```python
path('api/v1/bom/', include('bom.urls')),
```

## 3. Run migration
```bash
cd backend
python manage.py migrate bom
```

## 4. Install frontend dependency
```bash
cd frontend
npm install @xyflow/react
```
Also add to `frontend/package.json` dependencies:
```json
"@xyflow/react": "^12.3.6"
```

## 5. Update App.tsx import
Change:
```typescript
import BOMPage from './pages/BOMPage';
```
To:
```typescript
import BOMPage from './pages/BOM/BOMPage';
```
Then delete the old `frontend/src/pages/BOMPage.tsx`.

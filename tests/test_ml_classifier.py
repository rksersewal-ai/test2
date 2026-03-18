import pytest


TRAIN_URL = '/api/v1/ml/models/train/'
CLASSIFY_URL = '/api/v1/ml/results/classify/1/'


@pytest.mark.django_db
class TestMLClassifierDependencyGuards:
    def test_train_returns_503_when_ml_stack_missing(self, auth_client_admin, monkeypatch):
        from apps.ml_classifier import views

        monkeypatch.setattr(
            views,
            'ensure_ml_dependencies',
            lambda: (_ for _ in ()).throw(RuntimeError('missing optional ML stack')),
        )

        response = auth_client_admin.post(TRAIN_URL, {}, format='json')

        assert response.status_code == 503
        assert response.data['error'] == 'missing optional ML stack'

    def test_classify_returns_503_when_ml_stack_missing(self, auth_client_engineer, monkeypatch):
        from apps.ml_classifier import views

        monkeypatch.setattr(
            views,
            'ensure_ml_dependencies',
            lambda: (_ for _ in ()).throw(RuntimeError('missing optional ML stack')),
        )

        response = auth_client_engineer.post(CLASSIFY_URL, {}, format='json')

        assert response.status_code == 503
        assert response.data['error'] == 'missing optional ML stack'

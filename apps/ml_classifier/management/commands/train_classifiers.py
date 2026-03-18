# =============================================================================
# FILE: apps/ml_classifier/management/commands/train_classifiers.py
# SPRINT 5 — Django management command
#
# Usage:
#   python manage.py train_classifiers                   # train all targets
#   python manage.py train_classifiers --target document_type
#   python manage.py train_classifiers --target category
#   python manage.py train_classifiers --target correspondent
# =============================================================================
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Train ML metadata classifiers from existing labelled EDMS documents.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--target',
            choices=['document_type', 'category', 'correspondent', 'all'],
            default='all',
            help='Which classifier to train (default: all)',
        )

    def handle(self, *args, **options):
        target = options['target']
        from apps.ml_classifier.runtime import ensure_ml_dependencies

        try:
            ensure_ml_dependencies()
        except RuntimeError as exc:
            raise CommandError(str(exc)) from exc

        from apps.ml_classifier.pipeline  import train, train_all
        from apps.ml_classifier.inference import reload_all

        self.stdout.write(self.style.NOTICE(
            f'Training classifier(s): target={target}'
        ))

        if target == 'all':
            results = train_all()
        else:
            try:
                results = {target: train(target)}
            except ValueError as e:
                raise CommandError(str(e))

        reload_all()

        for t, result in results.items():
            if hasattr(result, 'accuracy'):
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ [{t}] v{result.version}  '
                    f'acc={result.accuracy:.2%}  '
                    f'docs={result.training_docs}  '
                    f'saved to {result.model_path}'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'  ✗ [{t}] FAILED: {result}'
                ))

from django.core.management.base import BaseCommand
from bible_way.models import (
    Language, LanguageChoices,
    Category, CategoryChoices,
    AgeGroup, AgeGroupChoices
)


class Command(BaseCommand):
    help = 'Populate default Language, Category, and AgeGroup records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing records instead of skipping them',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            default=True,
            help='Skip records that already exist (default: True)',
        )

    def handle(self, *args, **options):
        update_existing = options.get('update', False)
        skip_existing = options.get('skip_existing', True) and not update_existing

        self.stdout.write(self.style.SUCCESS('Starting to populate default data...\n'))

        # Populate Languages
        self.stdout.write('Populating Languages...')
        languages_created = 0
        languages_updated = 0
        languages_skipped = 0

        for choice_value, choice_label in LanguageChoices.choices:
            language, created = Language.objects.get_or_create(
                language_name=choice_value,
                defaults={}
            )
            if created:
                languages_created += 1
                self.stdout.write(f'  ✓ Created: {choice_label}')
            elif update_existing:
                # Update existing record if needed
                if language.language_name != choice_value:
                    language.language_name = choice_value
                    language.save()
                    languages_updated += 1
                    self.stdout.write(f'  ↻ Updated: {choice_label}')
                else:
                    languages_skipped += 1
            else:
                languages_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nLanguages: {languages_created} created, '
                f'{languages_updated} updated, {languages_skipped} skipped\n'
            )
        )

        # Populate Categories
        self.stdout.write('Populating Categories...')
        categories_created = 0
        categories_updated = 0
        categories_skipped = 0

        for index, (choice_value, choice_label) in enumerate(CategoryChoices.choices):
            category, created = Category.objects.get_or_create(
                category_name=choice_value,
                defaults={
                    'display_order': index
                }
            )
            if created:
                categories_created += 1
                self.stdout.write(f'  ✓ Created: {choice_label}')
            elif update_existing:
                # Update display_order if needed
                if category.display_order != index:
                    category.display_order = index
                    category.save()
                    categories_updated += 1
                    self.stdout.write(f'  ↻ Updated: {choice_label}')
                else:
                    categories_skipped += 1
            else:
                categories_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCategories: {categories_created} created, '
                f'{categories_updated} updated, {categories_skipped} skipped\n'
            )
        )

        # Populate Age Groups
        self.stdout.write('Populating Age Groups...')
        age_groups_created = 0
        age_groups_updated = 0
        age_groups_skipped = 0

        for index, (choice_value, choice_label) in enumerate(AgeGroupChoices.choices):
            age_group, created = AgeGroup.objects.get_or_create(
                age_group_name=choice_value,
                defaults={
                    'display_order': index
                }
            )
            if created:
                age_groups_created += 1
                self.stdout.write(f'  ✓ Created: {choice_label}')
            elif update_existing:
                # Update display_order if needed
                if age_group.display_order != index:
                    age_group.display_order = index
                    age_group.save()
                    age_groups_updated += 1
                    self.stdout.write(f'  ↻ Updated: {choice_label}')
                else:
                    age_groups_skipped += 1
            else:
                age_groups_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nAge Groups: {age_groups_created} created, '
                f'{age_groups_updated} updated, {age_groups_skipped} skipped\n'
            )
        )

        # Summary
        total_created = languages_created + categories_created + age_groups_created
        total_updated = languages_updated + categories_updated + age_groups_updated
        total_skipped = languages_skipped + categories_skipped + age_groups_skipped

        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*50}\n'
                f'Summary:\n'
                f'  Total Created: {total_created}\n'
                f'  Total Updated: {total_updated}\n'
                f'  Total Skipped: {total_skipped}\n'
                f'{"="*50}\n'
            )
        )

        self.stdout.write(self.style.SUCCESS('Default data population completed!'))


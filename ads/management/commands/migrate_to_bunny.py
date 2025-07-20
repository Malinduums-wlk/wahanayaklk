from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ads.models import Vehicle
import os

class Command(BaseCommand):
    help = 'Migrate existing files to bunny.net'

    def handle(self, *args, **options):
        self.stdout.write('Starting file migration to bunny.net...')
        
        # Migrate vehicle images
        vehicles = Vehicle.objects.all()
        total = vehicles.count()
        migrated = 0
        
        for vehicle in vehicles:
            try:
                # Migrate main image
                if vehicle.main_image:
                    self.migrate_file(vehicle.main_image)
                
                # Migrate additional images
                for image in vehicle.images.all():
                    if image.image:
                        self.migrate_file(image.image)
                
                migrated += 1
                self.stdout.write(f'Migrated files for vehicle {migrated}/{total}')
                
            except Exception as e:
                self.stderr.write(f'Error migrating files for vehicle {vehicle.id}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully migrated files for {migrated} vehicles'))

    def migrate_file(self, file_field):
        if not file_field:
            return
            
        try:
            # Read the file content
            file_content = file_field.read()
            
            # Save to new storage
            new_file = default_storage.save(
                file_field.name,
                ContentFile(file_content)
            )
            
            # Update the field with new path
            file_field.name = new_file
            file_field.save()
            
        except Exception as e:
            raise Exception(f'Error migrating file {file_field.name}: {str(e)}') 
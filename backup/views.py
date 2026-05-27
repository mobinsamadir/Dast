from django.http import FileResponse, HttpResponseForbidden
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import shutil
import os
import zipfile

@staff_member_required
def download_backup(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can download backups.")

    backup_filename = "dastdoosti_backup.zip"
    backup_filepath = os.path.join(settings.BASE_DIR, backup_filename)

    with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if 'sqlite3' in settings.DATABASES['default']['ENGINE']:
            db_path = settings.DATABASES['default']['NAME']
            if os.path.exists(db_path):
                zipf.write(db_path, os.path.basename(db_path))

        media_dir = settings.MEDIA_ROOT
        if os.path.exists(media_dir):
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, settings.BASE_DIR))

    response = FileResponse(open(backup_filepath, 'rb'), as_attachment=True, filename=backup_filename)
    return response

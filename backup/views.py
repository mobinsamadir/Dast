from django.http import FileResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
import shutil
import os
import zipfile
import tempfile

@staff_member_required
def download_backup(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can download backups.")

    backup_filename = "dastdoosti_backup.zip"
    backup_filepath = os.path.join(settings.BASE_DIR, backup_filename)
    json_dump_path = os.path.join(settings.BASE_DIR, 'database_dump.json')

    # Dump database to json
    with open(json_dump_path, 'w', encoding='utf-8') as f:
        call_command('dumpdata', format='json', indent=2, stdout=f, exclude=['contenttypes', 'auth.Permission'])

    with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the json dump
        if os.path.exists(json_dump_path):
            zipf.write(json_dump_path, os.path.basename(json_dump_path))

        # Add media files
        media_dir = settings.MEDIA_ROOT
        if os.path.exists(media_dir):
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create a media/ prefix in the zip for clarity
                    arcname = os.path.join('media', os.path.relpath(file_path, media_dir))
                    zipf.write(file_path, arcname)

    # Cleanup the temporary json dump
    if os.path.exists(json_dump_path):
        os.remove(json_dump_path)

    response = FileResponse(open(backup_filepath, 'rb'), as_attachment=True, filename=backup_filename)
    return response


@staff_member_required
def upload_restore_backup(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can restore backups.")

    if request.method == 'POST':
        if 'backup_file' not in request.FILES:
            messages.error(request, 'No file uploaded.')
            return HttpResponseRedirect(reverse('admin:index'))

        backup_file = request.FILES['backup_file']
        if not backup_file.name.endswith('.zip'):
            messages.error(request, 'Uploaded file must be a zip archive.')
            return HttpResponseRedirect(reverse('admin:index'))

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = os.path.join(temp_dir, 'backup.zip')

            with open(temp_zip_path, 'wb+') as f:
                for chunk in backup_file.chunks():
                    f.write(chunk)

            try:
                with zipfile.ZipFile(temp_zip_path, 'r') as zipf:
                    zipf.extractall(temp_dir)

                # Restore database
                json_dump_path = os.path.join(temp_dir, 'database_dump.json')
                if os.path.exists(json_dump_path):
                    call_command('loaddata', json_dump_path)
                else:
                    messages.warning(request, 'No database_dump.json found in the archive.')

                # Restore media
                extracted_media_dir = os.path.join(temp_dir, 'media')
                if os.path.exists(extracted_media_dir):
                    if not os.path.exists(settings.MEDIA_ROOT):
                        os.makedirs(settings.MEDIA_ROOT)
                    for item in os.listdir(extracted_media_dir):
                        s = os.path.join(extracted_media_dir, item)
                        d = os.path.join(settings.MEDIA_ROOT, item)
                        if os.path.isdir(s):
                            if os.path.exists(d):
                                shutil.rmtree(d)
                            shutil.copytree(s, d)
                        else:
                            shutil.copy2(s, d)

                messages.success(request, 'Backup restored successfully.')
            except Exception as e:
                messages.error(request, f'Error restoring backup: {str(e)}')

        return HttpResponseRedirect(reverse('admin:index'))

    return render(request, 'backup/upload_restore.html')

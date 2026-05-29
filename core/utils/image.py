import sys
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

def process_image(image_field, quality=82):
    """
    Process an image:
    - Convert to WebP format
    - Max dimensions: 1200x1200px (preserve aspect ratio)
    - Strip EXIF metadata
    - Handle RGBA/P modes (convert to RGB before WebP)
    """
    if not image_field:
        return None

    img = Image.open(image_field)

    # Strip EXIF metadata is automatic when creating a new image from data,
    # but we can also use getdata to be sure or just re-save it without exif.
    # PIL's save drops EXIF unless explicitly requested.

    # Handle RGBA/P modes
    if img.mode in ('RGBA', 'P', 'LA'):
        # Create a white background image
        background = Image.new('RGB', img.size, (255, 255, 255))
        # Paste the image on the background. If it has alpha channel, use it as mask.
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        elif img.mode == 'LA':
            background.paste(img, mask=img.split()[1])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize to max 1200x1200, preserving aspect ratio
    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)

    output = BytesIO()
    # WebP method: 6 (maximum compression effort)
    img.save(output, format='WEBP', quality=quality, method=6)
    output.seek(0)

    # Generate new filename
    original_name = image_field.name
    # Handle path vs just name
    name_parts = original_name.rsplit('.', 1)
    new_name = f"{name_parts[0]}.webp"

    return InMemoryUploadedFile(
        output,
        'ImageField',
        new_name,
        'image/webp',
        sys.getsizeof(output),
        None
    )

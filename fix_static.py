with open("dastdoosti/settings.py", "r") as f:
    content = f.read()

import re
content = re.sub(r"STATICFILES_DIRS\s*=\s*\[.*?\]", "STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core', 'static')]", content, flags=re.DOTALL)

with open("dastdoosti/settings.py", "w") as f:
    f.write(content)

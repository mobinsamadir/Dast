import re

with open('accounts/api/views.py', 'r') as f:
    text = f.read()

text = re.sub(
    r"@api_view\(\['GET'\]\)\n@extend_schema\(responses=\{200: UserSerializer\(many=True\)\}\)",
    r"@extend_schema(responses={200: UserSerializer(many=True)})\n@api_view(['GET'])",
    text
)

with open('accounts/api/views.py', 'w') as f:
    f.write(text)

with open('core/api/views.py', 'r') as f:
    text2 = f.read()

text2 = re.sub(
    r"@api_view\(\['GET'\]\)\n\n@extend_schema\(responses=\{200: dict\}\)",
    r"@extend_schema(responses={200: dict})\n@api_view(['GET'])",
    text2
)

with open('core/api/views.py', 'w') as f:
    f.write(text2)

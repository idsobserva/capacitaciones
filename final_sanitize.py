import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ensure only ONE <script type="module"> exists for the main logic.
# Let's find all script tags related to the module.
script_matches = list(re.finditer(r'<script( type="module")?>(.*?)</script>', content, re.DOTALL))

# We want the big one that contains imports.
main_script_idx = -1
for i, match in enumerate(script_matches):
    if 'import {' in match.group(2):
        main_script_idx = i
        break

if main_script_idx != -1:
    main_match = script_matches[main_script_idx]
    script_body = main_match.group(2)

    # Remove duplicate ADMIN_NAME
    # Find all occurrences of "const ADMIN_NAME ="
    # Keep only one.
    script_body = re.sub(r'const ADMIN_NAME\s*=\s*"Administrador";', '', script_body)
    # The one at line 1576 is "const ADMIN_NAME  = "Administrador ODS";" - let's keep that one.

    # Ensure no empty try-catch blocks are breaking things
    script_body = re.sub(r'try\s*{\s*}\s*catch\s*\(e\)\s*{\s*}', '', script_body)

    # Re-insert the cleaned script body into the content
    new_main_script = f'<script type="module">\n{script_body}\n</script>'
    content = content[:main_match.start()] + new_main_script + content[main_match.end():]

# Remove other empty script tags that might have been left around 1474
content = re.sub(r'<script>\s*</script>', '', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Sanitization complete.")

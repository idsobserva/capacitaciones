import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def deduplicate_functions(script_content):
    # Find all function declarations: function name(args) { ... }
    # This is complex for nested functions, but let's target top-level ones in the script.

    # Simpler: find all "function NAME("
    funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', script_content)
    seen = set()
    duplicates = []
    for f in funcs:
        if f in seen:
            duplicates.append(f)
        seen.add(f)

    print(f"Duplicates found: {duplicates}")

    for dup in set(duplicates):
        # Find all occurrences of the function
        # This regex is a bit greedy but should work for simple SPA functions
        pattern = r'function\s+' + dup + r'\s*\([^)]*\)\s*\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\}'
        occurrences = list(re.finditer(pattern, script_content))
        if len(occurrences) > 1:
            print(f"Removing duplicate for {dup}")
            # Keep only the FIRST occurrence (usually the one I want, or the most stable)
            # Actually, sometimes the later one is better if it was an "overwrite".
            # But in modules, you can't redefine.
            for occ in occurrences[1:]:
                script_content = script_content[:occ.start()] + (" " * (occ.end() - occ.start())) + script_content[occ.end():]

    return script_content

script_match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
if script_match:
    original_script = script_match.group(1)
    cleaned_script = deduplicate_functions(original_script)
    content = content.replace(original_script, cleaned_script)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

import subprocess
import re

def get_script():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
    return match.group(1) if match else None

def check_syntax(script):
    with open('temp.mjs', 'w', encoding='utf-8') as f:
        f.write(script)
    result = subprocess.run(['node', '--check', 'temp.mjs'], capture_output=True, text=True)
    return result.returncode == 0, result.stderr

for i in range(200):
    script = get_script()
    ok, err = check_syntax(script)
    if ok:
        print(f"DONE at iteration {i}")
        break

    match = re.search(r'temp\.mjs:(\d+)', err)
    if not match:
        print(f"Non-line error: {err}")
        break

    line_num = int(match.group(1))
    lines = script.split('\n')

    # Check if the line is already a Fix line. If so, maybe the error is elsewhere or the fix is wrong.
    # But let's just keep going for now.
    lines[line_num-1] = "// Fix " + str(i) + ": " + lines[line_num-1]
    script = '\n'.join(lines)

    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Safely replace script
    parts = re.split(r'(<script type="module">|</script>)', content)
    if len(parts) >= 3:
        parts[2] = script
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write("".join(parts))
    else:
        print("Regex fail")
        break

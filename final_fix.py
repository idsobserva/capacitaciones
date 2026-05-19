import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Module
content = content.replace('<script>', '<script type="module">', 1)

# 2. Extract script
match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
if match:
    script_start = match.start(1)
    script_end = match.end(1)
    script_content = match.group(1)

    # 3. Targeted Rename of the MOST LIKELY BREAKING dups
    breaking = ["imageToBase64", "uploadImage", "updateTopbarAvatar", "renderPerfilView", "_epPerfiles", "_ipsCache", "getIPSForMun", "loadFooterConfig", "applyFooterConfig", "prefillFooterModal", "postSetupInit", "buildQ", "renderActas", "selPerfilesCap", "selPerfilesPlan", "allCaps", "allPlans", "allUsers", "allActores", "tiposCap", "metas"]

    for name in breaking:
        pattern = re.compile(r'\b(function|let|const|var|async\s+function)\s+(' + name + r')\b')
        matches = list(pattern.finditer(script_content))
        if len(matches) > 1:
            # Rename all but the LAST one
            for i, m in enumerate(reversed(matches[:-1])):
                idx = len(matches) - 2 - i
                script_content = script_content[:m.start(2)] + f"{name}_old_{idx}" + script_content[m.end(2):]

    # 4. Remove clutter at the end
    script_content = re.sub(r'try\s*{\s*(window|Object\.defineProperty).*?\}\s*catch\s*\(e\)\s*{\s*}', '', script_content, flags=re.DOTALL)
    script_content = re.sub(r'try\s*{\s*}\s*catch\s*\(e\)\s*{\s*}', '', script_content)

    # 5. Global Exposure
    exposed_functions = [
        "authTab", "doLogin", "doRegister", "showView", "switchTab", "openPlanModal",
        "savePlan", "editPlan", "deletePlan", "openCapModal", "saveCap", "editCap",
        "deleteCap", "verActa", "printActa", "downloadPDF", "aprobarActa"
    ]

    exposure_script = "\n// --- Global Exposure ---\n"
    exposure_script += 'const ADMIN_NAME = "Administrador ODS";\n'
    for func in exposed_functions:
        exposure_script += f"window.{func} = {func};\n"

    script_content += exposure_script

    content = content[:script_start] + script_content + content[script_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

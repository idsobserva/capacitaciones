import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Module
content = content.replace('<script>', '<script type="module">', 1)

# Global Exposure
exposed_functions = [
    "authTab", "doLogin", "doRegister", "showView", "switchTab", "openPlanModal",
    "savePlan", "editPlan", "deletePlan", "openCapModal", "saveCap", "editCap",
    "deleteCap", "verActa", "printActa", "downloadPDF", "aprobarActa"
]
exposure = "\n// --- Global Exposure ---\n"
for f in exposed_functions:
    exposure += f"window.{f} = {f};\n"
content = content.replace('</script>\n</body>', exposure + '</script>\n</body>')

# Remove the massive block of try-catch at the end
content = re.sub(r'try\s*{\s*(window|Object\.defineProperty).*?\}\s*catch\s*\(e\)\s*{\s*}', '', content, flags=re.DOTALL)

# Targeted Rename for the most annoying duplicates
to_rename = ["imageToBase64", "uploadImage", "updateTopbarAvatar", "renderPerfilView",
             "getIPSForMun", "loadFooterConfig", "applyFooterConfig", "prefillFooterModal",
             "postSetupInit", "buildQ", "renderActas", "_epPerfiles", "_ipsCache",
             "selPerfilesPlan", "selPerfilesCap", "allCaps", "allPlans", "allUsers",
             "allActores", "tiposCap", "metas"]

for name in to_rename:
    pattern = re.compile(r'\b(function|let|const|var|async\s+function)\s+(' + name + r')\b')
    matches = list(pattern.finditer(content))
    if len(matches) > 1:
        # Keep LAST, rename others
        for i, m in enumerate(reversed(matches[:-1])):
            idx = len(matches) - 2 - i
            content = content[:m.start(2)] + f"{name}_old_{idx}" + content[m.end(2):]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

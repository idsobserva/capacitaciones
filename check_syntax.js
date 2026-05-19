const fs = require('fs');
const content = fs.readFileSync('index.html', 'utf8');
const match = content.match(/<script type="module">([\s\S]*?)<\/script>/);
if (match) {
    const script = match[1];
    fs.writeFileSync('temp_script.mjs', script);
}

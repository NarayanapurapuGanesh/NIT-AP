import os, re

src_dir = 'C:/Users/Ganesh/Documents/NIT-AP/frontend'
failed = False

def check_path(base_dir, imp_path):
    global failed
    p = os.path.normpath(os.path.join(base_dir, imp_path))
    dir_name = os.path.dirname(p)
    base_name = os.path.basename(p)
    
    if not os.path.exists(dir_name):
        return
        
    files = os.listdir(dir_name)
    found = False
    for f in files:
        if f == base_name or f.startswith(base_name + '.') or (os.path.isdir(os.path.join(dir_name, f)) and f == base_name):
            found = True
            break
            
    if not found:
        any_match = [f for f in files if f.lower() == base_name.lower() or f.lower().startswith(base_name.lower() + '.')]
        if any_match:
            print(f"Case mismatch: expected {any_match[0]}, got {base_name} in {base_dir}")
            failed = True

for root, _, files in os.walk(src_dir):
    if 'node_modules' in root or '.next' in root:
        continue
    for file in files:
        if file.endswith('.ts') or file.endswith('.tsx'):
            filepath = os.path.join(root, file)
            try:
                content = open(filepath, 'r', encoding='utf-8').read()
                for match in re.findall(r'(?:import|export).*?from\s+[\'"]([^\'"]+)[\'"]', content):
                    if match.startswith('./') or match.startswith('../'):
                        check_path(root, match)
                    elif match.startswith('@/'):
                        check_path(src_dir, match[2:])
            except Exception as e:
                pass

if not failed:
    print('No case sensitivity issues found!')

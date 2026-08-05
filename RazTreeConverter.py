import os
import re
import json
import shutil

cwd = os.getcwd()
out_dir = os.path.join(cwd, 'output')
os.makedirs(out_dir, exist_ok=True)

for root_id in os.listdir(cwd):
    root_path = os.path.join(cwd, root_id)
    if not os.path.isdir(root_path) or root_id in ('output', 'Common', '.git'):
        continue

    max_minor_len = 1
    max_patch_len = 1
    valid_folders = []

    for ver_folder in os.listdir(root_path):
        ver_path = os.path.join(root_path, ver_folder)
        info_path = os.path.join(ver_path, 'info.json')
        
        if not os.path.isfile(info_path):
            continue
            
        valid_folders.append((ver_folder, ver_path, info_path))
        
        parts = re.findall(r'\d+', ver_folder)
        if len(parts) > 1:
            max_minor_len = max(max_minor_len, len(parts[1]))
        if len(parts) > 2:
            max_patch_len = max(max_patch_len, len(parts[2]))

    for ver_folder, ver_path, info_path in valid_folders:

        # ===== 先只读 Version 字段（避免 json.load）=====
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except:
            continue

        m_ver = re.search(r'"Version"\s*:\s*"([^"]+)"', text)
        orig = m_ver.group(1) if m_ver else ''

        m = re.match(r'^(\d+)\.(\d+)', orig)
        if m:
            major, minor = m.groups()
        else:
            parts = re.findall(r'\d+', orig)
            major = parts[0] if len(parts) > 0 else ''
            minor = parts[1] if len(parts) > 1 else ''

        parts = re.findall(r'\d+', ver_folder)
        v_major = parts[0] if len(parts) > 0 else '0'
        v_minor = parts[1].zfill(max_minor_len) if len(parts) > 1 else '0'.zfill(max_minor_len)
        v_patch = parts[2].zfill(max_patch_len) if len(parts) > 2 else '0'.zfill(max_patch_len)

        digits = f"{v_major}{v_minor}{v_patch}"
        digits = str(int(digits)) 

        new_version = f"{major}.{minor}.{digits}x{root_id}"
        out_file = os.path.join(out_dir, f"{new_version}.json")

        # ===== 现在真正实现“先跳过再执行”=====
        if os.path.exists(out_file):
            print(f"[SKIP] {out_file} already exists")
            continue

        # ===== 只有需要写入时才完整解析 JSON =====
        data = json.loads(text)
        data['Version'] = new_version

        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',',':'))

        print(f"[OK] {info_path} -> {out_file}")

# ===== 复制 Common =====
common_dir = os.path.join(cwd, 'Common')
if os.path.isdir(common_dir):
    for file in os.listdir(common_dir):
        if not file.lower().endswith('.json'):
            continue

        src_file = os.path.join(common_dir, file)
        dst_file = os.path.join(out_dir, file)

        if os.path.exists(dst_file):
            print(f"[SKIP] {dst_file} already exists")
            continue

        shutil.copy2(src_file, dst_file)
        print(f"[COPY] {src_file} -> {dst_file}")
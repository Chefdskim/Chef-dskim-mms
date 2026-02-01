from flask import Flask, render_template, jsonify, send_from_directory
import os
import json
import pandas as pd
import glob

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVE_DIR = r'G:\내 드라이브\전문요리서적과 영상자료'
DB_FILE = os.path.join(BASE_DIR, 'file_list.json')

@app.route('/')
def home():
    return render_template('index.html')

# 자료실
@app.route('/api/files')
def get_files():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    else:
        return scan_files()

def scan_files():
    files = []
    print("--- 🚀 자료실 스캔 시작 ---")
    try:
        if not os.path.exists(DRIVE_DIR):
             return jsonify([])
        for root, dirs, filenames in os.walk(DRIVE_DIR):
            for filename in filenames:
                if filename.startswith('~$') or filename.startswith('.'): continue
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, DRIVE_DIR).replace('\\', '/')
                lower = filename.lower()
                ftype = 'unknown'
                if lower.endswith(('.xlsx', '.xls')): ftype = 'excel'
                elif lower.endswith('.pdf'): ftype = 'pdf'
                elif lower.endswith(('.mp4', '.mov', '.avi')): ftype = 'video'
                files.append({'name': filename, 'path': relative_path, 'folder': os.path.basename(root), 'type': ftype})
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False)
    except Exception as e:
        print(f"❌ 오류: {e}")
        return jsonify([])
    return jsonify(files)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(DRIVE_DIR, filename)


# 원가계산기
def find_excel_file():
    all_files = os.listdir(BASE_DIR)
    # 1순위: DB.xlsx.xlsx
    if 'DB.xlsx.xlsx' in all_files: return os.path.join(BASE_DIR, 'DB.xlsx.xlsx')
    # 2순위: DB.xlsx
    if 'DB.xlsx' in all_files: return os.path.join(BASE_DIR, 'DB.xlsx')
    # 3순위: 그냥 엑셀 파일 아무거나
    for f in all_files:
        if f.lower().endswith('.xlsx') and 'app.py' not in f:
            return os.path.join(BASE_DIR, f)
    return None

@app.route('/api/ingredients')
def get_ingredients():
    target_file = find_excel_file()
    if target_file is None:
        print("❌ [오류] 엑셀 파일을 찾을 수 없습니다!")
        return jsonify({"error": "폴더에 엑셀 파일이 없습니다."})

    try:
        print(f"📖 엑셀 파일 읽는 중: {os.path.basename(target_file)}")
        # 헤더는 2번째 줄 (index 1)
        df = pd.read_excel(target_file, sheet_name='식자재 가격표', header=1)
        
        ing_list = []
        
        # 왼쪽 세트
        part1 = df.iloc[:, [0, 1, 2]].copy()
        part1.columns = ['name', 'spec', 'price']
        
        # 오른쪽 세트
        part2 = df.iloc[:, [5, 6, 7]].copy()
        part2.columns = ['name', 'spec', 'price']
        
        full_df = pd.concat([part1, part2])
        
        count = 0
        for _, row in full_df.iterrows():
            name = str(row['name']).strip()
            if name == 'nan' or name == '' or name == 'None': continue
            
            try:
                spec_raw = str(row['spec']).lower()
                price = row['price']
                if pd.isna(price) or price == '': price = 0
                else: price = float(price)
                
                gram = 1000 
                if 'kg' in spec_raw or 'l' in spec_raw:
                   num = ''.join(filter(str.isdigit, spec_raw.split('k')[0].split('l')[0]))
                   if num: gram = float(num) * 1000
                elif 'g' in spec_raw:
                   num = ''.join(filter(str.isdigit, spec_raw.split('g')[0]))
                   if num: gram = float(num)
                
                price_per_g = 0
                if price > 0: price_per_g = price / gram
                
                ing_list.append({'name': name, 'spec': row['spec'], 'price': price, 'price_per_g': price_per_g})
                count += 1
            except:
                continue

        print(f"✅ 재료 목록 로딩 성공! 총 {count}개 발견됨.")
        return jsonify(ing_list)

    except Exception as e:
        print(f"❌ 엑셀 읽기 실패: {e}")
        return jsonify({"error": f"엑셀 오류: {str(e)}"})

if __name__ == '__main__':
    print(f"🚀 시스템 가동 중...")
    f = find_excel_file()
    if f: print(f"👉 엑셀 파일 감지됨: {os.path.basename(f)}")
    else: print(f"⚠️ 경고: 엑셀 파일이 없습니다.")
    app.run(host='0.0.0.0', port=5000, debug=True)
import numpy as np
from PIL import Image
import matplotlib.cm as cm
import os
import sys

# --- 設定 ---
INPUT_FILE = 'data/from_top_4.csv'
OUTPUT_FILE = 'output/converted_image.jpg'
JPEG_QUALITY = 95

def csv_to_jpeg():
    setup_directories()
    
    if not os.path.exists(INPUT_FILE):
        print(f"エラー: {INPUT_FILE} が見つかりません。")
        return

    print(f"{INPUT_FILE} を読み込んでいます... (データが大きい場合、時間がかかります)")

    try:
        # --- 1. CSVデータの読み込み (genfromtxtに変更) ---
        # filling_values=0 : 空欄があれば 0 で埋める
        # dtype=np.float32 : メモリ節約
        data_matrix = np.genfromtxt(INPUT_FILE, delimiter=',', filling_values=0, dtype=np.float32)
        
        print(f"データ読み込み完了。サイズ: {data_matrix.shape} (行, 列)")
        print("データをカラーマップ(jet)でRGB変換中...")

        # --- 2. データの正規化 ---
        min_val = np.nanmin(data_matrix) # nanが入っていても無視して最小値を取得
        max_val = np.nanmax(data_matrix) # nanが入っていても無視して最大値を取得

        # 万が一データが全部 NaN だった場合の対策
        if np.isnan(min_val) or np.isnan(max_val):
            min_val = 0
            max_val = 1

        if max_val == min_val:
            normalized_data = np.zeros_like(data_matrix, dtype=np.float32)
        else:
            normalized_data = (data_matrix - min_val) / (max_val - min_val)

        # NaN（計算不能な値）が残っていると画像化でエラーになるので 0 に置換
        normalized_data = np.nan_to_num(normalized_data)

        # --- カラーマップ適用 ---
        colored_data_rgba = cm.jet(normalized_data)
        image_data = (colored_data_rgba[:, :, :3] * 255).astype(np.uint8)

        # --- 3. 保存 ---
        print("画像を保存中...")
        img = Image.fromarray(image_data, 'RGB')
        img.save(OUTPUT_FILE, 'JPEG', quality=JPEG_QUALITY)
        print(f"変換完了: {OUTPUT_FILE} を保存しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

def setup_directories():
    if not os.path.exists('data'): os.makedirs('data')
    if not os.path.exists('output'): os.makedirs('output')

if __name__ == '__main__':
    csv_to_jpeg()
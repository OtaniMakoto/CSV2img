import tkinter as tk
from tkinter import filedialog, messagebox
import os
import numpy as np
from PIL import Image
import matplotlib.cm as cm

# --- 設定 ---
JPEG_QUALITY = 95

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV to Heatmap Converter")
        self.root.geometry("500x200")

        # 変数
        self.file_path = tk.StringVar()

        # --- GUIレイアウト ---
        # 1. ファイル選択部分
        frame_input = tk.Frame(root, padx=20, pady=20)
        frame_input.pack(fill='x')

        lbl_instr = tk.Label(frame_input, text="CSVファイルを選択してください:")
        lbl_instr.pack(anchor='w')

        entry_path = tk.Entry(frame_input, textvariable=self.file_path, width=50)
        entry_path.pack(side='left', padx=(0, 10))

        btn_browse = tk.Button(frame_input, text="参照...", command=self.browse_file)
        btn_browse.pack(side='left')

        # 2. 実行ボタン部分
        frame_action = tk.Frame(root, padx=20, pady=10)
        frame_action.pack(fill='x')

        self.btn_convert = tk.Button(frame_action, text="変換実行", command=self.run_conversion, bg="#dddddd", height=2)
        self.btn_convert.pack(fill='x')

        # 3. ステータス表示
        self.lbl_status = tk.Label(root, text="待機中...", fg="gray")
        self.lbl_status.pack(pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.lbl_status.config(text="ファイルが選択されました", fg="black")

    def run_conversion(self):
        input_csv = self.file_path.get()
        
        if not input_csv or not os.path.exists(input_csv):
            messagebox.showerror("エラー", "有効なCSVファイルを選択してください。")
            return

        # 保存先のパスを作成（元のファイル名の拡張子を .jpg に変えたもの）
        output_jpg = os.path.splitext(input_csv)[0] + ".jpg"

        try:
            self.lbl_status.config(text="処理中... (応答なしになる場合があります)", fg="blue")
            self.root.update() # 画面描画を更新

            # --- 変換ロジック (前回と同じ) ---
            
            # 1. 読み込み (欠損値対応版)
            data_matrix = np.genfromtxt(input_csv, delimiter=',', filling_values=0, dtype=np.float32)

            # 2. 正規化
            min_val = np.nanmin(data_matrix)
            max_val = np.nanmax(data_matrix)

            if np.isnan(min_val) or np.isnan(max_val):
                min_val, max_val = 0, 1

            if max_val == min_val:
                normalized_data = np.zeros_like(data_matrix, dtype=np.float32)
            else:
                normalized_data = (data_matrix - min_val) / (max_val - min_val)
            
            normalized_data = np.nan_to_num(normalized_data)

            # 3. カラーマップ適用 (Jet)
            colored_data_rgba = cm.jet(normalized_data)
            image_data = (colored_data_rgba[:, :, :3] * 255).astype(np.uint8)

            # 4. 保存
            img = Image.fromarray(image_data, 'RGB')
            img.save(output_jpg, 'JPEG', quality=JPEG_QUALITY)

            self.lbl_status.config(text=f"完了！保存しました: {os.path.basename(output_jpg)}", fg="green")
            messagebox.showinfo("成功", f"画像を保存しました！\n{output_jpg}")

        except Exception as e:
            self.lbl_status.config(text="エラーが発生しました", fg="red")
            messagebox.showerror("エラー", f"変換に失敗しました。\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()
"""
Context Library - File upload and management
"""
import os
from pathlib import Path
import streamlit as st
from datetime import datetime

# ─── Context Library (File Management) ───────────────────────────
CONTEXT_DIR = str(Path(__file__).resolve().parent.parent.parent / "context")
os.makedirs(CONTEXT_DIR, exist_ok=True)

def get_context_files():
    """アップロード済みファイル一覧を取得"""
    if "context_files" not in st.session_state:
        st.session_state.context_files = {}
    return st.session_state.context_files

def add_context_file(filename: str, content: bytes, file_type: str):
    """コンテキストファイルを追加"""
    filepath = os.path.join(CONTEXT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    if "context_files" not in st.session_state:
        st.session_state.context_files = {}

    st.session_state.context_files[filename] = {
        "path": filepath,
        "type": file_type,
        "active": True,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def toggle_context_file(filename: str):
    """ファイルのアクティブ状態を切り替え"""
    if filename in st.session_state.context_files:
        st.session_state.context_files[filename]["active"] = not st.session_state.context_files[filename]["active"]

def delete_context_file(filename: str):
    """コンテキストファイルを削除"""
    if filename in st.session_state.context_files:
        filepath = st.session_state.context_files[filename]["path"]
        if os.path.exists(filepath):
            os.remove(filepath)
        del st.session_state.context_files[filename]

def extract_excel_data(filepath: str) -> str:
    """Excelファイルから財務データを抽出"""
    try:
        import pandas as pd
        # 全シートを読み込み
        xl_file = pd.ExcelFile(filepath)
        extracted = f"【エクセルファイル: {os.path.basename(filepath)}】\n\n"

        for sheet_name in xl_file.sheet_names[:3]:  # 最初の3シートまで
            df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=100)  # 最大100行
            extracted += f"## シート: {sheet_name}\n"
            extracted += df.to_string(index=False, max_rows=50)
            extracted += "\n\n"

        return extracted
    except Exception as e:
        return f"エクセル読み込みエラー: {str(e)}"

def extract_text_data(filepath: str) -> str:
    """テキストファイルからデータを抽出"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()[:10000]  # 最初の10000文字
        return f"【テキストファイル: {os.path.basename(filepath)}】\n\n{content}"
    except:
        try:
            with open(filepath, "r", encoding="shift-jis") as f:
                content = f.read()[:10000]
            return f"【テキストファイル: {os.path.basename(filepath)}】\n\n{content}"
        except Exception as e:
            return f"テキスト読み込みエラー: {str(e)}"

def extract_pdf_data(filepath: str) -> str:
    """PDFファイルからテキストを抽出"""
    try:
        import pypdf
        extracted = f"【PDFファイル: {os.path.basename(filepath)}】\n\n"

        with open(filepath, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            num_pages = min(len(pdf_reader.pages), 20)  # 最大20ページ

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                extracted += f"--- Page {page_num + 1} ---\n{text}\n\n"

                # 文字数制限（約20000文字まで）
                if len(extracted) > 20000:
                    extracted = extracted[:20000] + "\n\n[... 以降省略 ...]"
                    break

        return extracted
    except ImportError:
        return f"【PDFファイル: {os.path.basename(filepath)}】\n\nエラー: pypdfライブラリがインストールされていません。\n`pip install pypdf` を実行してください。"
    except Exception as e:
        return f"PDF読み込みエラー: {str(e)}"

def get_active_context_data() -> str:
    """アクティブなコンテキストファイルのデータを統合"""
    context_files = get_context_files()
    context_data = ""

    for filename, info in context_files.items():
        if info["active"]:
            filepath = info["path"]
            file_type = info["type"]

            if file_type in ["xlsx", "xls"]:
                context_data += extract_excel_data(filepath) + "\n" + "="*50 + "\n\n"
            elif file_type in ["txt", "md", "csv"]:
                context_data += extract_text_data(filepath) + "\n" + "="*50 + "\n\n"
            elif file_type == "pdf":
                context_data += extract_pdf_data(filepath) + "\n" + "="*50 + "\n\n"

    return context_data



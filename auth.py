import os
import streamlit as st
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

def check_password():
    """シンプルなパスワード保護機能を提供する"""
    # 環境変数からパスワードを取得、設定されていない場合はデフォルト値を使用
    correct_password = os.getenv("APP_PASSWORD", "default_password")
    
    # 開発環境かどうかを確認
    is_dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() in ("true", "1", "yes")
    
    # 開発モードの場合は認証をスキップ
    if is_dev_mode:
        # すでにセッション状態が設定されていなければ設定する
        if "password_correct" not in st.session_state:
            st.session_state.password_correct = True
        return True
    
    # セッション状態の初期化
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    # すでに認証されている場合は何もしない
    if st.session_state.password_correct:
        return True
    
    # ログインフォームを表示
    st.title("送料シミュレーター")
    
    password = st.text_input("パスワードを入力してください", type="password")
    login_btn = st.button("ログイン")
    
    if login_btn:
        if password == correct_password:
            st.session_state.password_correct = True
            # experimental_rerunの代わりにrerunを使用
            st.rerun()
        else:
            st.error("パスワードが正しくありません")
            return False
    
    # パスワードが正しくなければ、メインアプリを表示しない
    if not st.session_state.password_correct:
        st.stop()
    
    return True
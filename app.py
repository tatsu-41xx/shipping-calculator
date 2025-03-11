import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import OrderedDict

# 自作モジュールのインポート
from auth import check_password
from utils.data_loader import load_shipping_rates, load_population_data
from utils.calculator import (
    calculate_regional_shipments,
    calculate_shipping_costs,
    calculate_summary
)

# ページ設定
st.set_page_config(
    page_title="送料シミュレーター",
    page_icon="📦",
    layout="wide"
)

# パスワード認証
if not check_password():
    st.stop()

# データ読み込み
shipping_rates = load_shipping_rates()
population_data = load_population_data()

# サイドバー - 入力フォーム
with st.sidebar:
    st.title("送料シミュレーター")
    st.markdown("---")
    
    # 出荷個数の入力
    total_shipments = st.number_input(
        "想定される全国総出荷個数",
        min_value=1,
        max_value=1000000,
        value=1000,
        step=100
    )
    
    # 荷物サイズの選択と割合の設定
    st.subheader("荷物サイズと割合")
    st.markdown("各サイズの出荷割合を設定してください（合計が100%になるようにします）")
    
    # サイズオプションの取得
    size_options = shipping_rates[['size_code', 'size_name', 'weight']].copy()
    
    # サイズ選択と割合の入力用のコンテナ
    size_selections = []
    total_proportion = 0.0
    remaining_proportion = 100.0
    
    # 最大5つのサイズまで追加できるようにする
    max_sizes = 5
    size_count = st.number_input("使用するサイズの数", min_value=1, max_value=max_sizes, value=1)
    
    # サイズの選択と割合の入力
    size_distribution = {}
    
    # 各サイズ選択で使用できるサイズのリストを管理
    available_size_indices = list(range(len(size_options)))
    
    for i in range(size_count):
        st.markdown(f"**サイズ {i+1}**")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            size_display = [f"{row['size_name']} ({row['weight']})" for _, row in size_options.iterrows()]
            size_values = size_options['size_code'].tolist()
            
            # デフォルト値の設定 - 残りの選択肢から選ぶ
            default_index = min(i, len(available_size_indices) - 1)
            if available_size_indices:
                default_size_index = available_size_indices[default_index]
            else:
                default_size_index = 0
            
            selected_size_index = st.selectbox(
                f"サイズを選択 #{i+1}",
                range(len(size_display)),
                format_func=lambda i: size_display[i],
                index=default_size_index,
                key=f"size_select_{i}"
            )
            selected_size = size_values[selected_size_index]
        
        with col2:
            # 最後のサイズは残りの割合を自動設定
            if i == size_count - 1:
                proportion = remaining_proportion
                st.text(f"{proportion:.1f}%（残り）")
            else:
                max_available = min(100.0, remaining_proportion)
                default_value = max_available if i == 0 else min(25.0, max_available)
                proportion = st.number_input(
                    "割合 (%)",
                    min_value=0.1,
                    max_value=max_available,
                    value=default_value,
                    step=0.1,
                    key=f"proportion_{i}"
                )
                remaining_proportion -= proportion
        
        # 選択されたサイズと割合を保存
        size_distribution[selected_size] = proportion / 100.0
    
    # 詳細設定の折りたたみメニュー
    with st.expander("地域別出荷比率の詳細設定"):
        st.markdown("地域別の出荷比率を調整できます。初期値は人口分布に基づいています。")
        
        # 地域別の出荷比率調整（オプション）
        custom_distribution = {}
        total_percentage = 100.0
        remaining_percentage = 100.0
        
        for i, (region, row) in enumerate(population_data.iterrows()):
            default_pct = row['percentage'] * 100
            # 最後の地域は残りの割合を自動計算
            if i == len(population_data) - 1:
                pct_value = remaining_percentage
                st.text(f"{region}: {pct_value:.1f}%（残り）")
                custom_distribution[region] = pct_value / 100
            else:
                pct_value = st.slider(
                    f"{region}",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(default_pct),
                    step=0.1,
                    format="%.1f%%"
                )
                custom_distribution[region] = pct_value / 100
                remaining_percentage -= pct_value
        
        use_custom = st.checkbox("カスタム地域比率を使用", value=False)
    
    # 計算実行ボタン
    calc_button = st.button("送料を計算", type="primary")

# サイドバー - 送料データのアップロード機能
with st.sidebar:
    st.markdown("---")
    st.subheader("送料データのアップロード")
    
    st.markdown("""
    送料は機密情報です。アップロードしたデータはセッション中のみ使用され、保存されません。
    ブラウザを閉じるか更新すると、データは消去されます。
    """)
    
    uploaded_file = st.file_uploader("送料CSVファイルをアップロード", type="csv")
    
    if uploaded_file is not None:
        try:
            # アップロードされたCSVを読み込み
            uploaded_shipping_rates = pd.read_csv(uploaded_file)
            
            # 必要なカラムが含まれているか確認
            required_columns = ['size_code', 'size_name', 'weight', '北海道', '北東北', '南東北', 
                              '関東', '信越', '北陸', '中部', '関西', '中国', '四国', '九州', '沖縄']
            
            missing_columns = [col for col in required_columns if col not in uploaded_shipping_rates.columns]
            
            if missing_columns:
                st.error(f"以下の必須カラムがCSVファイルに含まれていません: {', '.join(missing_columns)}")
            else:
                # セッションステートに保存（一時的な使用のみ）
                st.session_state.custom_shipping_rates = uploaded_shipping_rates
                st.success("送料データを正常に読み込みました！セッション中のみ有効です。")
                
                # アップロードされたデータの確認表示
                with st.expander("アップロードしたデータを確認"):
                    st.dataframe(uploaded_shipping_rates)
                
        except Exception as e:
            st.error(f"ファイルの読み込み中にエラーが発生しました: {str(e)}")

# データ読み込み（アップロードされたデータを優先）
if 'custom_shipping_rates' in st.session_state:
    shipping_rates = st.session_state.custom_shipping_rates
    st.info("アップロードされた送料データを使用しています（セッション中のみ有効）")
else:
    shipping_rates = load_shipping_rates()

# メインコンテンツ
st.title("送料シミュレーター")

# 初期状態または計算の実行
if calc_button:
    # 人口分布データの準備（カスタム比率を使用する場合は置き換え）
    working_population_data = population_data.copy()
    
    if use_custom:
        for region, percentage in custom_distribution.items():
            working_population_data.loc[region, 'percentage'] = percentage
    
    # # デバッグ情報の表示（開発モード時のみ）
    # is_dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() in ("true", "1", "yes")
    # if is_dev_mode:
    #     with st.expander("送料データと選択したサイズ"):
    #         st.write("利用可能なサイズコード:", shipping_rates['size_code'].tolist())
    #         st.write("選択したサイズ分布:", size_distribution)
    #         st.dataframe(shipping_rates.head())
    
    # 地域別出荷数の計算
    shipments_result = calculate_regional_shipments(total_shipments, working_population_data)
    
    try:
        # 送料計算（複数サイズ対応）
        result, size_results = calculate_shipping_costs(shipments_result, shipping_rates, size_distribution)
        
        # 集計結果の計算
        summary = calculate_summary(result, size_results)
        
        # 結果を保存（セッションステートに格納）
        st.session_state.result = result
        st.session_state.size_results = size_results
        st.session_state.summary = summary
        st.session_state.size_distribution = size_distribution
        st.session_state.has_result = True
        
    except Exception as e:
        st.error(f"計算中にエラーが発生しました: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# 結果の表示（計算が実行された場合）
if 'has_result' in st.session_state and st.session_state.has_result:
    result = st.session_state.result
    size_results = st.session_state.size_results
    summary = st.session_state.summary
    size_distribution = st.session_state.size_distribution
    
    # 集計結果の表示
    st.subheader("シミュレーション結果")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総出荷個数", f"{summary['total_shipments']:,}個")
    with col2:
        st.metric("総送料", f"{summary['total_cost']:,.0f}円")
    with col3:
        st.metric("1個あたりの平均送料", f"{summary['average_cost']:.1f}円")
    
    # サイズ分布の情報表示
    st.subheader("サイズ別情報")
    
    size_info_list = []
    for info in summary['size_info']:
        size_info_list.append({
            "サイズ": f"{info['size_name']} ({info['weight']})",
            "割合": f"{info['proportion']*100:.1f}%",
            "出荷個数": f"{info['shipments']:,}個",
            "送料合計": f"{info['cost']:,.0f}円",
            "平均単価": f"{info['average_cost']:.1f}円"
        })
    
    size_info_df = pd.DataFrame(size_info_list)
    st.dataframe(size_info_df, use_container_width=True)
    
    # サイズ別詳細タブ
    tab_size = st.tabs(["サイズ別詳細"])
    
    with tab_size[0]:
        # サイズ別の詳細情報
        for i, size_result in enumerate(size_results):
            size_code = size_result['size_code'].iloc[0]
            size_name = size_result['size_name'].iloc[0]
            weight = size_result['weight'].iloc[0]
            proportion = size_result['proportion'].iloc[0]
            
            st.markdown(f"### {size_name} ({weight}) - {proportion*100:.1f}%")
            
            # DataFrameの整形
            size_display_df = size_result.reset_index()
            
            # カラム名を確認して適切に選択
            size_columns = size_display_df.columns.tolist()
            
            # # 開発モード時のみデバッグ情報を表示
            # is_dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() in ("true", "1", "yes")
            # if is_dev_mode:
            #     st.write("デバッグ - 利用可能なカラム:", size_columns)
            
            if 'region' in size_columns:
                region_col = 'region'
            else:
                region_col = size_columns[0]  # 最初のカラムがリージョン名と仮定
            
            selected_columns = [region_col]
            if 'prefectures' in size_columns:
                selected_columns.append('prefectures')
            if 'size_shipments' in size_columns:
                selected_columns.append('size_shipments')
            if 'rate' in size_columns:
                selected_columns.append('rate')
            if 'size_cost' in size_columns:
                selected_columns.append('size_cost')
            
            size_display_df = size_display_df[selected_columns]
            
            # カラム名を変更
            new_cols = ['地域']
            if 'prefectures' in selected_columns:
                new_cols.append('都道府県')
            if 'size_shipments' in selected_columns:
                new_cols.append('出荷個数')
            if 'rate' in selected_columns:
                new_cols.append('送料単価(円)')
            if 'size_cost' in selected_columns:
                new_cols.append('送料合計(円)')
            
            size_display_df.columns = new_cols
            
            # 表示用の書式設定
            st.dataframe(size_display_df, use_container_width=True)
            
            # # グラフ（出荷個数と送料合計を並べて表示）
            # col1, col2 = st.columns(2)
            
            # try:
            #     with col1:
            #         # リージョンカラムを使用
            #         size_df_reset = size_result.reset_index()
                    
            #         # 利用可能なカラム名を確認
            #         if region_col in size_df_reset.columns and 'size_shipments' in size_df_reset.columns:
            #             fig_size_1 = px.bar(
            #                 size_df_reset,
            #                 x=region_col,  # ここを'index'から変更
            #                 y='size_shipments',
            #                 title=f'{size_name} - 地域別出荷個数',
            #                 labels={region_col: '地域', 'size_shipments': '出荷個数'}
            #             )
            #             st.plotly_chart(fig_size_1, use_container_width=True)
                
            #     with col2:
            #         # リージョンカラムを使用
            #         if region_col in size_df_reset.columns and 'size_cost' in size_df_reset.columns:
            #             fig_size_2 = px.bar(
            #                 size_df_reset,
            #                 x=region_col,  # ここを'index'から変更
            #                 y='size_cost',
            #                 title=f'{size_name} - 地域別送料合計',
            #                 labels={region_col: '地域', 'size_cost': '送料合計(円)'}
            #             )
            #             st.plotly_chart(fig_size_2, use_container_width=True)
            # except Exception as e:
            #     if is_dev_mode:
            #         st.error(f"グラフ作成エラー: {str(e)}")
            #         st.write(f"カラム: {size_df_reset.columns.tolist() if 'size_df_reset' in locals() else '不明'}")
            
            st.markdown("---")
import pandas as pd
import numpy as np

def calculate_regional_shipments(total_shipments, population_data):
    """
    地域別の出荷数を人口分布に基づいて計算する
    
    Args:
        total_shipments (int): 全国総出荷個数
        population_data (DataFrame): 地域別人口データ
    
    Returns:
        DataFrame: 地域別の出荷数を含むデータフレーム
    """
    # 人口分布データをコピー
    result = population_data.copy()
    
    # 人口分布率に基づいて出荷数を計算
    result['shipments'] = (result['percentage'] * total_shipments).round().astype(int)
    
    # 丸め誤差による総数のずれを補正
    shipment_diff = total_shipments - result['shipments'].sum()
    if shipment_diff != 0:
        # 最も人口の多い地域に差分を追加（一般的には関東）
        max_pop_idx = result['population'].idxmax()
        result.loc[max_pop_idx, 'shipments'] += shipment_diff
    
    # インデックス名を明示的に設定
    result.index.name = 'region'
    
    return result

def calculate_shipping_costs(shipments_data, shipping_rates, size_distribution):
    """
    地域別の送料を計算する (複数サイズ対応)
    
    Args:
        shipments_data (DataFrame): 地域別出荷数データ
        shipping_rates (DataFrame): 送料データ
        size_distribution (dict): サイズコードと割合の辞書 (例: {'60': 0.5, '80': 0.3, '100': 0.2})
    
    Returns:
        tuple: (全体結果データフレーム, サイズ別結果データフレームのリスト)
    """
    # 結果データフレームを準備
    result = shipments_data.copy()
    result['rate'] = 0
    result['total_cost'] = 0
    
    # サイズごとの結果を格納するリスト
    size_results = []
    
    # 各サイズごとに計算
    for size_code, proportion in size_distribution.items():
        # 該当サイズの送料データを取得（データ型の問題を避けるため文字列として比較）
        size_code_str = str(size_code)
        size_rates_df = shipping_rates[shipping_rates['size_code'].astype(str) == size_code_str]
        
        # 対応するサイズが見つからない場合のエラーハンドリング
        if size_rates_df.empty:
            print(f"サイズコード '{size_code}' に対応する送料データが見つかりません。")
            print(f"使用可能なサイズコード: {shipping_rates['size_code'].tolist()}")
            # デフォルトの送料データを使用（最初の行）
            size_rates = shipping_rates.iloc[0]
        else:
            size_rates = size_rates_df.iloc[0]
            
        # デバッグ情報
        print(f"サイズ '{size_code}' の送料データ: {dict(size_rates)}")
        
        # このサイズの結果データフレーム
        size_result = shipments_data.copy()
        
        # このサイズの出荷数を計算
        size_result['size_shipments'] = (size_result['shipments'] * proportion).round().astype(int)
        
        # 地域別の送料単価を追加
        for region in size_result.index:
            size_result.loc[region, 'rate'] = size_rates[region]
        
        # 地域別の送料合計を計算
        size_result['size_cost'] = size_result['size_shipments'] * size_result['rate']
        
        # サイズ名と重量を追加
        size_result['size_name'] = size_rates['size_name']
        size_result['weight'] = size_rates['weight']
        size_result['size_code'] = size_code
        size_result['proportion'] = proportion
        
        # インデックス名を明示的に設定
        size_result.index.name = 'region'
        
        # 全体の結果に加算
        result['rate'] += size_result['rate'] * proportion
        result['total_cost'] += size_result['size_cost']
        
        # サイズごとの結果を保存
        size_results.append(size_result)
    
    return result, size_results

def calculate_summary(result_data, size_results=None):
    """
    送料計算の集計結果を生成する
    
    Args:
        result_data (DataFrame): 送料計算結果
        size_results (list, optional): サイズ別結果データフレームのリスト
    
    Returns:
        dict: 集計結果（総出荷数、総送料、平均送料、サイズ別情報）
    """
    total_shipments = result_data['shipments'].sum()
    total_cost = result_data['total_cost'].sum()
    average_cost = total_cost / total_shipments if total_shipments > 0 else 0
    
    summary = {
        'total_shipments': total_shipments,
        'total_cost': total_cost,
        'average_cost': average_cost
    }
    
    # サイズ別の情報を追加
    if size_results:
        size_info = []
        for size_df in size_results:
            size_code = size_df['size_code'].iloc[0]
            size_name = size_df['size_name'].iloc[0]
            weight = size_df['weight'].iloc[0]
            proportion = size_df['proportion'].iloc[0]
            size_shipments = size_df['size_shipments'].sum()
            size_cost = size_df['size_cost'].sum()
            size_average_cost = size_cost / size_shipments if size_shipments > 0 else 0
            
            size_info.append({
                'size_code': size_code,
                'size_name': size_name,
                'weight': weight,
                'proportion': proportion,
                'shipments': size_shipments,
                'cost': size_cost,
                'average_cost': size_average_cost
            })
        
        summary['size_info'] = size_info
    
    return summary
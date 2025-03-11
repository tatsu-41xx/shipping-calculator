import os
import pandas as pd

def load_shipping_rates():
    """
    送料データをCSVファイルから読み込む。実データが見つからない場合はサンプルデータを使用する。
    
    Returns:
        DataFrame: 送料データ
    """
    # 実データとサンプルデータのパス
    real_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shipping_rates.csv'),
        os.path.join('data', 'shipping_rates.csv'),
        'shipping_rates.csv'
    ]
    
    sample_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shipping_rates_sample.csv'),
        os.path.join('data', 'shipping_rates_sample.csv'),
        'shipping_rates_sample.csv'
    ]
    
    # 実データの読み込みを試行
    for file_path in real_paths:
        try:
            if os.path.exists(file_path):
                shipping_rates = pd.read_csv(file_path)
                print(f"送料データを読み込みました: {file_path}")
                return shipping_rates
        except Exception as e:
            print(f"{file_path}からの読み込みに失敗: {e}")
    
    # サンプルデータの読み込みを試行
    for file_path in sample_paths:
        try:
            if os.path.exists(file_path):
                shipping_rates = pd.read_csv(file_path)
                print(f"サンプル送料データを読み込みました: {file_path}")
                return shipping_rates
        except Exception as e:
            print(f"{file_path}からの読み込みに失敗: {e}")
    
    print("送料データの読み込みに失敗しました。ダミーデータを使用します。")
    # すべてのパスが失敗した場合はダミーデータを返す
    return create_dummy_shipping_rates()

def load_population_data():
    """
    地域別人口データをCSVファイルから読み込む
    
    Returns:
        DataFrame: 地域別人口データ（indexを地域名に設定）
    """
    # 人口データのパス
    potential_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'population_data.csv'),
        os.path.join('data', 'population_data.csv'),
        'population_data.csv',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'population_data_sample.csv'),
        os.path.join('data', 'population_data_sample.csv'),
        'population_data_sample.csv'
    ]
    
    # データの読み込みを試行
    for file_path in potential_paths:
        try:
            if os.path.exists(file_path):
                population_data = pd.read_csv(file_path)
                # 地域名をインデックスに設定し、インデックス名も明示的に設定
                population_data = population_data.set_index('region')
                population_data.index.name = 'region'  # インデックス名を明示的に設定
                print(f"人口データを読み込みました: {file_path}")
                return population_data
        except Exception as e:
            print(f"{file_path}からの読み込みに失敗: {e}")
    
    print("人口データの読み込みに失敗しました。ダミーデータを使用します。")
    # すべてのパスが失敗した場合はダミーデータを返す
    return create_dummy_population_data()

def create_dummy_shipping_rates():
    """
    ダミーの送料データを作成（データ読み込みに失敗した場合のフォールバック）
    """
    regions = ['北海道', '北東北', '南東北', '関東', '信越', '北陸', '中部', '関西', '中国', '四国', '九州', '沖縄']
    sizes = [
        {'size_code': '60', 'size_name': '60cm以内', 'weight': '2kg以内'},
        {'size_code': '80', 'size_name': '80cm以内', 'weight': '5kg以内'},
        {'size_code': '100', 'size_name': '100cm以内', 'weight': '10kg以内'},
        {'size_code': '120', 'size_name': '120cm以内', 'weight': '15kg以内'},
        {'size_code': '140', 'size_name': '140cm以内', 'weight': '20kg以内'},
        {'size_code': '160', 'size_name': '160cm以内', 'weight': '25kg以内'},
        {'size_code': '180', 'size_name': '180cm以内', 'weight': '30kg以内'},
        {'size_code': 'compact', 'size_name': 'コンパクト', 'weight': 'なし'},
        {'size_code': 'yupacket', 'size_name': 'ゆうパケット', 'weight': '1kg以内'},
    ]
    
    # ダミーデータフレームの作成
    data = []
    for size in sizes:
        row = size.copy()
        # 適当な送料を各地域に設定
        for region in regions:
            if size['size_code'] == 'yupacket':
                row[region] = 250
            else:
                # サイズに応じた送料を設定
                base_rate = int(size['size_code']) * 10 if size['size_code'].isdigit() else 500
                if region == '北海道':
                    row[region] = base_rate * 2
                elif region == '沖縄':
                    row[region] = base_rate * 3
                else:
                    row[region] = base_rate
        data.append(row)
    
    return pd.DataFrame(data)

def create_dummy_population_data():
    """
    ダミーの人口分布データを作成（データ読み込みに失敗した場合のフォールバック）
    """
    regions = ['北海道', '北東北', '南東北', '関東', '信越', '北陸', '中部', '関西', '中国', '四国', '九州', '沖縄']
    
    # 適当な人口と分布率を設定
    data = {
        'population': [5000000, 4000000, 9000000, 43000000, 4500000, 3000000, 15000000, 20000000, 7300000, 3700000, 13000000, 1500000],
        'percentage': [0.04, 0.03, 0.07, 0.34, 0.04, 0.02, 0.12, 0.16, 0.06, 0.03, 0.10, 0.01],
        'prefectures': [
            '北海道',
            '青森・岩手・秋田',
            '宮城・山形・福島',
            '東京・神奈川・埼玉・千葉・茨城・栃木・群馬',
            '新潟・長野',
            '富山・石川・福井',
            '愛知・岐阜・静岡・三重',
            '大阪・京都・兵庫・奈良・和歌山・滋賀',
            '鳥取・島根・岡山・広島・山口',
            '徳島・香川・愛媛・高知',
            '福岡・佐賀・長崎・熊本・大分・宮崎・鹿児島',
            '沖縄'
        ]
    }
    
    df = pd.DataFrame(data, index=regions)
    # インデックス名を明示的に指定
    df.index.name = 'region'
    return df
import pandas as pd
import json

# 讀取 CSV 檔案
file_path = 'ELog_Stastic.csv'
data = pd.read_csv(file_path)

# 轉換日期格式
data['Date'] = pd.to_datetime(data['Date'])

# 轉換資料格式
data_melted = data.melt(id_vars='Date', var_name='Device Name', value_name='Energy Consumption (kWh)')
daily_consumption = data_melted.groupby(['Date', 'Device Name'])['Energy Consumption (kWh)'].sum().reset_index()

# 產生 JSON
devices_data = {
    device: daily_consumption[daily_consumption['Device Name'] == device]
    .assign(Date=daily_consumption[daily_consumption['Device Name'] == device]['Date'].dt.strftime('%Y-%m-%d'))
    .to_dict(orient='records')
    for device in daily_consumption['Device Name'].unique()
}

# 存成 JSON 檔案
with open("devices_data.json", "w", encoding="utf-8") as f:
    json.dump(devices_data, f, ensure_ascii=False, indent=4)

print("JSON 檔案已成功生成！")

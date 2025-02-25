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

with open("devices_data.json", "w", encoding="utf-8") as f:
    json.dump(devices_data, f, ensure_ascii=False, indent=4)

# 產生 HTML
html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>Device Power Consumption Trend</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; }}
        .container {{ margin: 20px; padding: 20px; text-align: center; }}
        #chart {{ height: 500px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>📊 Device Power Consumption Trend</h2>
        <div id="chart"></div>
    </div>
    <script>
        let devices = {json.dumps(devices_data, ensure_ascii=False)};

        let traces = [];
        for (let device in devices) {{
            traces.push({{
                x: devices[device].map(d => d["Date"]),
                y: devices[device].map(d => d["Energy Consumption (kWh)"]),
                mode: 'lines',
                name: device
            }});
        }}

        Plotly.newPlot('chart', traces, {{
            title: '📈 Daily Power Consumption',
            xaxis: {{ title: 'Date' }},
            yaxis: {{ title: 'Energy Consumption (kWh)' }}
        }});
    </script>
</body>
</html>
"""

with open("power_consumption.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("JSON & HTML 檔案已成功生成！")

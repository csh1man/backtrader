import sys
import pandas as pd
import quantstats as qs

# Check if the correct number of command-line arguments are provided.
if len(sys.argv) < 3:
    print("Usage: python create_report.py <input_csv_path> <output_html_path>")
    sys.exit(1)

# Get file paths from command-line arguments.
input_csv = sys.argv[1]
output_html = sys.argv[2]
date_start = None
date_end = None
report_title = "Janus Backtest Report"

if len(sys.argv) >= 4 and sys.argv[3] and sys.argv[3].lower() != "null":
    date_start = sys.argv[3]

if len(sys.argv) >= 5and sys.argv[4] and sys.argv[4].lower() != "null":
    date_end = sys.argv[4]

print(f"Reading equity curve from: {input_csv}")
print(f"Saving QuantStats report to: {output_html}")
print(f"Filtering date range: from [{date_start or 'Start'}] to [{date_end or 'End'}]")

# 4. CSV 파일을 불러옵니다.
try:
    equity_df = pd.read_csv(input_csv, index_col='date', parse_dates=True)
except Exception as e:
    print(f"Error reading CSV file: {e}")
    sys.exit(1)

# 5. .loc 슬라이싱을 사용하여 DataFrame을 필터링합니다.
# .loc는 None을 '처음부터' 또는 '끝까지'로 완벽하게 이해합니다.
try:
    equity_df = equity_df.loc[date_start:date_end]
    if equity_df.empty:
        print("Warning: No data found in the specified date range.")
        sys.exit(1)
except Exception as e:
    print(f"Error during date filtering (check your date formats, e.g., 'YYYY-MM-DD'): {e}")
    sys.exit(1)

# 6. 필터링된 데이터로 리포트를 생성합니다.
qs.reports.html(equity_df['value'], output=output_html, title=report_title)

print("Report generation complete.")
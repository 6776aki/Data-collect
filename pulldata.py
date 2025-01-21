import requests
import csv
import os
from datetime import datetime, timedelta
import argparse

def fetch_binance_kline(symbol, interval, limit=1000, start_time=None, end_time=None):
    base_url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit  # Maximum 1000 candlesticks per request
    }
    if start_time:
        params["startTime"] = int(start_time.timestamp() * 1000)  # Convert to milliseconds
    if end_time:
        params["endTime"] = int(end_time.timestamp() * 1000)  # Convert to milliseconds

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def save_to_csv(data, filename):
    # Define headers for the data
    headers = [
        "Open Time", "Open", "High", "Low", "Close", 
        "Volume", "Close Time", "Number of Trades"
    ]

    # Check if the file already exists
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write headers only if the file doesn't exist
        if not file_exists:
            writer.writerow(headers)

        for row in data:
            # Convert Open Time and Close Time
            open_time_human = datetime.utcfromtimestamp(row[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            close_time_human = datetime.utcfromtimestamp(row[6] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            # Write the cleaned row with human-readable times
            writer.writerow([
                open_time_human, row[1], row[2], row[3], row[4], 
                row[5], close_time_human, row[8]
            ])
def main(fromDate, toDate):
    today = datetime.now().date()
    symbol = "WIFUSDT"  # Replace with your desired trading pair
    interval_num = 1  # Number for interval
    symbol_time = "h"  # Time unit: "d" for days, "h" for hours, "m" for minutes
    filename = f"{today}_{symbol}_{interval_num}{symbol_time}_data.csv"  # Output CSV file name

    # Map time symbols to their equivalent conversion factors
    time_conversions = {"d": 1, "h": 24, "m": 1440}

    def convert_to_seconds(interval_num, symbol):
        if symbol == "m":
            return interval_num * 60
        elif symbol == "h":
            return interval_num * 3600
        elif symbol == "d":
            return interval_num * 24 * 3600
        else:
            return None

    if symbol_time not in time_conversions:
        print(f"Invalid time unit: {symbol_time}. Use 'd', 'h', or 'm'.")
        return

    def time_period(from_date, to_date):
        try:
            frmDate = datetime.strptime(from_date, "%Y/%m/%d %H:%M:%S")
            toDate = datetime.strptime(to_date, "%Y/%m/%d %H:%M:%S")

            duration = (toDate - frmDate).total_seconds()

            return duration, frmDate, toDate
        except Exception as e:
            print(e)
            return None, None, None

    def match_duration_with_interval_symbol(duration, symbol):
        if symbol == "m":
            i = duration / 60
            if i < 1:
                print("Time frame is larger than the time period.")
                return
            else:
                return i
        elif symbol == "h":
            i = duration / 3600
            if i < 1:
                print("Time frame is larger than the time period.")
                return
            else:
                return i
        elif symbol == "d":
            i = duration / 86400
            if i < 1:
                print("Time frame is larger than the time period.")
                return
            else:
                return i
        else:
            return None

    def candle_count(duration, interval):
        count = duration / interval
        if count < 1:
            print("Candle count is less than 1.")
            return
        else:
            return count

    maximumCandles = 1000
    duration, from_date, to_date = time_period(fromDate, toDate)
    totalCandles = candle_count(match_duration_with_interval_symbol(duration, symbol_time), interval_num)

    if totalCandles > maximumCandles:
        maximumDurationCandlesCanBeFetched = interval_num * 1000
        maximumDateCandlesCanFetched = from_date + timedelta(seconds=convert_to_seconds(maximumDurationCandlesCanBeFetched, symbol_time))

        while from_date < to_date:
            try:
                if maximumDateCandlesCanFetched > to_date:
                    maximumDateCandlesCanFetched = to_date  # Adjust for the last chunk

                print(f"Fetching data from: {from_date} to: {maximumDateCandlesCanFetched}")
                interval = f"{interval_num}{symbol_time}"
                data = fetch_binance_kline(symbol, interval, start_time=from_date, end_time=maximumDateCandlesCanFetched)
                save_to_csv(data, filename)
                
                # Update the start date for the next chunk
                from_date = maximumDateCandlesCanFetched
                maximumDateCandlesCanFetched += timedelta(seconds=convert_to_seconds(maximumDurationCandlesCanBeFetched, symbol_time))
            except Exception as e:
                print(e)
    else:
        try:
            print(f"Fetching data from: {from_date} to: {to_date}")
            interval = f"{interval_num}{symbol_time}"
            data = fetch_binance_kline(symbol, interval, start_time=from_date, end_time=to_date)
            save_to_csv(data, filename)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')
    parser.add_argument('frm_date',help="dateformate:2024/01/01 01:01:01")
    parser.add_argument('to_date',help="dateformate:2024/01/01 01:01:01")
    args = parser.parse_args()

    main(args.frm_date,args.to_date)
 

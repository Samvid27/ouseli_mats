import statistics
from datetime import datetime, timedelta

def analyze_fraud_risk(transactions, current_amount):
    """
    Simple Statistical Anomaly Detection.
    Flags 'True' if current amount is > Mean + (3 * StdDev).
    """
    if not transactions or len(transactions) < 5:
        return False # Not enough data to be sure
        
    amounts = [float(t['amount']) for t in transactions]
    mean = statistics.mean(amounts)
    
    # Need at least 2 points for stdev
    if len(amounts) > 1:
        stdev = statistics.stdev(amounts)
    else:
        stdev = 0
        
    threshold = mean + (3 * stdev)
    
    return current_amount > threshold

def predict_balance_trend(history, days=7):
    """
    Simple Linear Regression for balance prediction using pure Python.
    history: list of {date: datetime, balance: float}
    """
    if not history or len(history) < 2:
        return []
        
    # Prepare data for regression
    # X = days from start, Y = balance
    start_date = min(h['date'] for h in history)
    X = [(h['date'] - start_date).days for h in history]
    Y = [h['balance'] for h in history]
    
    # Calculate Linear Regression: y = mx + c
    n = len(X)
    sum_x = sum(X)
    sum_y = sum(Y)
    sum_xx = sum(x*x for x in X)
    sum_xy = sum(x*y for x, y in zip(X, Y))
    
    denominator = (n * sum_xx - sum_x**2)
    if denominator == 0:
        return []
        
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    predictions = []
    last_day = max(X)
    last_date = max(h['date'] for h in history)
    
    for i in range(1, days + 1):
        future_day = last_day + i
        pred_val = slope * future_day + intercept
        future_date = last_date + timedelta(days=i)
        predictions.append({
            "date": future_date.strftime('%Y-%m-%d'),
            "predicted_balance": round(max(0, float(pred_val)), 2)
        })
        
    return predictions

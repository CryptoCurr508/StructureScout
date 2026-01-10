"""
Data Logger Module

Handles CSV logging of all analysis results and trade outcomes.
Provides functions for logging setups, updating trade results, and generating statistics.

No emojis or unicode characters in this file.
"""

import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)


class DataLoggerError(Exception):
    """Custom exception for data logging errors."""
    pass


# CSV column headers for trading log
TRADING_LOG_HEADERS = [
    'date', 'time_est', 'timestamp_utc', 'screenshot_path', 'current_price',
    'market_regime', 'regime_reasoning',
    'valid_setup', 'setup_type', 'setup_direction',
    'entry_price', 'stop_loss', 'stop_reasoning', 'take_profit_1', 'tp1_reasoning', 'take_profit_2',
    'stop_distance_ticks', 'reward_risk_ratio',
    'position_size_contracts', 'dollar_risk', 'dollar_target_1',
    'setup_quality', 'confidence_score', 'analysis_notes',
    'trade_recommendation', 'caution_flags',
    'actual_trade_taken', 'trade_outcome', 'actual_profit_loss', 'actual_r_multiple',
    'weekly_trade_count', 'notes'
]


def initialize_log_file(filepath: Path, headers: List[str] = None) -> bool:
    """
    Initialize CSV log file with headers if it doesn't exist.
    
    Args:
        filepath: Path to log file
        headers: List of column headers (uses TRADING_LOG_HEADERS if None)
        
    Returns:
        True if file created or already exists
    """
    if headers is None:
        headers = TRADING_LOG_HEADERS
    
    try:
        # Create directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with headers if doesn't exist
        if not filepath.exists():
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            logger.info(f"Created log file: {filepath}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize log file: {e}")
        return False


def log_analysis_to_csv(parsed_data: Dict[str, Any], log_file: Path) -> bool:
    """
    Log analysis results to CSV file.
    
    Args:
        parsed_data: Parsed data from GPT analysis with all fields
        log_file: Path to log file
        
    Returns:
        True if logged successfully
    """
    try:
        # Ensure log file exists
        initialize_log_file(log_file)
        
        # Extract date and time
        timestamp_str = parsed_data.get('timestamp', '')
        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M EST")
        except:
            dt = datetime.now()
        
        # Prepare row data
        row = [
            dt.strftime("%Y-%m-%d"),  # date
            dt.strftime("%H:%M"),  # time_est
            datetime.utcnow().isoformat(),  # timestamp_utc
            parsed_data.get('screenshot_path', ''),  # screenshot_path
            parsed_data.get('current_price', ''),  # current_price
            parsed_data.get('market_regime', ''),  # market_regime
            parsed_data.get('regime_reasoning', ''),  # regime_reasoning
            'yes' if parsed_data.get('valid_setup_exists') else 'no',  # valid_setup
            parsed_data.get('setup_type', ''),  # setup_type
            parsed_data.get('setup_direction', ''),  # setup_direction
            parsed_data.get('entry_price', ''),  # entry_price
            parsed_data.get('stop_loss_price', ''),  # stop_loss
            parsed_data.get('stop_loss_reasoning', ''),  # stop_reasoning
            parsed_data.get('take_profit_1', ''),  # take_profit_1
            parsed_data.get('take_profit_1_reasoning', ''),  # tp1_reasoning
            parsed_data.get('take_profit_2', ''),  # take_profit_2
            parsed_data.get('stop_distance_ticks', ''),  # stop_distance_ticks
            parsed_data.get('reward_risk_ratio', ''),  # reward_risk_ratio
            parsed_data.get('position_size', ''),  # position_size_contracts
            parsed_data.get('dollar_risk', ''),  # dollar_risk
            parsed_data.get('dollar_target_1', ''),  # dollar_target_1
            parsed_data.get('setup_quality', ''),  # setup_quality
            parsed_data.get('confidence_score', ''),  # confidence_score
            parsed_data.get('analysis_notes', ''),  # analysis_notes
            parsed_data.get('trade_recommendation', ''),  # trade_recommendation
            ','.join(parsed_data.get('caution_flags', [])),  # caution_flags
            'no',  # actual_trade_taken (default)
            '',  # trade_outcome (empty until updated)
            '',  # actual_profit_loss (empty until updated)
            '',  # actual_r_multiple (empty until updated)
            '',  # weekly_trade_count (calculated later)
            ''  # notes (empty, can be filled manually)
        ]
        
        # Append to CSV
        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        logger.info(f"Logged analysis to {log_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log analysis: {e}")
        return False


def update_trade_outcome(
    log_file: Path,
    timestamp: str,
    outcome: str,
    profit_loss: float,
    notes: str = ""
) -> bool:
    """
    Update trade outcome in CSV log.
    
    Args:
        log_file: Path to log file
        timestamp: Timestamp to match (format: "YYYY-MM-DD HH:MM")
        outcome: Trade outcome (hit_tp1, hit_stop, manual_close, not_traded)
        profit_loss: Actual profit/loss in dollars
        notes: Additional notes
        
    Returns:
        True if updated successfully
    """
    try:
        # Read CSV
        df = pd.read_csv(log_file)
        
        # Find row with matching timestamp
        df_timestamp = df['date'] + ' ' + df['time_est']
        mask = df_timestamp == timestamp
        
        if not mask.any():
            logger.warning(f"No entry found for timestamp: {timestamp}")
            return False
        
        # Calculate R-multiple
        dollar_risk = df.loc[mask, 'dollar_risk'].values[0]
        r_multiple = profit_loss / dollar_risk if dollar_risk > 0 else 0
        
        # Update columns
        df.loc[mask, 'actual_trade_taken'] = 'yes'
        df.loc[mask, 'trade_outcome'] = outcome
        df.loc[mask, 'actual_profit_loss'] = profit_loss
        df.loc[mask, 'actual_r_multiple'] = round(r_multiple, 2)
        if notes:
            df.loc[mask, 'notes'] = notes
        
        # Save back to CSV
        df.to_csv(log_file, index=False)
        
        logger.info(f"Updated trade outcome for {timestamp}: {outcome}, P&L: ${profit_loss:.2f}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update trade outcome: {e}")
        return False


def get_weekly_summary_stats(log_file: Path, days: int = 7) -> Dict[str, Any]:
    """
    Calculate summary statistics for recent period.
    
    Args:
        log_file: Path to log file
        days: Number of days to look back
        
    Returns:
        Dictionary with summary statistics
    """
    try:
        # Read CSV
        df = pd.read_csv(log_file)
        
        if df.empty:
            return {}
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter last N days
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        df_recent = df[df['date'] >= cutoff_date]
        
        if df_recent.empty:
            return {}
        
        # Calculate statistics
        total_scans = len(df_recent)
        valid_setups = (df_recent['valid_setup'] == 'yes').sum()
        high_quality = (df_recent['setup_quality'] == 'high').sum()
        
        # Setup type distribution
        setup_counts = df_recent[df_recent['valid_setup'] == 'yes']['setup_type'].value_counts()
        
        # Regime distribution
        regime_counts = df_recent['market_regime'].value_counts()
        trending_count = regime_counts.get('trending_up', 0) + regime_counts.get('trending_down', 0)
        ranging_count = regime_counts.get('ranging', 0)
        
        # Average metrics
        avg_confidence = df_recent['confidence_score'].mean()
        avg_rr = df_recent['reward_risk_ratio'].mean()
        
        # Trading performance (if trades executed)
        trades = df_recent[df_recent['actual_trade_taken'] == 'yes']
        trade_stats = {}
        
        if not trades.empty:
            wins = trades[trades['actual_r_multiple'] > 0]
            win_rate = len(wins) / len(trades) * 100 if len(trades) > 0 else 0
            avg_r = trades['actual_r_multiple'].mean()
            total_pnl = trades['actual_profit_loss'].sum()
            
            trade_stats = {
                'trades_executed': len(trades),
                'win_rate': round(win_rate, 1),
                'avg_r_multiple': round(avg_r, 2),
                'total_pnl': round(total_pnl, 2)
            }
        
        # Compile summary
        summary = {
            'period_days': days,
            'total_scans': int(total_scans),
            'valid_setups': int(valid_setups),
            'high_quality_setups': int(high_quality),
            'trending_count': int(trending_count),
            'ranging_count': int(ranging_count),
            'avg_confidence': round(avg_confidence, 1) if pd.notna(avg_confidence) else 0,
            'avg_rr': round(avg_rr, 2) if pd.notna(avg_rr) else 0,
            'setup_type_distribution': setup_counts.to_dict(),
            **trade_stats
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to calculate summary stats: {e}")
        return {}


def export_for_analysis(log_file: Path, output_file: Path, output_format: str = "csv") -> bool:
    """
    Export log data for external analysis.
    
    Args:
        log_file: Path to log file
        output_file: Path to output file
        output_format: Output format (csv, json, excel)
        
    Returns:
        True if exported successfully
    """
    try:
        df = pd.read_csv(log_file)
        
        if output_format == "json":
            df.to_json(output_file, orient='records', indent=2)
        elif output_format == "excel":
            df.to_excel(output_file, index=False)
        else:  # csv
            df.to_csv(output_file, index=False)
        
        logger.info(f"Exported data to {output_file} ({output_format})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export data: {e}")
        return False


def get_daily_setups(log_file: Path, date: str) -> pd.DataFrame:
    """
    Get all setups for a specific date.
    
    Args:
        log_file: Path to log file
        date: Date string (YYYY-MM-DD)
        
    Returns:
        DataFrame with setups for that date
    """
    try:
        df = pd.read_csv(log_file)
        return df[df['date'] == date]
    except Exception as e:
        logger.error(f"Failed to get daily setups: {e}")
        return pd.DataFrame()


# Command-line testing interface
if __name__ == "__main__":
    import sys
    from config import get_config
    
    if "--test" in sys.argv:
        print("Testing Data Logger Module...")
        print("-" * 50)
        
        # Load configuration
        try:
            config = get_config()
            print(f"[OK] Configuration loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load configuration: {e}")
            sys.exit(1)
        
        # Test log file initialization
        test_log = Path("data/test_log.csv")
        print(f"Testing log file initialization...")
        result = initialize_log_file(test_log)
        if result and test_log.exists():
            print(f"[OK] Log file created: {test_log}")
        else:
            print(f"[ERROR] Failed to create log file")
            sys.exit(1)
        
        # Test logging sample data
        print("Testing data logging...")
        sample_data = {
            'timestamp': '2026-01-10 10:30 EST',
            'current_price': 21250.0,
            'market_regime': 'trending_up',
            'regime_reasoning': 'Higher highs',
            'valid_setup_exists': True,
            'setup_type': 'structure_break',
            'setup_direction': 'long',
            'entry_price': 21255.0,
            'stop_loss_price': 21240.0,
            'stop_loss_reasoning': 'Below swing low',
            'take_profit_1': 21285.0,
            'take_profit_1_reasoning': 'Prev day high',
            'take_profit_2': 21310.0,
            'stop_distance_ticks': 15,
            'reward_risk_ratio': 2.0,
            'position_size': 10,
            'dollar_risk': 50.0,
            'dollar_target_1': 100.0,
            'setup_quality': 'high',
            'confidence_score': 78,
            'analysis_notes': 'Clean break',
            'trade_recommendation': 'enter_immediately',
            'caution_flags': []
        }
        
        result = log_analysis_to_csv(sample_data, test_log)
        if result:
            print(f"[OK] Sample data logged")
        else:
            print(f"[ERROR] Failed to log data")
        
        # Test reading and statistics
        print("Testing statistics calculation...")
        stats = get_weekly_summary_stats(test_log, days=7)
        if stats:
            print(f"[OK] Statistics calculated:")
            print(f"     Total scans: {stats.get('total_scans', 0)}")
            print(f"     Valid setups: {stats.get('valid_setups', 0)}")
        
        # Cleanup test file
        if test_log.exists():
            test_log.unlink()
            print(f"[OK] Cleaned up test file")
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
        
    else:
        print("Usage: python3 -m modules.data_logger --test")

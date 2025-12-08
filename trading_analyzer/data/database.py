"""
SQLite Database Manager
Handles historical scan results, watchlists, and performance tracking
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from ..core.scanner import ScanResult


# Database location
DB_FILE = Path.home() / 'Documents' / 'trading_analyzer.db'


class DatabaseManager:
    """
    SQLite database manager for historical tracking

    Tables:
    - scan_results: Individual scan results with all metrics
    - scan_history: Metadata about each scan run
    - watchlist: User-curated tickers to monitor
    - alerts: Custom alert conditions
    - performance: Track actual performance of signaled stocks
    """

    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self._ensure_database_exists()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Scan results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_date DATE NOT NULL,
                    scan_time TIMESTAMP NOT NULL,
                    scan_type TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    price REAL,
                    score INTEGER,
                    rel_vol REAL,
                    float_m REAL,
                    change_pct REAL,
                    week_change REAL,
                    volume INTEGER,
                    market_cap INTEGER,
                    exchange TEXT,
                    source TEXT,
                    catalyst TEXT,
                    description TEXT,
                    raw_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Pressure Cooker specific results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pressure_cooker_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_result_id INTEGER,
                    short_percent REAL,
                    days_to_cover REAL,
                    has_reverse_split BOOLEAN,
                    consecutive_volume_days INTEGER,
                    breaking_20d_high BOOLEAN,
                    setup_quality TEXT,
                    grade TEXT,
                    FOREIGN KEY (scan_result_id) REFERENCES scan_results(id)
                )
            """)

            # Dark Flow specific results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dark_flow_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_result_id INTEGER,
                    dark_flow_score INTEGER,
                    bias TEXT,
                    key_levels TEXT,
                    signals TEXT,
                    FOREIGN KEY (scan_result_id) REFERENCES scan_results(id)
                )
            """)

            # Scan history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_date DATE NOT NULL,
                    scan_time TIMESTAMP NOT NULL,
                    scan_type TEXT NOT NULL,
                    scan_mode TEXT,
                    market_choice TEXT,
                    total_candidates INTEGER,
                    total_found INTEGER,
                    min_price REAL,
                    max_price REAL,
                    criteria TEXT,
                    duration_seconds REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Watchlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT UNIQUE NOT NULL,
                    added_date DATE NOT NULL,
                    first_signal_date DATE,
                    first_scan_type TEXT,
                    first_score INTEGER,
                    current_score INTEGER,
                    highest_score INTEGER,
                    times_appeared INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'watching',
                    notes TEXT,
                    last_seen DATE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_name TEXT NOT NULL,
                    scan_type TEXT,
                    ticker TEXT,
                    condition_type TEXT NOT NULL,
                    condition_value REAL,
                    notification_type TEXT DEFAULT 'desktop',
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_count INTEGER DEFAULT 0,
                    last_triggered TIMESTAMP
                )
            """)

            # Migrate existing tables (add missing columns)
            self._migrate_schema(cursor)

            # Performance tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_result_id INTEGER,
                    ticker TEXT NOT NULL,
                    signal_date DATE NOT NULL,
                    signal_price REAL NOT NULL,
                    signal_score INTEGER,
                    scan_type TEXT,
                    price_1d REAL,
                    price_3d REAL,
                    price_7d REAL,
                    price_30d REAL,
                    return_1d REAL,
                    return_3d REAL,
                    return_7d REAL,
                    return_30d REAL,
                    max_gain_pct REAL,
                    max_loss_pct REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_result_id) REFERENCES scan_results(id)
                )
            """)

            # Indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_results_date ON scan_results(scan_date DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_results_ticker ON scan_results(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_results_type ON scan_results(scan_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_results_score ON scan_results(score DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_date ON scan_history(scan_date DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_ticker ON watchlist(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_status ON watchlist(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_ticker ON performance_tracking(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_tracking(signal_date DESC)")

    def _migrate_schema(self, cursor):
        """Migrate database schema to add missing columns"""
        # Check if watchlist.last_seen exists
        cursor.execute("PRAGMA table_info(watchlist)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'last_seen' not in columns:
            print("📊 Migrating database: Adding 'last_seen' column to watchlist...")
            cursor.execute("ALTER TABLE watchlist ADD COLUMN last_seen DATE")
            print("   ✅ Migration complete")

    # ========== SCAN RESULTS ==========

    def save_scan_results(self, results: List[ScanResult], scan_type: str,
                          scan_metadata: Optional[Dict] = None) -> int:
        """
        Save scan results to database

        Args:
            results: List of scan results
            scan_type: Type of scan (momentum, dark_flow, pressure_cooker)
            scan_metadata: Additional metadata about the scan

        Returns:
            Number of results saved
        """
        if not results:
            return 0

        now = datetime.now()
        scan_date = now.date().isoformat()
        scan_time = now.isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Save scan history
            if scan_metadata:
                cursor.execute("""
                    INSERT INTO scan_history
                    (scan_date, scan_time, scan_type, scan_mode, market_choice,
                     total_candidates, total_found, min_price, max_price,
                     criteria, duration_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_date,
                    scan_time,
                    scan_type,
                    scan_metadata.get('scan_mode'),
                    scan_metadata.get('market_choice'),
                    scan_metadata.get('total_candidates', 0),
                    len(results),
                    scan_metadata.get('min_price'),
                    scan_metadata.get('max_price'),
                    json.dumps(scan_metadata.get('criteria', {})),
                    scan_metadata.get('duration_seconds')
                ))

            # Save individual results
            saved_count = 0
            for result in results:
                cursor.execute("""
                    INSERT INTO scan_results
                    (scan_date, scan_time, scan_type, ticker, price, score,
                     rel_vol, float_m, change_pct, week_change, volume,
                     market_cap, exchange, source, catalyst, description, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_date,
                    scan_time,
                    scan_type,
                    result.ticker,
                    result.price,
                    result.score,
                    result.rel_vol,
                    result.float_m,
                    result.change_pct,
                    getattr(result, 'week_change', None),
                    result.volume,
                    result.market_cap,
                    result.exchange,
                    result.source,
                    result.catalyst,
                    result.description,
                    json.dumps(result.__dict__)
                ))

                scan_result_id = cursor.lastrowid

                # Save scanner-specific data
                if scan_type == 'pressure_cooker' and hasattr(result, 'short_percent'):
                    cursor.execute("""
                        INSERT INTO pressure_cooker_results
                        (scan_result_id, short_percent, days_to_cover,
                         has_reverse_split, consecutive_volume_days,
                         breaking_20d_high, setup_quality, grade)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        scan_result_id,
                        getattr(result, 'short_percent', 0),
                        getattr(result, 'days_to_cover', 0),
                        getattr(result, 'has_reverse_split', False),
                        getattr(result, 'consecutive_volume_days', 0),
                        getattr(result, 'breaking_20d_high', False),
                        getattr(result, 'setup_quality', ''),
                        getattr(result, 'grade', '')
                    ))

                elif scan_type == 'dark_flow' and hasattr(result, 'dark_flow_score'):
                    cursor.execute("""
                        INSERT INTO dark_flow_results
                        (scan_result_id, dark_flow_score, bias, key_levels, signals)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        scan_result_id,
                        getattr(result, 'dark_flow_score', 0),
                        getattr(result, 'bias', ''),
                        json.dumps(getattr(result, 'key_levels', [])),
                        json.dumps(getattr(result, 'signals', []))
                    ))

                # Update watchlist if ticker exists
                self._update_watchlist_from_result(cursor, result, scan_type, scan_date)

                saved_count += 1

            return saved_count

    def get_recent_results(self, scan_type: Optional[str] = None,
                          days: int = 7, min_score: Optional[int] = None) -> List[Dict]:
        """Get recent scan results"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT * FROM scan_results
                WHERE scan_date >= date('now', '-{} days')
            """.format(days)

            params = []
            if scan_type:
                query += " AND scan_type = ?"
                params.append(scan_type)

            if min_score is not None:
                query += " AND score >= ?"
                params.append(min_score)

            query += " ORDER BY scan_date DESC, score DESC"

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_ticker_history(self, ticker: str, days: int = 90) -> List[Dict]:
        """Get all historical scans for a specific ticker"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM scan_results
                WHERE ticker = ? AND scan_date >= date('now', '-{} days')
                ORDER BY scan_date DESC
            """.format(days), (ticker,))

            return [dict(row) for row in cursor.fetchall()]

    # ========== WATCHLIST ==========

    def _update_watchlist_from_result(self, cursor, result: ScanResult,
                                      scan_type: str, scan_date: str):
        """Internal: Update watchlist when ticker appears in scan"""
        # Check if ticker is on watchlist
        cursor.execute("SELECT * FROM watchlist WHERE ticker = ?", (result.ticker,))
        existing = cursor.fetchone()

        if existing:
            # Update existing entry
            new_highest = max(existing['highest_score'], result.score)
            cursor.execute("""
                UPDATE watchlist
                SET current_score = ?,
                    highest_score = ?,
                    times_appeared = times_appeared + 1,
                    last_seen = ?,
                    last_updated = ?
                WHERE ticker = ?
            """, (result.score, new_highest, scan_date, datetime.now().isoformat(), result.ticker))

    def add_to_watchlist(self, ticker: str, notes: Optional[str] = None) -> bool:
        """Add ticker to watchlist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO watchlist (ticker, added_date, notes)
                    VALUES (?, ?, ?)
                """, (ticker.upper(), datetime.now().date().isoformat(), notes))
                return True
            except sqlite3.IntegrityError:
                # Already exists
                return False

    def remove_from_watchlist(self, ticker: str) -> bool:
        """Remove ticker from watchlist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker.upper(),))
            return cursor.rowcount > 0

    def get_watchlist(self, status: Optional[str] = None) -> List[Dict]:
        """Get watchlist items"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if status:
                cursor.execute("""
                    SELECT * FROM watchlist
                    WHERE status = ?
                    ORDER BY highest_score DESC, last_seen DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT * FROM watchlist
                    ORDER BY highest_score DESC, last_seen DESC
                """)

            return [dict(row) for row in cursor.fetchall()]

    def update_watchlist_status(self, ticker: str, status: str,
                               notes: Optional[str] = None) -> bool:
        """Update watchlist item status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if notes:
                cursor.execute("""
                    UPDATE watchlist
                    SET status = ?, notes = ?, last_updated = ?
                    WHERE ticker = ?
                """, (status, notes, datetime.now().isoformat(), ticker.upper()))
            else:
                cursor.execute("""
                    UPDATE watchlist
                    SET status = ?, last_updated = ?
                    WHERE ticker = ?
                """, (status, datetime.now().isoformat(), ticker.upper()))

            return cursor.rowcount > 0

    # ========== STATISTICS ==========

    def get_scan_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics about scan performance"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total scans
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM scan_history
                WHERE scan_date >= date('now', '-{} days')
            """.format(days))
            stats['total_scans'] = cursor.fetchone()['total']

            # Scans by type
            cursor.execute("""
                SELECT scan_type, COUNT(*) as count
                FROM scan_history
                WHERE scan_date >= date('now', '-{} days')
                GROUP BY scan_type
            """.format(days))
            stats['scans_by_type'] = {row['scan_type']: row['count'] for row in cursor.fetchall()}

            # Total results found
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM scan_results
                WHERE scan_date >= date('now', '-{} days')
            """.format(days))
            stats['total_results'] = cursor.fetchone()['total']

            # Results by type
            cursor.execute("""
                SELECT scan_type, COUNT(*) as count
                FROM scan_results
                WHERE scan_date >= date('now', '-{} days')
                GROUP BY scan_type
            """.format(days))
            stats['results_by_type'] = {row['scan_type']: row['count'] for row in cursor.fetchall()}

            # Average results per scan
            if stats['total_scans'] > 0:
                stats['avg_results_per_scan'] = stats['total_results'] / stats['total_scans']
            else:
                stats['avg_results_per_scan'] = 0

            # Top scoring tickers
            cursor.execute("""
                SELECT ticker, MAX(score) as max_score, COUNT(*) as appearances
                FROM scan_results
                WHERE scan_date >= date('now', '-{} days')
                GROUP BY ticker
                ORDER BY max_score DESC, appearances DESC
                LIMIT 10
            """.format(days))
            stats['top_tickers'] = [dict(row) for row in cursor.fetchall()]

            return stats

    # ========== MAINTENANCE ==========

    def cleanup_old_data(self, days: int = 90):
        """Remove data older than specified days"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()

            # Delete old scan results
            cursor.execute("DELETE FROM scan_results WHERE scan_date < ?", (cutoff_date,))
            results_deleted = cursor.rowcount

            # Delete old scan history
            cursor.execute("DELETE FROM scan_history WHERE scan_date < ?", (cutoff_date,))
            history_deleted = cursor.rowcount

            # Delete old performance tracking
            cursor.execute("DELETE FROM performance_tracking WHERE signal_date < ?", (cutoff_date,))
            perf_deleted = cursor.rowcount

            # Vacuum to reclaim space
            cursor.execute("VACUUM")

            return {
                'results_deleted': results_deleted,
                'history_deleted': history_deleted,
                'performance_deleted': perf_deleted
            }

    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            info = {
                'path': str(self.db_path),
                'exists': self.db_path.exists(),
                'size_mb': self.db_path.stat().st_size / 1024 / 1024 if self.db_path.exists() else 0,
                'tables': {}
            }

            # Get row counts for each table
            tables = ['scan_results', 'scan_history', 'watchlist', 'alerts',
                     'performance_tracking', 'pressure_cooker_results', 'dark_flow_results']

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                info['tables'][table] = cursor.fetchone()['count']

            return info


def get_database_manager() -> DatabaseManager:
    """Factory function to get database manager instance"""
    return DatabaseManager()

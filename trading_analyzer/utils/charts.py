"""
ASCII Chart Generation with Colors
Beautiful terminal charts using rich library
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Install 'rich' for colored charts: pip install rich")


@dataclass
class ChartConfig:
    """Configuration for ASCII charts"""
    width: int = 80
    height: int = 20
    show_volume: bool = True
    show_indicators: bool = True
    color_scheme: str = 'default'  # 'default', 'monochrome', 'cyberpunk'


class ASCIIChartGenerator:
    """
    Generate beautiful ASCII charts with colors in terminal

    Uses 'rich' library for:
    - Color support
    - Unicode box drawing
    - Progress bars for volume
    - Styled panels
    """

    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        self.console = Console() if RICH_AVAILABLE else None

    def plot_price_chart(self,
                        hist: pd.DataFrame,
                        ticker: str,
                        sr_levels: Optional[dict] = None,
                        vp_data: Optional[dict] = None):
        """
        Plot price chart with volume, S/R levels, and volume profile

        Args:
            hist: Historical OHLCV data
            ticker: Stock symbol
            sr_levels: Support/resistance levels dict
            vp_data: Volume profile data dict
        """
        if not RICH_AVAILABLE:
            print("⚠️  Install 'rich' library: pip install rich")
            return

        if len(hist) < 2:
            print("⚠️  Insufficient data for chart")
            return

        # Prepare data
        prices = hist['Close'].values
        volumes = hist['Volume'].values
        dates = hist.index

        # Take last N points for display
        display_points = min(len(prices), self.config.width)
        prices = prices[-display_points:]
        volumes = volumes[-display_points:]
        dates = dates[-display_points:]

        # Normalize data for display
        price_min, price_max = prices.min(), prices.max()
        price_range = price_max - price_min if price_max > price_min else 1

        # Create chart
        chart_lines = []

        # === PRICE CHART ===
        chart_height = self.config.height
        if self.config.show_volume:
            chart_height -= 5  # Reserve space for volume

        for row in range(chart_height):
            # Calculate price level for this row
            price_level = price_max - (row / chart_height) * price_range

            line = Text()

            # Y-axis price label
            price_label = f"${price_level:6.2f} │"
            line.append(price_label, style="dim")

            # Plot price line
            for i, price in enumerate(prices):
                # Determine if price crosses this level
                char = " "
                style = ""

                # Check if price is at this level
                tolerance = price_range / chart_height
                if abs(price - price_level) < tolerance:
                    # Color based on trend
                    if i > 0:
                        if price > prices[i-1]:
                            char = "█"
                            style = "green"
                        elif price < prices[i-1]:
                            char = "█"
                            style = "red"
                        else:
                            char = "─"
                            style = "yellow"
                    else:
                        char = "█"
                        style = "white"

                # Mark S/R levels
                if sr_levels:
                    if sr_levels.get('nearest_resistance'):
                        if abs(price_level - sr_levels['nearest_resistance']) < tolerance:
                            char = "─"
                            style = "red bold"

                    if sr_levels.get('nearest_support'):
                        if abs(price_level - sr_levels['nearest_support']) < tolerance:
                            char = "─"
                            style = "green bold"

                # Mark POC
                if vp_data and vp_data.get('poc_price'):
                    if abs(price_level - vp_data['poc_price']) < tolerance:
                        char = "•"
                        style = "cyan bold"

                line.append(char, style=style)

            chart_lines.append(line)

        # === VOLUME BARS ===
        if self.config.show_volume:
            chart_lines.append(Text("─" * (self.config.width + 10), style="dim"))

            # Normalize volume
            vol_max = volumes.max() if volumes.max() > 0 else 1
            vol_height = 4

            for row in range(vol_height):
                vol_level = vol_max * (1 - row / vol_height)
                line = Text()
                line.append(f"        │", style="dim")

                for vol in volumes:
                    if vol >= vol_level:
                        line.append("▌", style="blue")
                    else:
                        line.append(" ")

                chart_lines.append(line)

        # === X-AXIS (TIME) ===
        time_line = Text("        └" + "─" * len(prices), style="dim")
        chart_lines.append(time_line)

        # Date labels (start, middle, end)
        date_label = Text("         ")
        date_label.append(f"{dates[0].strftime('%m/%d')}", style="dim")
        date_label.append(" " * (len(prices) // 2 - 5))
        if len(dates) > len(prices) // 2:
            date_label.append(f"{dates[len(dates)//2].strftime('%m/%d')}", style="dim")
        date_label.append(" " * (len(prices) // 2 - 5))
        date_label.append(f"{dates[-1].strftime('%m/%d')}", style="dim")
        chart_lines.append(date_label)

        # === INDICATORS PANEL ===
        current_price = prices[-1]
        prev_price = prices[-2] if len(prices) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price * 100) if prev_price > 0 else 0

        price_color = "green" if price_change >= 0 else "red"
        arrow = "↑" if price_change >= 0 else "↓"

        indicators = Text()
        indicators.append(f"{ticker} ", style="bold white")
        indicators.append(f"${current_price:.2f} ", style=f"bold {price_color}")
        indicators.append(f"{arrow} {price_change_pct:+.2f}%", style=price_color)

        if sr_levels:
            indicators.append("\n")
            if sr_levels.get('nearest_support'):
                indicators.append(f"Support: ${sr_levels['nearest_support']:.2f} ", style="green")
            if sr_levels.get('nearest_resistance'):
                indicators.append(f"Resistance: ${sr_levels['nearest_resistance']:.2f}", style="red")

        if vp_data and vp_data.get('poc_price'):
            indicators.append("\n")
            indicators.append(f"POC: ${vp_data['poc_price']:.2f} ", style="cyan")

        # === ASSEMBLE PANEL ===
        panel = Panel(
            Text.from_ansi("\n".join(str(line) for line in chart_lines)),
            title=indicators,
            border_style="blue",
            box=box.ROUNDED
        )

        self.console.print(panel)

    def plot_compact_sparkline(self, prices: List[float], width: int = 20) -> str:
        """
        Create compact sparkline (mini chart)

        Args:
            prices: List of prices
            width: Width in characters

        Returns:
            ASCII sparkline string
        """
        if not prices:
            return ""

        # Normalize to 0-7 range (8 bar heights)
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price > min_price else 1

        bars = "▁▂▃▄▅▆▇█"
        sparkline = ""

        # Sample prices to fit width
        if len(prices) > width:
            step = len(prices) / width
            sampled_prices = [prices[int(i * step)] for i in range(width)]
        else:
            sampled_prices = prices

        for price in sampled_prices:
            normalized = (price - min_price) / price_range
            bar_idx = min(int(normalized * 7), 7)
            sparkline += bars[bar_idx]

        return sparkline

    def create_results_table(self, results: List[dict], max_rows: int = 20) -> Table:
        """
        Create rich table for scan results

        Args:
            results: List of result dictionaries
            max_rows: Maximum rows to display

        Returns:
            Rich Table object
        """
        if not RICH_AVAILABLE:
            return None

        table = Table(
            title="🔥 Scan Results",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )

        # Add columns
        table.add_column("#", style="dim", width=3)
        table.add_column("Ticker", style="bold")
        table.add_column("Price", justify="right")
        table.add_column("Change", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Chart", width=20)

        # Add rows
        for i, result in enumerate(results[:max_rows], 1):
            ticker = result.get('ticker', 'N/A')
            price = result.get('price', 0)
            change_pct = result.get('change_pct', 0)
            score = result.get('score', 0)

            # Price change color
            change_color = "green" if change_pct >= 0 else "red"
            change_text = f"{change_pct:+.1f}%"

            # Score color
            if score >= 80:
                score_color = "green bold"
            elif score >= 60:
                score_color = "yellow"
            else:
                score_color = "red"

            score_text = f"{score}/100"

            # Sparkline (if price history available)
            sparkline = ""
            if 'price_history' in result:
                sparkline = self.plot_compact_sparkline(result['price_history'])

            table.add_row(
                str(i),
                ticker,
                f"${price:.2f}",
                Text(change_text, style=change_color),
                Text(score_text, style=score_color),
                sparkline
            )

        return table

    def print_table(self, table: Table):
        """Print rich table"""
        if RICH_AVAILABLE and table:
            self.console.print(table)


# Test function
if __name__ == "__main__":
    import yfinance as yf

    print("Testing ASCII charts...")

    ticker = 'GME'
    stock = yf.Ticker(ticker)
    hist = stock.history(period='3mo')

    chart_gen = ASCIIChartGenerator()

    # Test price chart
    sr_levels = {
        'nearest_support': 15.50,
        'nearest_resistance': 22.75
    }

    vp_data = {
        'poc_price': 18.50
    }

    chart_gen.plot_price_chart(hist, ticker, sr_levels, vp_data)

    # Test sparkline
    prices = [10, 12, 11, 15, 14, 18, 20, 19, 22, 25]
    sparkline = chart_gen.plot_compact_sparkline(prices)
    print(f"\nSparkline: {sparkline}")

    # Test results table
    test_results = [
        {'ticker': 'GME', 'price': 22.50, 'change_pct': 8.5, 'score': 85,
         'price_history': [18, 19, 20, 21, 22, 22.5]},
        {'ticker': 'AMC', 'price': 5.75, 'change_pct': -2.1, 'score': 72,
         'price_history': [6.2, 6.0, 5.9, 5.8, 5.8, 5.75]},
    ]

    table = chart_gen.create_results_table(test_results)
    chart_gen.print_table(table)

"""
Export Utilities
Export scan results to CSV, Excel, and PDF formats
"""
import pandas as pd
from datetime import datetime
from typing import List, Optional
from pathlib import Path


class ResultExporter:
    """Export scan results in multiple formats"""

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize exporter

        Args:
            output_dir: Output directory (default: ~/Documents)
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.home() / 'Documents'

        self.output_dir.mkdir(exist_ok=True)

    def export_to_csv(self,
                     results: List[dict],
                     filename: Optional[str] = None,
                     scanner_type: str = 'scan') -> str:
        """
        Export results to CSV

        Args:
            results: List of result dictionaries
            filename: Output filename (auto-generated if None)
            scanner_type: Type of scan (for filename)

        Returns:
            Path to exported file
        """
        if not results:
            print("⚠️  No results to export")
            return None

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{scanner_type}_results_{timestamp}.csv"

        filepath = self.output_dir / filename

        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Reorder columns (important ones first)
        priority_cols = ['ticker', 'score', 'price', 'change_pct', 'rel_vol',
                        'float_m', 'short_percent', 'setup_stage']
        other_cols = [c for c in df.columns if c not in priority_cols]
        ordered_cols = [c for c in priority_cols if c in df.columns] + other_cols

        df = df[ordered_cols]

        # Export
        df.to_csv(filepath, index=False)

        print(f"✅ Exported to CSV: {filepath}")
        return str(filepath)

    def export_to_excel(self,
                       results: List[dict],
                       filename: Optional[str] = None,
                       scanner_type: str = 'scan') -> str:
        """
        Export results to Excel with formatting

        Args:
            results: List of result dictionaries
            filename: Output filename (auto-generated if None)
            scanner_type: Type of scan (for filename)

        Returns:
            Path to exported file
        """
        if not results:
            print("⚠️  No results to export")
            return None

        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            from openpyxl.formatting.rule import ColorScaleRule
        except ImportError:
            print("⚠️  Install openpyxl for Excel export: pip install openpyxl")
            return self.export_to_csv(results, filename, scanner_type)

        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{scanner_type}_results_{timestamp}.xlsx"

        filepath = self.output_dir / filename

        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Reorder columns
        priority_cols = ['ticker', 'score', 'price', 'change_pct', 'rel_vol',
                        'float_m', 'short_percent', 'setup_stage', 'grade',
                        'key_factors']
        other_cols = [c for c in df.columns if c not in priority_cols]
        ordered_cols = [c for c in priority_cols if c in df.columns] + other_cols

        df = df[ordered_cols]

        # Write to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Results', index=False)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Results']

            # Format header row
            header_fill = PatternFill(start_color="366092", end_color="366092",
                                     fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")

            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")

            # Conditional formatting for score column
            if 'score' in df.columns:
                score_col_letter = chr(65 + list(df.columns).index('score'))
                score_range = f"{score_col_letter}2:{score_col_letter}{len(df)+1}"

                # Color scale: red (0) -> yellow (50) -> green (100)
                worksheet.conditional_formatting.add(
                    score_range,
                    ColorScaleRule(
                        start_type='num', start_value=0, start_color='F8696B',
                        mid_type='num', mid_value=50, mid_color='FFEB84',
                        end_type='num', end_value=100, end_color='63BE7B'
                    )
                )

            # Conditional formatting for change_pct column
            if 'change_pct' in df.columns:
                change_col_letter = chr(65 + list(df.columns).index('change_pct'))
                change_range = f"{change_col_letter}2:{change_col_letter}{len(df)+1}"

                worksheet.conditional_formatting.add(
                    change_range,
                    ColorScaleRule(
                        start_type='num', start_value=-10, start_color='F8696B',
                        mid_type='num', mid_value=0, mid_color='FFFFFF',
                        end_type='num', end_value=10, end_color='63BE7B'
                    )
                )

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Freeze header row
            worksheet.freeze_panes = 'A2'

        print(f"✅ Exported to Excel: {filepath}")
        return str(filepath)

    def export_to_pdf(self,
                     results: List[dict],
                     filename: Optional[str] = None,
                     scanner_type: str = 'scan') -> str:
        """
        Export results to PDF report

        Args:
            results: List of result dictionaries
            filename: Output filename (auto-generated if None)
            scanner_type: Type of scan (for filename)

        Returns:
            Path to exported file
        """
        if not results:
            print("⚠️  No results to export")
            return None

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
        except ImportError:
            print("⚠️  Install reportlab for PDF export: pip install reportlab")
            return self.export_to_csv(results, filename, scanner_type)

        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{scanner_type}_results_{timestamp}.pdf"

        filepath = self.output_dir / filename

        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#366092'),
            spaceAfter=30,
        )

        title = Paragraph(f"🔥 {scanner_type.upper()} Scan Results", title_style)
        elements.append(title)

        # Subtitle
        subtitle = Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            f"Total Results: {len(results)}",
            styles['Normal']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))

        # Results table
        # Select key columns for PDF (use catalyst instead of setup_stage for momentum scans)
        columns = ['ticker', 'score', 'price', 'change_pct', 'rel_vol', 'float_m', 'catalyst', 'source']
        headers = ['Ticker', 'Score', 'Price', 'Change%', 'RelVol', 'Float(M)', 'Catalyst', 'Source']

        table_data = [headers]

        for result in results[:50]:  # Limit to 50 results for PDF
            row = []
            for col in columns:
                value = result.get(col, 'N/A')

                # Format numbers
                if col == 'price':
                    row.append(f"${value:.2f}" if isinstance(value, (int, float)) else str(value))
                elif col in ['change_pct', 'rel_vol', 'float_m']:
                    row.append(f"{value:.1f}" if isinstance(value, (int, float)) else str(value))
                elif col == 'score':
                    # Just show the score number, not "/100" since it's already out of 100
                    row.append(f"{value}" if isinstance(value, (int, float)) else str(value))
                else:
                    row.append(str(value)[:15])  # Truncate long strings

            table_data.append(row)

        # Create table
        table = Table(table_data, repeatRows=1)

        # Style table
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))

        elements.append(table)

        # Build PDF
        doc.build(elements)

        print(f"✅ Exported to PDF: {filepath}")
        return str(filepath)

    def export_to_json(self,
                      results: List[dict],
                      filename: Optional[str] = None,
                      scanner_type: str = 'scan') -> str:
        """
        Export results to JSON

        Args:
            results: List of result dictionaries
            filename: Output filename (auto-generated if None)
            scanner_type: Type of scan (for filename)

        Returns:
            Path to exported file
        """
        import json

        if not results:
            print("⚠️  No results to export")
            return None

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{scanner_type}_results_{timestamp}.json"

        filepath = self.output_dir / filename

        # Export to JSON with pretty printing
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"✅ Exported to JSON: {filepath}")
        return str(filepath)

    def export_all_formats(self,
                          results: List[dict],
                          base_filename: Optional[str] = None,
                          scanner_type: str = 'scan') -> dict:
        """
        Export to all formats at once

        Args:
            results: List of result dictionaries
            base_filename: Base filename (extensions added automatically)
            scanner_type: Type of scan

        Returns:
            Dictionary with paths to all exported files
        """
        if not base_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"{scanner_type}_results_{timestamp}"

        exports = {}

        # Remove extension if provided
        base_filename = base_filename.rsplit('.', 1)[0]

        # Export to each format
        exports['csv'] = self.export_to_csv(results, f"{base_filename}.csv", scanner_type)
        exports['json'] = self.export_to_json(results, f"{base_filename}.json", scanner_type)
        exports['xlsx'] = self.export_to_excel(results, f"{base_filename}.xlsx", scanner_type)
        exports['pdf'] = self.export_to_pdf(results, f"{base_filename}.pdf", scanner_type)

        print(f"\n✅ Exported to all formats:")
        for format_type, path in exports.items():
            if path:
                print(f"   • {format_type.upper()}: {path}")

        return exports


# Test function
if __name__ == "__main__":
    print("Testing export functionality...")

    # Test data
    test_results = [
        {
            'ticker': 'GME',
            'score': 85,
            'price': 22.50,
            'change_pct': 8.5,
            'rel_vol': 7.2,
            'float_m': 2.5,
            'short_percent': 32.5,
            'setup_stage': 'ready',
            'grade': 'A',
            'key_factors': ['Ultra-Low Float', 'High Short Interest']
        },
        {
            'ticker': 'AMC',
            'score': 72,
            'price': 5.75,
            'change_pct': -2.1,
            'rel_vol': 5.8,
            'float_m': 4.1,
            'short_percent': 18.3,
            'setup_stage': 'forming',
            'grade': 'B',
            'key_factors': ['Volume Surge']
        }
    ]

    exporter = ResultExporter()

    # Export to all formats
    exporter.export_all_formats(test_results, scanner_type='pressure_cooker')

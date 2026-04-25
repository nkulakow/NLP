"""PDF export utilities for stock analysis reports."""

from datetime import datetime
from io import BytesIO

import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.utils.chart_builder import ChartBuilder


class PDFReportExporter:
    """Generates professional PDF reports for stock analysis."""

    def __init__(self):
        """Initialize PDF exporter with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.title_style = ParagraphStyle(
            "CustomTitle",
            parent=self.styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1f77b4"),
            spaceAfter=12,
            alignment=1,
        )
        
        self.metadata_style = ParagraphStyle(
            "Metadata",
            parent=self.styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
        )

    def export(
        self,
        ticker: str,
        report_text: str,
        fig: go.Figure,
        metrics: dict,
        indicators: dict,
        mode: str,
        provider: str,
        execution_time: float,
        time_period: str = "1mo",
        chart_type: str = "Candlestick",
    ) -> BytesIO:
        """
        Export investment report with chart to PDF.

        Args:
            ticker: Stock symbol
            report_text: Report markdown text
            fig: Plotly figure object (if None, will be generated)
            metrics: Stock metrics dict (last_close, change, pct_change, high, low, volume)
            indicators: Selected indicators dict {name: bool}
            mode: Analysis mode (sequential or group_chat)
            provider: LLM provider (gemini or openai)
            execution_time: Report generation time in seconds
            time_period: Time period for chart if generating (default: "1mo")
            chart_type: Chart type - "Candlestick" or "Line" (default: "Candlestick")

        Returns:
            BytesIO object containing PDF ready for download
        """
        # Generate chart if not provided
        if fig is None:
            fig = self._generate_chart(ticker, indicators, time_period, chart_type)
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
        )

        story = []

        self._add_title_section(story, ticker)
        self._add_metadata_section(story, mode, provider, execution_time)

        self._add_report_content(story, report_text)

        if metrics:
            self._add_metrics_table(story, metrics)

        if indicators and any(indicators.values()):
            self._add_indicators_section(story, indicators)
        
        self._add_chart_image(story, fig)

        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer

    def _add_title_section(self, story: list, ticker: str):
        """Add title section to PDF."""
        story.append(Paragraph(f"Stock Analysis Report: {ticker.upper()}", self.title_style))
        story.append(Spacer(1, 0.2 * inch))

    def _add_metadata_section(self, story: list, mode: str, provider: str, execution_time: float):
        """Add metadata section with generation info."""
        metadata_text = (
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Mode: {mode.replace('_', ' ').title()} | "
            f"Provider: {provider.title()} | "
            f"Execution Time: {execution_time:.1f}s"
        )
        story.append(Paragraph(metadata_text, self.metadata_style))
        story.append(Spacer(1, 0.15 * inch))

    def _add_metrics_table(self, story: list, metrics: dict):
        """Add stock metrics table to PDF."""
        metrics_data = [
            ["Metric", "Value"],
            ["Last Close", f"${metrics.get('last_close', 0):.2f}"],
            ["Change", f"${metrics.get('change', 0):.2f} ({metrics.get('pct_change', 0):.2f}%)"],
            ["High", f"${metrics.get('high', 0):.2f}"],
            ["Low", f"${metrics.get('low', 0):.2f}"],
            ["Volume", f"{metrics.get('volume', 0):,}"],
        ]

        metrics_table = Table(metrics_data, colWidths=[2 * inch, 2 * inch])
        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(metrics_table)
        story.append(Spacer(1, 0.2 * inch))

    def _add_indicators_section(self, story: list, indicators: dict):
        """Add technical indicators section."""
        selected = [k for k, v in indicators.items() if v]
        indicators_text = f"<b>Technical Indicators:</b> {', '.join(selected)}"
        story.append(Paragraph(indicators_text, self.styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

    def _generate_chart(self, ticker: str, indicators: dict, time_period: str, chart_type: str) -> go.Figure:
        """Generate chart if not provided."""
        return ChartBuilder.create_chart(ticker, indicators, time_period, chart_type)


    def _add_chart_image(self, story: list, fig: go.Figure):
        """Add chart reference text to PDF."""
        story.append(Paragraph("<b>Interactive Chart</b>", self.styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        
        chart_text = (
            "<i>A detailed interactive chart with price candlesticks/lines and selected technical indicators "
            "(SMA, EMA, Bollinger Bands) can be viewed in the web application. "
            "Click the 'Update' button in the sidebar to generate and view the live chart.</i>"
        )
        story.append(Paragraph(chart_text, self.styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

    def _add_report_content(self, story: list, report_text: str):
        """Add report content section."""
        story.append(Paragraph("Investment Analysis Report", self.styles["Heading1"]))
        story.append(Spacer(1, 0.15 * inch))

        report_lines = report_text.split("\n")
        for line in report_lines:
            if line.strip():
                if line.startswith("**") and line.endswith("**"):
                    text = line.replace("**", "")
                    story.append(Paragraph(f"<b>{text}</b>", self.styles["Normal"]))
                else:
                    story.append(Paragraph(line, self.styles["Normal"]))
            story.append(Spacer(1, 0.05 * inch))

# src/analytics/reports.py
"""
PDF report generation using matplotlib and reportlab.
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import pandas as pd

from .data_manager import DataManager
from .calculations import AnalyticsEngine

class ReportGenerator:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager
        self.engine = AnalyticsEngine(data_manager)

    def generate_pdf_report(self, filename: str):
        """Generate a comprehensive PDF report."""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=1  # center
        )
        story.append(Paragraph("Rapport d'Analyse Comptable", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Date
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        story.append(Paragraph(f"Généré le {date_str}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Summary metrics
        summary = self.engine.company_summary()
        story.append(Paragraph("Résumé Global", styles['Heading2']))
        summary_data = [
            ["Total CA", f"{summary['total_revenue']:,.2f} Ar"],
            ["Coût total", f"{summary['total_cost']:,.2f} Ar"],
            ["Bénéfice net", f"{summary['net_profit']:,.2f} Ar"],
            ["Marge moyenne", f"{summary['average_margin_percent']:.2f}%"]
        ]
        t = Table(summary_data, colWidths=[2*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))

        # Break-even analysis
        be = self.engine.break_even_analysis()
        story.append(Paragraph("Seuil de Rentabilité", styles['Heading2']))
        be_data = [
            ["Seuil (unités)", f"{be['break_even_units']:,.0f}"],
            ["Seuil (CA)", f"{be['break_even_revenue']:,.2f} Ar"],
            ["Marge unitaire", f"{be['margin_per_unit']:.2f} Ar"],
            ["Charges fixes", f"{be['total_fixed_costs']:,.2f} Ar"]
        ]
        t = Table(be_data, colWidths=[2*inch, 2*inch])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))

        # Product profitability table
        story.append(Paragraph("Rentabilité par Produit", styles['Heading2']))
        prod_df = self.engine.product_profitability()
        # Convert to list of lists for reportlab
        headers = ["Produit", "Ventes", "CA", "Coût", "Bénéfice", "Marge%"]
        data = [headers]
        for _, row in prod_df.iterrows():
            data.append([
                row['name'],
                f"{row['sold']:,.0f}",
                f"{row['revenue']:,.2f}",
                f"{row['total_cost']:,.2f}",
                f"{row['profit']:,.2f}",
                f"{row['margin_percent']:.1f}%"
            ])
        t = Table(data, colWidths=[1.2*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.8*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))

        # Add a bar chart (using matplotlib)
        story.append(Paragraph("Chiffre d'Affaires par Produit", styles['Heading2']))
        img_data = self._create_bar_chart(prod_df)
        if img_data:
            story.append(Image(img_data, width=6*inch, height=3*inch))

        # Build PDF
        doc.build(story)

    def _create_bar_chart(self, prod_df: pd.DataFrame):
        """Create a bar chart as an in-memory image and return it."""
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(prod_df['name'], prod_df['revenue'], color='#2E86AB')
            ax.set_title('CA par Produit')
            ax.set_ylabel('Montant (Ar)')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            # Save to BytesIO
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close(fig)
            return buf
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None
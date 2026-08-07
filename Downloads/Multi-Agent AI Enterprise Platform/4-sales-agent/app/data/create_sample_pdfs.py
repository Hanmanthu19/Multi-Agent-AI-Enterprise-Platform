import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def build_pdf(filename: str, title: str, paragraphs: list[str]):
    os.makedirs("app/data", exist_ok=True)
    filepath = os.path.join("app/data", filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, title)
    
    c.setFont("Helvetica", 11)
    y = 710
    for text in paragraphs:
        for line in text.split("\n"):
            c.drawString(50, y, line)
            y -= 18
        y -= 10
    c.save()
    print(f"Created: {filepath}")

if __name__ == "__main__":
    build_pdf(
        "products.pdf",
        "Enterprise AI Agent Product Suite",
        [
            "Starter Tier: Includes single-document RAG and community support for up to 5,000 queries per month.",
            "Pro Tier: Provides multi-document RAG search, priority email support, and up to 50,000 queries per month.",
            "Enterprise Tier: Features dedicated account management, 24/7 SLA, fine-tuned custom LLM models, and on-premises deployment."
        ]
    )

    build_pdf(
        "pricing.pdf",
        "Official Subscription Pricing Sheet",
        [
            "Starter Plan: $29/user/month.",
            "Pro Plan: $79/user/month.",
            "Enterprise Plan: $199/user/month.",
            "Taxes: A standard 10% estimation applies to all subscription tiers."
        ]
    )

    build_pdf(
        "discount_policy.pdf",
        "Corporate Discount Policy",
        [
            "Annual Billing Discount: Signing an annual agreement grants an instant 20% discount across all tiers.",
            "Volume Discount (50+ seats): Additional 10% discount.",
            "Volume Discount (100+ seats): Additional 15% discount.",
            "Maximum Discount Cap: No combined discount may exceed 50% of subtotal."
        ]
    )

    build_pdf(
        "company_information.pdf",
        "Company Profile & SLA Overview",
        [
            "Our company delivers enterprise-grade LLM sales solutions with 99.99% uptime guarantees.",
            "All data is encrypted in transit and at rest using AES-256 standards.",
            "Dedicated support teams are available 24/7 for Enterprise customers."
        ]
    )
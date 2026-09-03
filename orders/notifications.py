from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .utils import generate_invoice_pdf

def send_order_notifications(order):
    """
    Sends notification emails to the customer (with PDF) and the seller.
    """
    # 1. Generate PDF
    pdf_content = generate_invoice_pdf(order)
    filename = f"Facture_Sankhofa_{order.id}.pdf"

    # 2. Email to Customer
    customer_subject = f"Confirmation de votre commande #{order.id} — Sankhofa"
    customer_body = f"""
    Bonjour {order.user.get_full_name() or order.user.email},
    
    Merci pour votre commande sur Sankhofa ! 
    Nous avons bien reçu votre demande et préparons l'expédition de vos trésors.
    
    Vous trouverez ci-joint votre facture au format PDF.
    
    L'équipe Sankhofa.
    """
    
    customer_email = EmailMessage(
        customer_subject,
        customer_body,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email]
    )
    customer_email.attach(filename, pdf_content, 'application/pdf')
    customer_email.send(fail_silently=True)

    # 3. Email to Sellers (An order can have multiple products from different sellers)
    sellers = set()
    for item in order.items.all():
        if item.product and item.product.seller:
            sellers.add(item.product.seller)
    
    for seller in sellers:
        seller_subject = f"Nouvelle vente sur Sankhofa ! Commande #{order.id}"
        seller_body = f"""
        Félicitations {seller.profile.business_name if hasattr(seller, 'profile') else seller.email} !
        
        Une nouvelle commande vient d'être passée pour l'un de vos produits.
        Connectez-vous à votre espace vendeur pour voir les détails et préparer l'envoi.
        
        Détails de la commande accessible sur : http://localhost:8080/seller/dashboard/orders
        
        L'équipe Sankhofa.
        """
        
        seller_email = EmailMessage(
            seller_subject,
            seller_body,
            settings.DEFAULT_FROM_EMAIL,
            [seller.email]
        )
        seller_email.send(fail_silently=True)

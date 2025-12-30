from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from core.email_service import EmailService

@receiver(pre_save, sender=Order)
def order_status_sync_and_email(sender, instance, **kwargs):
    if not instance.pk:
        return # New order

    try:
        old_order = Order.objects.get(pk=instance.pk)
        
        # 1. AUTO-SYNC LOGIC: If status implies payment, set is_paid = True
        paid_statuses = ['paid', 'processing', 'shipped', 'delivered']
        if instance.status in paid_statuses:
            instance.is_paid = True

        # 2. EMAIL LOGIC: If status changed, send email
        if old_order.status != instance.status:
            print(f"Status changed from {old_order.status} to {instance.status}")
            EmailService.send_order_status_email(instance)
            
    except Order.DoesNotExist:
        pass
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from core.email_service import EmailService

@receiver(pre_save, sender=Order)
def order_status_change_listener(sender, instance, **kwargs):
    if not instance.pk:
        return # New order, ignore (Checkout view handles new order email if needed)

    try:
        old_order = Order.objects.get(pk=instance.pk)
        if old_order.status != instance.status:
            # Status has changed! Send Email.
            print(f"Status changed from {old_order.status} to {instance.status}")
            EmailService.send_order_status_email(instance)
    except Order.DoesNotExist:
        pass
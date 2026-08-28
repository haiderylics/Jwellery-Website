"""Signal receivers to handle post-commit cache invalidation, media processing, and safe cleanup.

Architecture Guarantees:
1. Transaction Safety: Media variant generation, file cleanup, and cache invalidation
   are deferred via `transaction.on_commit(...)` to execute only after successful DB commit.
2. Change Detection: Variants are generated ONLY when the file field actually changed
   or is newly created, avoiding redundant processing on unrelated field saves.
3. Safe Replacement: On media update, old files are cleaned up only after the new record
   has successfully committed to the database.
"""

import logging
from typing import Any

from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from backend.apps.catalog.models import (
    Category,
    Product,
    ProductAttributeType,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
    ProductVideo,
)
from backend.apps.common.cache_utils import (
    CACHE_KEY_ABOUT,
    CACHE_KEY_ADMIN_BRANDING,
    CACHE_KEY_ADMIN_METRICS,
    CACHE_KEY_ATTRIBUTES,
    CACHE_KEY_CATEGORIES,
    CACHE_KEY_DELIVERY_SETTINGS,
    CACHE_KEY_GALLERY,
    CACHE_KEY_HOMEPAGE,
    CACHE_KEY_POPUPS_ACTIVE,
    CACHE_KEY_PROMOTIONS_ACTIVE,
    CACHE_KEY_REVIEWS,
    CACHE_KEY_SITE_SETTINGS,
    invalidate_product_cache,
    invalidate_storefront_cache,
)
from backend.apps.common.media import cleanup_storage_media, generate_image_variants
from backend.apps.content.models import AboutSection, GalleryItem, Review
from backend.apps.promotions.models import Popup, Promotion
from backend.apps.settings.models import DeliverySettings, SiteSettings, SocialLink

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Cache Invalidation Signals (Post-Commit)
# --------------------------------------------------------------------------


def _schedule_cache_invalidation(keys: list[str], *, products: bool = False) -> None:
    """Schedule storefront cache invalidation on transaction commit."""

    def _invalidate() -> None:
        invalidate_storefront_cache(keys)
        if products:
            invalidate_product_cache()

    transaction.on_commit(_invalidate)


@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Product)
@receiver([post_save, post_delete], sender=ProductVariant)
@receiver([post_save, post_delete], sender=ProductImage)
@receiver([post_save, post_delete], sender=ProductVideo)
@receiver([post_save, post_delete], sender=ProductAttributeType)
@receiver([post_save, post_delete], sender=ProductAttributeValue)
def invalidate_catalog_cache(sender: Any, **kwargs: Any) -> None:
    """Invalidate catalog and homepage cache when products or categories change."""
    keys = [CACHE_KEY_HOMEPAGE]
    if sender in {Category, Product}:
        keys.append(CACHE_KEY_CATEGORIES)
    if sender in {ProductAttributeType, ProductAttributeValue}:
        keys.append(CACHE_KEY_ATTRIBUTES)
    if sender is Product:
        keys.append(CACHE_KEY_ADMIN_METRICS)
    _schedule_cache_invalidation(keys, products=True)


@receiver([post_save, post_delete], sender=Review)
@receiver([post_save, post_delete], sender=GalleryItem)
@receiver([post_save, post_delete], sender=AboutSection)
def invalidate_content_cache(sender: Any, **kwargs: Any) -> None:
    """Invalidate content and homepage cache when reviews, gallery, or about sections change."""
    keys = [CACHE_KEY_HOMEPAGE]
    if sender is Review:
        keys.extend([CACHE_KEY_REVIEWS, CACHE_KEY_ADMIN_METRICS])
    elif sender is GalleryItem:
        keys.append(CACHE_KEY_GALLERY)
    elif sender is AboutSection:
        keys.append(CACHE_KEY_ABOUT)
    _schedule_cache_invalidation(keys)


@receiver([post_save, post_delete], sender=Promotion)
@receiver([post_save, post_delete], sender=Popup)
def invalidate_promotions_cache(sender: Any, **kwargs: Any) -> None:
    """Invalidate active promotions and homepage cache."""
    keys = [CACHE_KEY_HOMEPAGE, CACHE_KEY_ADMIN_METRICS]
    keys.append(CACHE_KEY_PROMOTIONS_ACTIVE if sender is Promotion else CACHE_KEY_POPUPS_ACTIVE)
    _schedule_cache_invalidation(keys)


@receiver([post_save, post_delete], sender=SiteSettings)
@receiver([post_save, post_delete], sender=DeliverySettings)
@receiver([post_save, post_delete], sender=SocialLink)
def invalidate_settings_cache(sender: Any, **kwargs: Any) -> None:
    """Invalidate settings and homepage cache."""
    keys = [CACHE_KEY_HOMEPAGE]
    if sender in {SiteSettings, SocialLink}:
        keys.append(CACHE_KEY_SITE_SETTINGS)
    if sender is DeliverySettings:
        keys.append(CACHE_KEY_DELIVERY_SETTINGS)
    if sender is SiteSettings:
        keys.append(CACHE_KEY_ADMIN_BRANDING)
    _schedule_cache_invalidation(keys)


# --------------------------------------------------------------------------
# Media Change Detection & Transactional Processing
# --------------------------------------------------------------------------

MEDIA_IMAGE_MODELS = [ProductImage, GalleryItem, Review, Promotion, Popup, AboutSection]


@receiver(pre_save, sender=ProductImage)
@receiver(pre_save, sender=GalleryItem)
@receiver(pre_save, sender=Review)
@receiver(pre_save, sender=Promotion)
@receiver(pre_save, sender=Popup)
@receiver(pre_save, sender=AboutSection)
def detect_image_changes(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Detect whether the image file field was added or changed before saving."""
    instance._media_changed = False
    instance._old_media_to_cleanup = None

    if not instance.pk:
        # New model instance
        if hasattr(instance, "image") and instance.image:
            instance._media_changed = True
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        old_file_name = (
            old_instance.image.name if (old_instance.image and old_instance.image.name) else None
        )
        new_file_name = instance.image.name if (instance.image and instance.image.name) else None

        if old_file_name != new_file_name:
            instance._media_changed = True
            if old_file_name:
                instance._old_media_to_cleanup = old_file_name
    except sender.DoesNotExist:
        instance._media_changed = True


@receiver(pre_save, sender=ProductVideo)
def detect_video_changes(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Detect whether product video file changed before saving."""
    instance._media_changed = False
    instance._old_media_to_cleanup = None

    if not instance.pk:
        if instance.video_file:
            instance._media_changed = True
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        old_file_name = (
            old_instance.video_file.name
            if (old_instance.video_file and old_instance.video_file.name)
            else None
        )
        new_file_name = (
            instance.video_file.name if (instance.video_file and instance.video_file.name) else None
        )

        if old_file_name != new_file_name:
            instance._media_changed = True
            if old_file_name:
                instance._old_media_to_cleanup = old_file_name
    except sender.DoesNotExist:
        instance._media_changed = True


@receiver(post_save, sender=ProductImage)
@receiver(post_save, sender=GalleryItem)
@receiver(post_save, sender=Review)
@receiver(post_save, sender=Promotion)
@receiver(post_save, sender=Popup)
@receiver(post_save, sender=AboutSection)
def handle_image_variant_generation(
    sender: Any, instance: Any, created: bool, **kwargs: Any
) -> None:
    """Generate responsive WebP variants on transaction commit only if the image changed."""
    media_changed = getattr(instance, "_media_changed", False) or created
    old_media = getattr(instance, "_old_media_to_cleanup", None)

    if media_changed and hasattr(instance, "image") and instance.image and instance.image.name:
        file_name = instance.image.name

        def _process_and_clean():
            # Cloudinary creates CDN variants lazily from the original. Calling
            # the local pipeline here would require Storage.open() and download
            # the just-uploaded asset back from the CDN.
            if not getattr(default_storage, "is_cloudinary_storage", False):
                generate_image_variants(file_name)
            if old_media and old_media != file_name:
                cleanup_storage_media(old_media)

        transaction.on_commit(_process_and_clean)
    elif old_media:
        transaction.on_commit(lambda: cleanup_storage_media(old_media))


@receiver(post_save, sender=ProductVideo)
def handle_video_post_save(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    """Safely clean up old video file after replacement commits."""
    old_media = getattr(instance, "_old_media_to_cleanup", None)
    if old_media:
        transaction.on_commit(lambda: cleanup_storage_media(old_media))


@receiver(post_delete, sender=ProductImage)
@receiver(post_delete, sender=GalleryItem)
@receiver(post_delete, sender=Review)
@receiver(post_delete, sender=Promotion)
@receiver(post_delete, sender=Popup)
@receiver(post_delete, sender=AboutSection)
def handle_image_cleanup(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Safely cleanup original image file and all variants on transaction commit."""
    if hasattr(instance, "image") and instance.image and instance.image.name:
        file_name = instance.image.name
        transaction.on_commit(lambda: cleanup_storage_media(file_name))


@receiver(post_delete, sender=ProductVideo)
def handle_video_cleanup(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Safely delete uploaded video file on transaction commit."""
    if instance.video_file and instance.video_file.name:
        file_name = instance.video_file.name
        transaction.on_commit(lambda: cleanup_storage_media(file_name))

from django.utils.text import slugify


def unique_slug_generator(model_instance, first_name):
    """
    :param model_instance:
    :param first_name:
    :return:
    """
    slug = slugify(first_name)
    model_class = model_instance.__class__
    num = 1

    while model_class._default_manager.filter(slug=slug).exists():
        slug = slugify(first_name)
        slug = f'{slug}-{num}'
        num += 1

    return slug
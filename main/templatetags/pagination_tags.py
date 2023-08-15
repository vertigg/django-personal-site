from django import template

register = template.Library()


@register.filter
def generate_pagination_link(request, page: int) -> str:
    params = '&'.join([f'{k}={v}' for k, v in request.GET.items() if k != 'page'])
    return f'?page={page}&{params}'

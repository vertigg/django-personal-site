from discordbot.models import Wisdom
from discordbot.cogs.utils.checks import check_author_name


def wisdom_format(cache, wisdom_history):
    pyformat = '```py\n{}```'
    message = '{0:<4} : {1:^18} : {2:^35}\n'.format(
        'ID', 'Author', 'Wisdom Text')

    latest_wisdom = Wisdom.objects.latest('id')
    wisdom_count = Wisdom.objects.count()

    if wisdom_history:
        message += '\nLast wisdoms (Max limit: {0})\n'.format(
            wisdom_history.maxlen)
        for item in wisdom_history:
            author_name = check_author_name(item.author_id, cache)
            wisdom = item.text.replace('\n', '')
            if len(wisdom) > 35:
                wisdom = '{0:.32}...'.format(wisdom)
            message += '{0.id:<4} : {1:^18} : {2:35}\n'.format(
                item, author_name, wisdom)

    message += '\nLatest wisdom:\n{0.id:<4} : {1:^18} : {0.text:35}\n\nTotal wisdoms: {2}'.format(
        latest_wisdom, check_author_name(latest_wisdom.author_id, cache), wisdom_count)
    return pyformat.format(message)

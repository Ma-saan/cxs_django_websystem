from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    # dictionaryが辞書型でない場合は何もせずにNoneを返す
    if not isinstance(dictionary, dict):
        return None
    
    return dictionary.get(key)
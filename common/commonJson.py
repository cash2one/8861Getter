#!/usr/bin/env python
#encoding=UTF-8
import json
import decimal
import six

class CommonJSONEncoder(json.JSONEncoder):

    """
    Common JSON Encoder
    json.dumps(myString, cls=CommonJSONEncoder)
    """

    def default(self, obj):

        if isinstance(obj, decimal.Decimal):
            return str(obj)

# class CommonJSONDecoder(json.JSONDecoder):
#
#     """
#     Common JSON Encoder
#     json.loads(myString, cls=CommonJSONEncoder)
#     """
#
#     @classmethod
#     def object_hook(cls, obj):
#         for key in obj:
#             if isinstance(key, six.string_types):
#                 if 'type{decimal}' == key:
#                     try:
#                         return decimal.Decimal(obj[key])
#                     except:
#                         pass
#
#     def __init__(self, **kwargs):
#         kwargs['object_hook'] = self.object_hook
#         super(CommonJSONDecoder, self).__init__(**kwargs)
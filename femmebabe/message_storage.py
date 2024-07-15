from django.contrib.messages.storage.session import SessionStorage
from django.contrib.messages.storage.base import Message


class DedupMessageMixin(object):
    def __iter__(self):
        msgset = [tuple(m.__dict__.items())
                  for m in super(DedupMessageMixin, self).__iter__()]
        return iter([Message(**dict(m)) for m in set(msgset)])


class SessionDedupStorage(DedupMessageMixin, SessionStorage):
    pass

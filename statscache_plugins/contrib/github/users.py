from __future__ import absolute_import

import datetime
import functools

import statscache.plugins
from statscache_plugins.contrib.github import ModelMixinBase, PluginMixin

import fedmsg.meta
import sqlalchemy as sa


class Plugin(PluginMixin, statscache.plugins.BasePlugin):
    name = "contrib, github users"
    summary = "Mapping of FAS identities to GitHub usernames"
    description = """
    ...
    """
    topics = [
        'github.create',
        'github.delete',
        'github.push',
        'github.fork',
        'github.release',
        'github.member',
        'github.commit_comment',
        'gihtub.issue.opened',
        'github.issue.reopened',
        'gihtub.issue.comment',
        'github.pull_request_review_comment',
        'github.pull_request.closed',
    ]

    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(self, *args, **kwargs)
        self.cache = set() # FIXME: set *some* limit and employ LRU eviction

    class Model(ModelMixinBase, statscache.plugins.BaseModel):
        __tablename__ = 'contrib_github_users'
        identity = sa.Column(sa.UnicodeText, nullable=True, index=True)

    model = Model

    def process(self, message):
        identity = fedmsg.meta.msg2usernames(message)[0]
        username = message['msg']['sender']['login']

        key = (identity, username)

        if key not in self.cache:
            self.cache.add(key)
            timestamp = datetime.datetime.fromtimestamp(message['timestamp'])
            self.ready.append(self.model(
                timestamp=timestamp,
                username=username,
                identity=identity
            ))

    def update(self, session):
        def unique(item):
            return session.query(self.model)\
                    .filter_by(username=item.username,
                               identity=item.identity)\
                    .first() is None

        self.ready = filter(unique, self.ready)
        super(Plugin, self).update(session)

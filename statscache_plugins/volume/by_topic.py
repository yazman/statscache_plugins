import collections
import datetime

from statscache_plugins.volume.utils import VolumePluginMixin, plugin_factory

import sqlalchemy as sa


class PluginMixin(VolumePluginMixin):
    name = "volume, by topic"
    summary = "the count of messages, organized by topic"
    description = """
    For any given time window, the number of messages that come across
    the bus for each topic.
    """

    def handle(self, session, messages):
        volumes = collections.defaultdict(int)
        for msg in messages:
            msg_timestamp = datetime.datetime.fromtimestamp(msg['timestamp'])
            volumes[(msg['topic'],
                     self.frequency.next(now=msg_timestamp))] += 1

        for key, volume in volumes.items():
            topic, timestamp = key
            result = session.query(self.model)\
                .filter(self.model.topic == topic)\
                .filter(self.model.timestamp == timestamp)
            row = result.first()
            if row:
                row.volume += volume
            else:
                row = self.model(
                    timestamp=timestamp,
                    volume=volume,
                    topic=topic)
            session.add(row)
        session.commit()


plugins = plugin_factory(
    [datetime.timedelta(seconds=s) for s in [1, 5, 60]],
    PluginMixin,
    "VolumeByTopic",
    "data_volume_by_topic_",
    columns={
        'volume': sa.Column(sa.Integer, nullable=False),
        'topic': sa.Column(sa.UnicodeText, nullable=False, index=True),
    }
)

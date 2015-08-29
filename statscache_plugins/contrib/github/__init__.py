import sqlalchemy as sa

class ModelMixinBase(object):
        identity = sa.Column(sa.UnicodeText, nullable=True, index=True)
        username = sa.Column(sa.UnicodeText, nullable=False, index=True)


class ModelMixin(ModelMixinBase):
        repository = sa.Column(sa.UnicodeText, nullable=False, index=True)
        link = sa.Column(sa.UnicodeText, nullable=False)


class PluginMixin(object):

    nullable = [] # nullable columns of the model

    def __init__(self, *args, **kwargs):
        super(PluginMixin, self).__init__(*args, **kwargs)
        self.ready = [] # rows to insert

    def fill(self, session):
        for item in session.filter(sa.or_(column == None
                                          for column in self.nullable)):
            self.queue.enqueue(item)

    def update(self, session):
        session.add_all(self.ready)
        self.ready = []
        session.commit()

import abc
from search import Search
from storage import PersistantMixin

class MessageProcessor(object):
    """
    This class will process all messages received by chat bot. A message can be of different types,
    accordingly there can be any number of processors. The first processor for which message meet
    criteria will be invoked.

    For chat-bot this class is abstract class which will invoke correct processer and return
    response.
    """
    def execute(self, message):
        for processor in BaseProcessor.processors:
            proc_obj = processor(message.lower())
            if proc_obj.is_valid_message():
                return proc_obj.execute()


class BaseProcessor(object):
    """
    This class will act as base class for all processors. All subclass will resgister themself.
    """
    # All subclass will resgister themself here and sequentially executed.
    processors = []
    # Register all subclass against supported link_name
    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.processors.append(cls)

    @abc.abstractmethod
    def is_valid_message(self):
        """
        Drived class must implement this method. Processor will be executed only if this method
        return True. If return value is False, then skip this processor.
        """
        return False

    def __init__(self, message):
        self.message = message
        self.msg_tokens = message.split()

    @abc.abstractmethod
    def execute(self):
        return None


class ExactMessageProcessor(BaseProcessor):
    """
    If message match exactly then we need to return an exact response like any user sending message
    'hi' should get "Hey". All such messages can be listed here.
    """
    exact_response = {
        "hi": "Hey"
    }

    def is_valid_message(self):
        return self.message in self.exact_response

    def execute(self):
        return self.exact_response[self.message]


class SearchMessageProcessor(BaseProcessor, PersistantMixin):
    """
    This class is responsible to make a search request for valid messages. First word of the message
    is going to decide the search engine. Before sending response to user we also log query history
    to persistent storage.
    """
    def is_valid_message(self):
        engines = ['!'+engine for engine in Search.all_engines.keys()]
        if self.msg_tokens[0].startswith(tuple(engines)):
            return True
        return False

    def execute(self):
        engine, *query_tokens = self.msg_tokens
        query = ' '.join(query_tokens)
        # remove ! from engine name
        engine_name = engine[1:]
        self.store_data(query)
        return Search().execute(engine_name, query)


class RecenetHistoryProcessor(BaseProcessor, PersistantMixin):
    """
    This class is responsible to extract recent search history.
    """
    def is_valid_message(self):
        if self.msg_tokens[0].startswith('!recent'):
            return True
        return False

    def execute(self):
        _, *query_tokens = self.msg_tokens
        query = ' '.join(query_tokens)
        return self.search(query)

class MultichoiceQuestion:
    def __init__(self,):
        self.statement= ""
        self.options = []
        self.answer = None
        self.topic = None

    def add_statement(self, statement):
        self.statement = statement

    def add_option(self, option):
        self.options.append(option)

    def add_answer(self, answer):
        self.answer = answer

    def add_topic(self, topic):
        self.topic = topic

    def add_call(self, call):
        self.call = call

    def add_source(self, source):
        self.source = source

    def is_empty(self):
        if self.statement == "" and self.options.len == 0 and self.answer is None:
            return True
        else:
            return False

    def print(self):
        text = ""
        if self.statement != "":
            text += self.statement + '\n'

        if len(self.options) > 0:
            for i, option in enumerate(self.options):
                text += option
                if i<len(self.options)-1:
                    text += '\n'

        return text

    def to_dict(self):
        return {
            "statement": self.statement,
            "options": self.options,
            "answer": self.answer,
            "topic": self.topic,
            "call": self.call,
            "source": self.source
        }



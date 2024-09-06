import csv

class TopicConverter:
    def __init__(self):
        # Open the CSV file
        call_lines = self.read_csv('../../test_data/topics_eq/calls_test.csv')

        topic_conv_lines = self.read_csv('../../test_data/topics_eq/topics_eq_test3.csv')
        if not self.check_topic_lines(topic_conv_lines):
            # It should raise an error
            self.topic_conv_lines = None

        # Declare attributes
        self.call_lines = call_lines
        self.topic_conv_lines = topic_conv_lines

    def read_csv(self, path):
        with open(path, mode='r') as file:
            reader = csv.reader(file, delimiter=',')

            # Skip the first line (header)
            next(reader)

            # Read the remaining lines into a list
            return [line for line in reader]

    def check_topic_lines(self, topic_eq_lines):
        for topic_eq_line in topic_eq_lines:
            prev_call = int(topic_eq_line[1])
            prev_topic = int(topic_eq_line[2])
            next_call = int(topic_eq_line[3])
            next_topic = int(topic_eq_line[4])

            if prev_call == next_call:
                print("Error in topic conversion file: Prev and next call are equal.")
                print(f"Rule: {prev_call}.{prev_topic} - {next_call}.{next_topic}")
                return False
        return True

    def split_topic_id(self, topic_id):
        # Split the string at the dot
        numbers = topic_id.split('.')

        # Convert the split parts into integers
        call_num = int(numbers[0])
        topic_num = int(numbers[1])

        return call_num, topic_num

    def find_next_call(self, call_num, call_lines):
        take_next = False
        next_call = None
        for call_line in call_lines:
            if take_next:
                next_call = call_line[0]
            if call_line[0] == call_num:
                take_next = True
        return next_call

    def int_or_space(self, number):
        if number == '':
            return ''
        else:
            int(number)

    def find_eq_topic(self, call, topic, ref_call, ):
        # identify the call after the topic ID call
        # next_call = find_next_call(call_num, call_lines)
        call_lines = self.call_lines
        topic_conv_lines = self.topic_conv_lines

        topic_results = []

        if ref_call > call:
            going_forward = True
        else:
            going_forward = False

        # loop conversion table
        for topic_conv_line in topic_conv_lines:
            if going_forward:
                line_cur_call = int(topic_conv_line[1])
                line_cur_topic = int(topic_conv_line[2])
            else:
                line_cur_call = int(topic_conv_line[3])
                line_cur_topic = int(topic_conv_line[4])

            if line_cur_call == call and line_cur_topic == topic:
                if going_forward:
                    eq_call = int(topic_conv_line[3])
                    eq_topic = int(topic_conv_line[4])
                else:
                    eq_call = int(topic_conv_line[1])
                    eq_topic = int(topic_conv_line[2])

                if eq_call == ref_call:
                    topic_results.append(eq_topic)
                else:
                    topic_lookup_results = self.find_eq_topic(eq_call, eq_topic, ref_call)
                    if topic_lookup_results:
                        topic_results += topic_lookup_results

        # Remove possible duplicates, respecting original order
        topic_results_no_dupl = [i for n, i in enumerate(topic_results) if i not in topic_results[:n]]

        return topic_results_no_dupl


def main():
    default_call = 203
    default_topic = "201.1"

    tc = TopicConverter()

    ref_call = input(f"Enter reference call [default {default_call}]:")
    if ref_call == '':
        ref_call = default_call
    else:
        ref_call = int(ref_call)

    topic_id = input(f"Enter topic ID [default {default_topic}]:")
    if topic_id == '':
        topic_id = default_topic

    call_num, topic_num = tc.split_topic_id(topic_id)

    if ref_call == call_num:
        print("Source call and goal call are equivalent = " + str(ref_call))
    else:
        ref_topics = tc.find_eq_topic(call_num, topic_num, ref_call)

        if ref_topics:
            # display results
            for ref_topic in ref_topics:
                print(f"{topic_id} -> {ref_call}.{ref_topic}")
        else:
            print(f"Cannot find equivalence {topic_id} in call {ref_call}.")

if __name__ == "__main__":
    main()
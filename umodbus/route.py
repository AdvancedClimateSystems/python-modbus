class Map:
    def __init__(self):
        self._rules = []

    def add_rule(self, endpoint, slave_ids, function_codes, addresses):
        self._rules.append(DataRule(endpoint, slave_ids, function_codes,
                                    addresses))

    def match(self, slave_id, function_code, address):
        if not self._rules[0].match_slave_id(slave_id):
            return False

        for rule in self._rules:
            if rule.match(function_code, address):
                return rule.endpoint


class DataRule:
    def __init__(self, endpoint, slave_ids, function_codes, addresses):
        self.endpoint = endpoint
        self.slave_ids = slave_ids
        self.function_codes = function_codes
        self.addresses = addresses

    def match(self, function_code, address):
        # A constraint of None matches any value
        matches = lambda values, v: values is None or v in values

        return matches(self.function_codes, function_code) and \
               matches(self.addresses, address)

    def match_slave_id(self, slave_id):
        matches = lambda values, v: values is None or v in values

        if matches(self.slave_ids, slave_id):
            return True
        return False

class HttpParser:
    @staticmethod
    def parse_params(params={}):
        params_to_string = "" if len(params) == 0 else "?"
        amount_params = 0
        for key in params:
            params_to_string += f"{key}={params[key]}"
            amount_params += 1
            if amount_params < len(params):
                params_to_string += "&"

        return params_to_string

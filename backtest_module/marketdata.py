from tokenize import String
import backtest_module.backtest_config as backtest_config
import requests



class MDClient:
    def __init__(self, backend) -> None:
        pass


class MarketStackBackEnd:

    def __init__(self) -> None:
        self.session = requests.session()
        self.api_key = self._read_secrets()

        
    def _read_secrets(self) -> String:
        with open(backtest_config.API_KEY_PATH) as file:
            api_key = file.read()
        return api_key
class GasProvider:
    """
    Simulated gas provider module showing how additional providers
    are added into the automation architecture.
    """

    def __init__(self):
        self.provider_name = "Demo Gas Provider"

    def login(self):
        return True

    def download_latest_bill(self):
        return {
            "provider_name": self.provider_name,
            "account_number": "ACC-100987",
            "billing_period": "Jan 2026",
            "amount_due": "$88.12",
            "due_date": "2026-02-12",
            "usage": "120 Therms"
        }

    def run(self):
        if self.login():
            return self.download_latest_bill()
        return None


if __name__ == "__main__":
    provider = GasProvider()
    print(provider.run())

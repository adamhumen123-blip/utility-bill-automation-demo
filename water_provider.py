class WaterProvider:
    """
    Simulated water provider module showing how the system scales
    provider-by-provider while keeping the structure maintainable.
    """

    def __init__(self):
        self.provider_name = "Demo Water Provider"

    def login(self):
        return True

    def download_latest_bill(self):
        return {
            "provider_name": self.provider_name,
            "account_number": "ACC-101554",
            "billing_period": "Jan 2026",
            "amount_due": "$54.67",
            "due_date": "2026-02-15",
            "usage": "18,400 Gallons"
        }

    def run(self):
        if self.login():
            return self.download_latest_bill()
        return None


if __name__ == "__main__":
    provider = WaterProvider()
    print(provider.run())

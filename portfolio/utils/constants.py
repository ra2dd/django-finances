import datetime
from decouple import config

# Global constant defining a start date of AssetPriceHistory importing
# and latest date a user can create AssetBalanceHistory record
START_DATE = datetime.date(
    int(config("START_DATE_YEAR")),
    int(config("START_DATE_MONTH")),
    int(config("START_DATE_DAY"))
)
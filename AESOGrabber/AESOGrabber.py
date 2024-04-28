from sqlalchemy import create_engine, text
import sqlalchemy.exc
import os
import time
import requests
import datetime

DB_URL = os.getenv("AESO_DB_URL")
AESO_API_KEY = os.getenv("AESO_API_KEY")
POLL_DELAY = int(os.getenv("AESO_POLL_DELAY", 60))

engine = create_engine(DB_URL)

with engine.connect() as conn:
    while True:
        resp = requests.get("https://api.aeso.ca/report/v1/csd/generation/assets/current", headers={"X-API-Key": AESO_API_KEY})
        jsondata = resp.json()

        ts = datetime.datetime.strptime(jsondata['return']['last_updated_datetime_utc'], '%Y-%m-%d %H:%M').replace(tzinfo=datetime.timezone.utc)
        data = []
        for asset in jsondata['return']['asset_list']:
            asset['ts'] = ts
            data.append(asset)        

        with conn.begin():
            try:
                conn.execute(text("insert into aeso_generation(ts, asset_id, fuel_type, sub_fuel_type, maximum_capability, net_generation, dispatched_contingency_reserve) "
                                "values (:ts, :asset, :fuel_type, :sub_fuel_type, :maximum_capability, :net_generation, :dispatched_contingency_reserve)"), data)
            except sqlalchemy.exc.IntegrityError:
                # We've already seen this set of data, just continue on
                pass
            finally:
                conn.commit()
        
        time.sleep(POLL_DELAY)
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
        time.sleep(POLL_DELAY)
        
        # Fetch per-asset generation data
        resp = requests.get(
            "https://api.aeso.ca/report/v1/csd/generation/assets/current",
            headers={"X-API-Key": AESO_API_KEY},
        )
        jsondata = resp.json()
        ts = datetime.datetime.strptime(
            jsondata["return"]["last_updated_datetime_utc"], "%Y-%m-%d %H:%M"
        ).replace(tzinfo=datetime.timezone.utc)
        with conn.begin():
            data = []
            for asset in jsondata["return"]["asset_list"]:
                asset["ts"] = ts
                data.append(asset)
            try:
                conn.execute(
                    text(
                        "insert into aeso_generation(ts, asset_id, fuel_type, sub_fuel_type, maximum_capability, net_generation, dispatched_contingency_reserve) "
                        "values (:ts, :asset, :fuel_type, :sub_fuel_type, :maximum_capability, :net_generation, :dispatched_contingency_reserve)"
                    ),
                    data,
                )
            except sqlalchemy.exc.IntegrityError:
                # We've already seen this set of data, just continue on
                pass
            finally:
                conn.commit()

        # Fetch summary data
        resp = requests.get(
            "https://api.aeso.ca/report/v1/csd/summary/current",
            headers={"X-API-Key": AESO_API_KEY},
        )
        jsondata = resp.json()
        ts = datetime.datetime.strptime(
            jsondata["return"]["last_updated_datetime_utc"], "%Y-%m-%d %H:%M"
        ).replace(tzinfo=datetime.timezone.utc)
        with conn.begin():
            try:
                data = jsondata["return"]
                data["ts"] = ts
                # NB: ":dispatched_contigency_reserve_total" is correct as this field is misspelled in the API
                #      "dispatched_contingency_reserve_total" is the database field with the correct spelling
                conn.execute(
                    text(
                        "insert into aeso_summary(ts, total_max_generation_capability, total_net_generation, net_to_grid_generation, net_actual_interchange, "
                        "alberta_internal_load, contingency_reserve_required, dispatched_contingency_reserve_total, dispatched_contingency_reserve_gen, "
                        "dispatched_contingency_reserve_other, lssi_armed_dispatch, lssi_offered_volume ) "
                        "values (:ts, :total_max_generation_capability, :total_net_generation, :net_to_grid_generation, :net_actual_interchange, "
                        ":alberta_internal_load, :contingency_reserve_required, :dispatched_contigency_reserve_total, :dispatched_contingency_reserve_gen, "
                        ":dispatched_contingency_reserve_other, :lssi_armed_dispatch, :lssi_offered_volume)"
                    ),
                    data,
                )

                data = []
                for gendata in jsondata["return"]["generation_data_list"]:
                    gendata["ts"] = ts
                    data.append(gendata)
                conn.execute(
                    text(
                        "insert into aeso_summary_generation(ts, fuel_type, aggregated_maximum_capability, aggregated_net_generation, aggregated_dispatched_contingency_reserve) "
                        "values (:ts, :fuel_type, :aggregated_maximum_capability, :aggregated_net_generation, :aggregated_dispatched_contingency_reserve)"
                    ),
                    data,
                )

                data = []
                for interchange in jsondata["return"]["interchange_list"]:
                    interchange["ts"] = ts
                    data.append(interchange)
                conn.execute(
                    text(
                        "insert into aeso_summary_interchange(ts, flow_path, actual_flow) values (:ts, :path, :actual_flow)"
                    ),
                    data,
                )

            except sqlalchemy.exc.IntegrityError:
                # We've already seen this set of data, just continue on
                pass
            finally:
                conn.commit()
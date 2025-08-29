import logging
import requests
from celery import shared_task

from apps.glycemic.models import GlycemicData

URL = "https://zang.vertigo-spy.workers.dev/"
logger = logging.getLogger("apps.glycemic.tasks")


@shared_task
def fetch_glycemic_data():
    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Error fetching glycemic data: {e}")
        return

    glycemic_list = data.get("glycemic_list", [])
    if not isinstance(glycemic_list, list):
        logger.error("Invalid data structure from API")
        return

    objs = []
    for entry in glycemic_list:
        objs.append(
            GlycemicData(
                time=int(entry["time"]),
                glycemic=float(entry["glycemic"]),
            )
        )

    GlycemicData.objects.bulk_create(objs, ignore_conflicts=True)
    logger.info(f"Inserted {len(objs)} new glycemic data entries.")

from faker import Faker
import random
import orjson
from myleadcli.utils import benchmark


@benchmark
def generate_fake_data(num_entries: int) -> None:
    fake = Faker(
        "en_US",
        providers=[
            "faker.providers",
            "faker.providers.user_agent",
            "faker.providers.date_time",
            "faker.providers.misc",
            "faker.providers.internet",
            "faker.providers.lorem",
            "faker.providers.currency",
            "faker.providers.address",
            "faker.providers.company",
            "faker.providers.person",
        ],
    )
    Faker.seed(0)

    data = []
    for _ in range(num_entries):
        conversion = {
            "id": fake.sha256(),
            "campaign_id": random.randint(1, 100),
            "campaign_name": fake.sentence(),
            "payout": round(random.uniform(10, 50), 2),
            "currency": "PLN",
            "status": random.choice(["pre_approved", "rejected", "pending", "approved"]),
            "status_reason": "some reason",
            "country": fake.country_code(representation="alpha-2"),
            "created_at": {
                "date": fake.date_time_this_decade(tzinfo=None).isoformat(),
                "timezone_type": 3,
                "timezone": fake.timezone(),
            },
            "user_agent": {
                "name": fake.user_agent(),
                "operation_system": fake.android_platform_token(),
                "operation_system_version": fake.android_platform_token(),
                "browser_system": fake.chrome(),
                "browser_version": fake.chrome(),
                "device": random.choice(["mobile", "desktop", "tablet"]),
                "device_brand": fake.company(),
                "device_model": fake.word(),
            },
            "ip": fake.ipv4(),
            "ml_sub1": fake.word(),
            "ml_sub2": fake.word(),
            "ml_sub3": fake.word(),
            "ml_sub4": fake.word(),
            "ml_sub5": fake.word(),
        }
        data.append(conversion)

    with open("fake_data.json", "wb") as f:
        content = orjson.dumps(data, option=orjson.OPT_INDENT_2)
        f.write(content)


if __name__ == "__main__":
    generate_fake_data(100_000)

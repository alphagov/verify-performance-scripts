import pandas


def get_sample_rp_mapping():
    return {
        "https://rp-entity-id-1.test.id": "RP 1",
        "https://rp-entity-id-2.test.id": "RP 2",
    }


def get_sample_verifications_by_rp_dataframe(with_rp_name=False):
    verifications_by_rp = pandas.DataFrame.from_dict(
        {
            0: ["https://rp-entity-id-1.test.id", "2018-07-23T01:22:03.478Z",
                "RETURNING", "https://sample-idp-1/sso"],
            1: ["https://rp-entity-id-2.test.id", "2018-07-23T04:56:19.156Z",
                "NEW", "https://sample-idp-2/sso"]
        },
        orient="index", columns=["RP Entity Id", "Timestamp", "Response type", "IDP Entity Id"])
    if with_rp_name:
        verifications_by_rp["rp"] = ["RP 1", "RP 2"]
    return verifications_by_rp

import main

event = {
    'Records': [
        {
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "tf-s3-lambda-20220727112810026100000001",
                "bucket": {
                    "name": "julian-log-router-test",
                    "ownerIdentity": {
                        "principalId": "A2VWZB4X1D3ETR"
                    },
                    "arn": "arn:aws:s3:::julian-log-router-test"
                },
                "object": {
                    "key": "cpln-test/coke/2022/07/27/14/42/ZsU064AN.jsonl",
                    "size": 219,
                    "eTag": "62319a931cce6616040afd74d1b75bc3",
                    "sequencer": "0062E12E2890FDF3A7"
                }
            }
        }
    ]
}

main.handler(event, {})

from flask import Flask, request, Response
from db import SessionLocal, License, init_db
from crypto_keys import get_signing_key
import datetime
import json
import time
import base64
import logging

app = Flask(__name__)

def make_signed_response(payload, status_code: int = 200) -> Response:
    if isinstance(payload, str):
        payload = {
            "status": "error",
            "message": payload
        }

    json_str = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    timestamp = str(int(time.time()))
    message = timestamp + json_str

    key = get_signing_key()
    signature = base64.b64encode(
        key.sign(message.encode()).signature
    ).decode()

    resp = Response(json_str, status=status_code, mimetype="application/json")
    resp.headers["x-signature-ed25519"] = signature
    resp.headers["x-signature-timestamp"] = timestamp
    return resp


@app.route("/auth", methods=["POST"])
def authorize():
    if not request.is_json:
        return make_signed_response("Invalid JSON")

    data = request.get_json()
    license_key = data.get("license_key")
    hwid = data.get("hwid")

    if not license_key or not hwid:
        return make_signed_response("Missing license_key or hwid")

    db = SessionLocal()
    now = datetime.datetime.utcnow()

    try:
        license = (
            db.query(License)
            .filter(License.license_key == license_key)
            .with_for_update()
            .first()
        )

        if not license:
            return make_signed_response("License key not found")

        if license.expires_at and license.expires_at < now:
            return make_signed_response("License expired")

        if license.hwid is None:
            license.hwid = hwid
            license.expires_at = now + datetime.timedelta(
                minutes=license.duration_minutes
            )
            db.commit()

        elif license.hwid != hwid:
            return make_signed_response("HWID does not match")

        return make_signed_response({
            "status": "success",
            "message": "Access granted",
            "hwid": hwid,
            "license_key": license.license_key,
            "expires_at": license.expires_at.isoformat()
        })

    except Exception:
        logging.exception("AUTH ERROR")
        return make_signed_response("Internal server error", 500)

    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=80)

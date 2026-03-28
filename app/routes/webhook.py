import json
import uuid
from flask import Blueprint, request, jsonify
from app import db
from app.models import ReferralCode, Conversion

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/conversion', methods=['POST'])
def record_conversion():
    """
    Called by your product backend when a meaningful event occurs.
    E.g. when a referred user completes signup or makes a purchase.

    Payload:
    {
        "referral_code": "ABC123XYZ",
        "conversion_type": "signup" | "purchase" | "hire",
        "value": 999.0,           // optional — purchase amount
        "referred_user_id": 42,   // optional
        "idempotency_key": "txn-xyz-001",  // prevents duplicate conversions
        "metadata": { ... }       // any extra data
    }
    """
    data = request.get_json() or {}

    ref_code_str = data.get('referral_code', '')
    idem_key     = data.get('idempotency_key') or str(uuid.uuid4())

    ref_code = ReferralCode.query.filter_by(code=ref_code_str).first()
    if not ref_code:
        return jsonify({'error': 'Referral code not found'}), 404

    # Idempotency guard — never double-count the same event
    if Conversion.query.filter_by(idempotency_key=idem_key).first():
        return jsonify({'message': 'Conversion already recorded (idempotent)'}), 200

    conversion = Conversion(
        referral_code_id=ref_code.id,
        referred_user_id=data.get('referred_user_id'),
        conversion_type=data.get('conversion_type', 'signup'),
        value=float(data.get('value', 0.0)),
        metadata_json=json.dumps(data.get('metadata', {})),
        idempotency_key=idem_key,
    )
    db.session.add(conversion)
    db.session.commit()

    return jsonify({
        'message':    'Conversion recorded',
        'conversion': conversion.to_dict(),
    }), 201

from flask import Blueprint, request, jsonify, redirect, g, current_app
from app import db
from app.models import ReferralCode, ReferralClick, Conversion
from app.helpers import require_auth, get_visitor_hash, get_client_ip

referral_bp = Blueprint('referral', __name__)


@referral_bp.route('/', methods=['POST'])
@require_auth
def create_referral():
    """Generate a new referral link for the logged-in user."""
    data     = request.get_json() or {}
    campaign = data.get('campaign', 'default')

    code = ReferralCode(user_id=g.user.id, campaign=campaign)
    db.session.add(code)
    db.session.commit()
    return jsonify({'referral': code.to_dict()}), 201


@referral_bp.route('/', methods=['GET'])
@require_auth
def list_referrals():
    """List all referral codes owned by the logged-in user."""
    codes = ReferralCode.query.filter_by(user_id=g.user.id).all()
    return jsonify({'referrals': [c.to_dict() for c in codes]}), 200


@referral_bp.route('/<int:code_id>', methods=['DELETE'])
@require_auth
def deactivate_referral(code_id):
    code = ReferralCode.query.filter_by(id=code_id, user_id=g.user.id).first()
    if not code:
        return jsonify({'error': 'Not found'}), 404
    code.is_active = False
    db.session.commit()
    return jsonify({'message': 'Referral code deactivated'}), 200


@referral_bp.route('/r/<string:code>', methods=['GET'])
def track_click(code):
    """
    Public endpoint — every click on a referral link hits this.
    Records the click, then redirects to the configured destination.
    """
    ref_code = ReferralCode.query.filter_by(code=code, is_active=True).first()
    if not ref_code:
        return jsonify({'error': 'Invalid or expired referral link'}), 404

    visitor_hash = get_visitor_hash(request)

    # Check if this visitor has already clicked this code (unique vs repeat)
    existing = ReferralClick.query.filter_by(
        referral_code_id=ref_code.id,
        visitor_hash=visitor_hash,
    ).first()

    click = ReferralClick(
        referral_code_id=ref_code.id,
        visitor_ip=get_client_ip(request),
        user_agent=request.headers.get('User-Agent', '')[:256],
        referrer=request.headers.get('Referer', ''),
        visitor_hash=visitor_hash,
        is_unique=(existing is None),
    )
    db.session.add(click)
    db.session.commit()

    # Redirect destination — in prod, make this configurable per campaign
    destination = request.args.get('redirect', current_app.config['BASE_URL'])
    return redirect(destination, code=302)

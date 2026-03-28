from flask import Blueprint, request, jsonify, g
from sqlalchemy import func
from app.models import ReferralCode, ReferralClick, Conversion
from app.helpers import require_auth

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/summary', methods=['GET'])
@require_auth
def summary():
    """Overall stats for the logged-in user across all campaigns."""
    codes = ReferralCode.query.filter_by(user_id=g.user.id).all()
    code_ids = [c.id for c in codes]

    total_clicks       = ReferralClick.query.filter(ReferralClick.referral_code_id.in_(code_ids)).count()
    unique_clicks      = ReferralClick.query.filter(
                            ReferralClick.referral_code_id.in_(code_ids),
                            ReferralClick.is_unique == True
                         ).count()
    total_conversions  = Conversion.query.filter(Conversion.referral_code_id.in_(code_ids)).count()
    total_value        = Conversion.query.with_entities(
                            func.sum(Conversion.value)
                         ).filter(Conversion.referral_code_id.in_(code_ids)).scalar() or 0.0

    return jsonify({
        'total_referral_codes': len(codes),
        'total_clicks':         total_clicks,
        'unique_clicks':        unique_clicks,
        'total_conversions':    total_conversions,
        'total_value':          round(float(total_value), 2),
        'conversion_rate':      round(total_conversions / total_clicks * 100, 2) if total_clicks else 0.0,
    }), 200


@analytics_bp.route('/campaigns', methods=['GET'])
@require_auth
def campaigns():
    """Per-campaign breakdown."""
    codes = ReferralCode.query.filter_by(user_id=g.user.id).all()
    return jsonify({'campaigns': [c.to_dict() for c in codes]}), 200


@analytics_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    """Top referrers by conversion count — public endpoint."""
    from app import db
    from app.models import User
    results = (
        db.session.query(
            User.username,
            func.count(Conversion.id).label('conversions'),
            func.sum(Conversion.value).label('total_value'),
        )
        .join(ReferralCode, ReferralCode.user_id == User.id)
        .join(Conversion, Conversion.referral_code_id == ReferralCode.id)
        .group_by(User.id)
        .order_by(func.count(Conversion.id).desc())
        .limit(10)
        .all()
    )
    return jsonify({'leaderboard': [
        {'username': r.username, 'conversions': r.conversions, 'total_value': float(r.total_value or 0)}
        for r in results
    ]}), 200

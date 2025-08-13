# mock_data.py

# Example: one ticket you can run the crew on
ticket_data = {
    "ticket_id": "T001",
    "user_id": "user_001",
    "message": "I entered the bonus code WELCOME50 but didn’t get my free spins."
}

# Pool of user profiles for testing
user_profiles = {
    "user_001": {
        "vip_level": "Silver",
        "total_deposits": 1200,
        "recent_issues": ["Deposit Problem"],
        "account_age_days": 150
    },
    "user_002": {
        "vip_level": "Gold",
        "total_deposits": 5400,
        "recent_issues": ["Bonus not applied", "Withdrawal Delay"],
        "account_age_days": 220
    },
    "user_003": {
        "vip_level": "Bronze",
        "total_deposits": 300,
        "recent_issues": [],
        "account_age_days": 45
    },
    "user_004": {
        "vip_level": "Platinum",
        "total_deposits": 10000,
        "recent_issues": ["Withdrawal Delay"],
        "account_age_days": 500
    },
    "user_005": {
        "vip_level": "Gold",
        "total_deposits": 7500,
        "recent_issues": ["Technical Issue"],
        "account_age_days": 365
    },
    "user_006": {
        "vip_level": "Silver",
        "total_deposits": 2500,
        "recent_issues": ["Login Problem"],
        "account_age_days": 120
    },
    "user_007": {
        "vip_level": "Bronze",
        "total_deposits": 100,
        "recent_issues": ["Deposit Problem"],
        "account_age_days": 20
    },
    "user_008": {
        "vip_level": "Gold",
        "total_deposits": 8000,
        "recent_issues": ["Bonus Issue", "Technical Issue"],
        "account_age_days": 400
    },
    "user_009": {
        "vip_level": "Silver",
        "total_deposits": 2200,
        "recent_issues": ["Account Verification"],
        "account_age_days": 200
    }
}

# Optional: pool of sample tickets to swap into `ticket_data` when testing
ticket_samples = [
    {"ticket_id": "T001", "user_id": "user_001", "message": "I entered the bonus code WELCOME50 but didn’t get my free spins."},
    {"ticket_id": "T004", "user_id": "user_004", "message": "I requested a withdrawal on Friday and it still shows pending."},
    {"ticket_id": "T005", "user_id": "user_005", "message": "Live dealer blackjack video keeps buffering, can’t play."},
    {"ticket_id": "T006", "user_id": "user_006", "message": "I forgot my password and the reset link isn’t working."},
    {"ticket_id": "T007", "user_id": "user_007", "message": "Credit card payment got charged but my account didn’t update."},
    {"ticket_id": "T008", "user_id": "user_008", "message": "I opted in for the cashback offer but nothing was credited."},
    {"ticket_id": "T009", "user_id": "user_009", "message": "I uploaded my ID but it still says ‘Pending Verification’."}
]

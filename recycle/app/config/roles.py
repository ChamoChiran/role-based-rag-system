ALLOWED_ROLES = {
    "finance": "Finance_Team, God_Tier_Admins",
    "hr": "Payroll & benefits",
    "marketing": "Ad spend & ROI metrics",
    "employee": "General information"
}

role_permissions = {
        "finance": ["Finance_Team", "God_Tier_Admins"],
        "marketing": ["Marketing_Team", "God_Tier_Admins"],
        "hr": ["HR_Team", "God_Tier_Admins"],
        "engineering": ["Engineering_Department", "God_Tier_Admins"],
        "general": [
            "Employee_Level",
            "Finance_Team",
            "Marketing_Team",
            "HR_Team",
            "Engineering_Department",
            "God_Tier_Admins",
        ],
    }
"""Create the demo fallback SQLite database used by Phase 14 visual resilience."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEMO_DB_PATH = PROJECT_ROOT / "data" / "demo.db"

SPECIALISTS = [
    {
        "name": "Dr. Sarah Chen",
        "board_role": "President",
        "metro_region": "Los Angeles - West",
        "company": "TechBridge AI",
        "title": "VP Data Science",
        "expertise_tags": "AI strategy, machine learning, hackathons",
        "initials": "DSC",
    },
    {
        "name": "Marcus Webb",
        "board_role": "Vice President",
        "metro_region": "San Diego",
        "company": "West Coast Ventures",
        "title": "Startup Advisor",
        "expertise_tags": "founder coaching, venture readiness, pitch review",
        "initials": "MW",
    },
    {
        "name": "Priya Nair",
        "board_role": "Treasurer",
        "metro_region": "Bay Area",
        "company": "Cloud Harbor",
        "title": "Director of Product Analytics",
        "expertise_tags": "analytics, dashboards, product strategy",
        "initials": "PN",
    },
    {
        "name": "James Rodriguez",
        "board_role": "Secretary",
        "metro_region": "Orange County",
        "company": "Insight Works",
        "title": "Research Operations Lead",
        "expertise_tags": "research ops, customer insight, survey design",
        "initials": "JR",
    },
    {
        "name": "Dr. Emily Park",
        "board_role": "Member-at-Large",
        "metro_region": "Portland",
        "company": "Civic Data Lab",
        "title": "Principal Research Scientist",
        "expertise_tags": "ethics, civic tech, responsible AI",
        "initials": "DEP",
    },
    {
        "name": "Kevin O'Brien",
        "board_role": "Member-at-Large",
        "metro_region": "Seattle",
        "company": "Retail Signal",
        "title": "Head of Market Intelligence",
        "expertise_tags": "retail analytics, segmentation, growth",
        "initials": "KOB",
    },
    {
        "name": "Aisha Johnson",
        "board_role": "Programs Chair",
        "metro_region": "Sacramento",
        "company": "Community Insight Partners",
        "title": "Program Director",
        "expertise_tags": "community outreach, partnerships, event programming",
        "initials": "AJ",
    },
    {
        "name": "Dr. Michael Torres",
        "board_role": "Education Chair",
        "metro_region": "Phoenix",
        "company": "Desert State University",
        "title": "Professor of Information Systems",
        "expertise_tags": "higher ed, data literacy, student engagement",
        "initials": "DMT",
    },
    {
        "name": "Lisa Chang",
        "board_role": "Membership Chair",
        "metro_region": "San Francisco",
        "company": "North Bay Research",
        "title": "Client Services Director",
        "expertise_tags": "membership growth, account strategy, sponsorships",
        "initials": "LC",
    },
    {
        "name": "Robert Kim",
        "board_role": "Member-at-Large",
        "metro_region": "Las Vegas",
        "company": "Signal Path Consulting",
        "title": "Innovation Consultant",
        "expertise_tags": "innovation programs, operations, executive workshops",
        "initials": "RK",
    },
]

CPP_EVENTS = [
    {
        "Event / Program": "AI for a Better Future Hackathon",
        "Category": "Innovation",
        "Recurrence (typical)": "Annual spring hackathon",
        "Host / Unit": "Cal Poly Pomona",
        "Volunteer Roles (fit)": "Keynote, mentor, judge",
        "Primary Audience": "Students and early-career builders",
        "Public URL": "https://www.insightsassociation.org/ai-hackathon",
        "Point(s) of Contact (published)": "Innovation Programs Team",
        "Contact Email / Phone (published)": "programs@iawest.org",
    },
    {
        "Event / Program": "ITC Conference",
        "Category": "Conference",
        "Recurrence (typical)": "Annual fall conference",
        "Host / Unit": "Insights Association",
        "Volunteer Roles (fit)": "Speaker, panelist",
        "Primary Audience": "Industry practitioners",
        "Public URL": "https://www.insightsassociation.org/itc",
        "Point(s) of Contact (published)": "Conference Team",
        "Contact Email / Phone (published)": "events@iawest.org",
    },
    {
        "Event / Program": "Bronco Startup Challenge",
        "Category": "Competition",
        "Recurrence (typical)": "Quarterly pitch challenge",
        "Host / Unit": "Cal Poly Pomona Entrepreneurship Center",
        "Volunteer Roles (fit)": "Judge, workshop lead",
        "Primary Audience": "Student founders",
        "Public URL": "https://www.insightsassociation.org/bronco-startup",
        "Point(s) of Contact (published)": "CPP Entrepreneurship Center",
        "Contact Email / Phone (published)": "startup@cpp.edu",
    },
    {
        "Event / Program": "IA West Annual Summit",
        "Category": "Summit",
        "Recurrence (typical)": "Annual member summit",
        "Host / Unit": "IA West Chapter",
        "Volunteer Roles (fit)": "Keynote, moderator, networking host",
        "Primary Audience": "Chapter members and sponsors",
        "Public URL": "https://www.insightsassociation.org/ia-west-summit",
        "Point(s) of Contact (published)": "Chapter Leadership",
        "Contact Email / Phone (published)": "leadership@iawest.org",
    },
    {
        "Event / Program": "Tech Career Fair",
        "Category": "Career Fair",
        "Recurrence (typical)": "Biannual campus fair",
        "Host / Unit": "West Coast Career Consortium",
        "Volunteer Roles (fit)": "Panelist, recruiter, mentor",
        "Primary Audience": "Undergraduate and graduate students",
        "Public URL": "https://www.insightsassociation.org/tech-career-fair",
        "Point(s) of Contact (published)": "Career Partnerships Team",
        "Contact Email / Phone (published)": "careerfair@iawest.org",
    },
]

EVENT_CALENDAR = [
    {
        "IA Event Date": "2026-04-09",
        "Region": "Los Angeles - West",
        "Nearby Universities": "Cal Poly Pomona, UCLA, USC",
        "Suggested Lecture Window": "Apr 7-10",
        "Course Alignment": "AI product strategy",
    },
    {
        "IA Event Date": "2026-04-18",
        "Region": "Bay Area",
        "Nearby Universities": "UC Berkeley, San Jose State, Stanford",
        "Suggested Lecture Window": "Apr 15-18",
        "Course Alignment": "Analytics and product insight",
    },
    {
        "IA Event Date": "2026-04-24",
        "Region": "San Diego",
        "Nearby Universities": "UC San Diego, SDSU",
        "Suggested Lecture Window": "Apr 22-25",
        "Course Alignment": "Founder storytelling and research",
    },
    {
        "IA Event Date": "2026-05-02",
        "Region": "Portland",
        "Nearby Universities": "Portland State, Oregon State",
        "Suggested Lecture Window": "Apr 30-May 3",
        "Course Alignment": "Ethics and civic innovation",
    },
    {
        "IA Event Date": "2026-05-14",
        "Region": "Phoenix",
        "Nearby Universities": "Arizona State, Grand Canyon University",
        "Suggested Lecture Window": "May 12-15",
        "Course Alignment": "Student talent development",
    },
]

PIPELINE_STAGE_ORDER = {
    "Matched": "0",
    "Contacted": "1",
    "Confirmed": "2",
    "Attended": "3",
    "Member Inquiry": "4",
}

PIPELINE_STAGE_SEQUENCE = (
    ["Matched"] * 15
    + ["Contacted"] * 12
    + ["Confirmed"] * 8
    + ["Attended"] * 4
    + ["Member Inquiry"]
)

CALENDAR_EVENTS = [
    {
        "event_id": "demo-event-01",
        "event_name": "AI for a Better Future Hackathon",
        "event_date": "2026-04-09",
        "region": "Los Angeles - West",
        "nearby_universities": ["Cal Poly Pomona", "UCLA", "USC"],
        "suggested_lecture_window": "Apr 7-10",
        "course_alignment": "AI product strategy",
        "coverage_status": "covered",
        "coverage_label": "IA covered",
        "coverage_ratio": 0.83,
        "assigned_volunteers": ["Dr. Sarah Chen", "Marcus Webb"],
        "assignment_count": 2,
        "open_slots": 1,
        "status_color": "#005394",
    },
    {
        "event_id": "demo-event-02",
        "event_name": "ITC Conference",
        "event_date": "2026-04-18",
        "region": "Bay Area",
        "nearby_universities": ["UC Berkeley", "San Jose State", "Stanford"],
        "suggested_lecture_window": "Apr 15-18",
        "course_alignment": "Analytics and product insight",
        "coverage_status": "partial",
        "coverage_label": "Partial coverage",
        "coverage_ratio": 0.52,
        "assigned_volunteers": ["Priya Nair"],
        "assignment_count": 1,
        "open_slots": 2,
        "status_color": "#c47c00",
    },
    {
        "event_id": "demo-event-03",
        "event_name": "Bronco Startup Challenge",
        "event_date": "2026-04-24",
        "region": "San Diego",
        "nearby_universities": ["UC San Diego", "SDSU"],
        "suggested_lecture_window": "Apr 22-25",
        "course_alignment": "Founder storytelling and research",
        "coverage_status": "covered",
        "coverage_label": "IA covered",
        "coverage_ratio": 0.78,
        "assigned_volunteers": ["Marcus Webb", "Lisa Chang"],
        "assignment_count": 2,
        "open_slots": 1,
        "status_color": "#005394",
    },
    {
        "event_id": "demo-event-04",
        "event_name": "IA West Annual Summit",
        "event_date": "2026-05-02",
        "region": "Portland",
        "nearby_universities": ["Portland State", "Oregon State"],
        "suggested_lecture_window": "Apr 30-May 3",
        "course_alignment": "Ethics and civic innovation",
        "coverage_status": "partial",
        "coverage_label": "Partial coverage",
        "coverage_ratio": 0.47,
        "assigned_volunteers": ["Dr. Emily Park"],
        "assignment_count": 1,
        "open_slots": 2,
        "status_color": "#c47c00",
    },
    {
        "event_id": "demo-event-05",
        "event_name": "Tech Career Fair",
        "event_date": "2026-05-14",
        "region": "Phoenix",
        "nearby_universities": ["Arizona State", "Grand Canyon University"],
        "suggested_lecture_window": "May 12-15",
        "course_alignment": "Student talent development",
        "coverage_status": "needs_coverage",
        "coverage_label": "Needs volunteers",
        "coverage_ratio": 0.18,
        "assigned_volunteers": [],
        "assignment_count": 0,
        "open_slots": 3,
        "status_color": "#d14343",
    },
]

CALENDAR_ASSIGNMENTS = [
    {
        "assignment_id": "demo-assignment-01",
        "event_id": "demo-event-01",
        "event_name": "AI for a Better Future Hackathon",
        "event_date": "2026-04-09",
        "calendar_event_date": "2026-04-09",
        "region": "Los Angeles - West",
        "calendar_region": "Los Angeles - West",
        "volunteer_name": "Dr. Sarah Chen",
        "speaker_name": "Dr. Sarah Chen",
        "volunteer_title": "VP Data Science",
        "volunteer_company": "TechBridge AI",
        "speaker_region": "Los Angeles - West",
        "stage": "Attended",
        "stage_order": 3,
        "match_score": 0.93,
        "rank": 1,
        "travel_burden": 0.12,
        "event_cadence": 0.28,
        "recent_assignment_count": 2,
        "days_since_last_assignment": 18,
        "volunteer_fatigue": 0.18,
        "recovery_status": "Available",
        "recovery_label": "Available",
        "coverage_status": "covered",
        "coverage_label": "IA covered",
        "status_color": "#005394",
        "status_tone": "blue",
        "coverage_ratio": 0.83,
    },
    {
        "assignment_id": "demo-assignment-02",
        "event_id": "demo-event-02",
        "event_name": "ITC Conference",
        "event_date": "2026-04-18",
        "calendar_event_date": "2026-04-18",
        "region": "Bay Area",
        "calendar_region": "Bay Area",
        "volunteer_name": "Priya Nair",
        "speaker_name": "Priya Nair",
        "volunteer_title": "Director of Product Analytics",
        "volunteer_company": "Cloud Harbor",
        "speaker_region": "Bay Area",
        "stage": "Confirmed",
        "stage_order": 2,
        "match_score": 0.89,
        "rank": 1,
        "travel_burden": 0.21,
        "event_cadence": 0.41,
        "recent_assignment_count": 3,
        "days_since_last_assignment": 9,
        "volunteer_fatigue": 0.46,
        "recovery_status": "Needs Rest",
        "recovery_label": "Needs Rest",
        "coverage_status": "partial",
        "coverage_label": "Partial coverage",
        "status_color": "#c47c00",
        "status_tone": "amber",
        "coverage_ratio": 0.52,
    },
    {
        "assignment_id": "demo-assignment-03",
        "event_id": "demo-event-03",
        "event_name": "Bronco Startup Challenge",
        "event_date": "2026-04-24",
        "calendar_event_date": "2026-04-24",
        "region": "San Diego",
        "calendar_region": "San Diego",
        "volunteer_name": "Marcus Webb",
        "speaker_name": "Marcus Webb",
        "volunteer_title": "Startup Advisor",
        "volunteer_company": "West Coast Ventures",
        "speaker_region": "San Diego",
        "stage": "Confirmed",
        "stage_order": 2,
        "match_score": 0.87,
        "rank": 1,
        "travel_burden": 0.18,
        "event_cadence": 0.36,
        "recent_assignment_count": 4,
        "days_since_last_assignment": 6,
        "volunteer_fatigue": 0.62,
        "recovery_status": "Needs Rest",
        "recovery_label": "Needs Rest",
        "coverage_status": "covered",
        "coverage_label": "IA covered",
        "status_color": "#005394",
        "status_tone": "blue",
        "coverage_ratio": 0.78,
    },
]

QR_STATS = {
    "generated_count": 5,
    "scan_count": 42,
    "membership_interest_count": 12,
    "conversion_rate": round(12 / 42, 4),
    "unique_speakers": 5,
    "unique_events": 5,
    "filters": {"speaker_name": None, "event_name": None, "referral_code": None},
    "referral_codes": [
        {
            "referral_code": "IAW-SARAHAI24",
            "speaker_name": "Dr. Sarah Chen",
            "speaker_title": "VP Data Science",
            "speaker_company": "TechBridge AI",
            "event_name": "AI for a Better Future Hackathon",
            "generated_at": "2026-03-18T09:00:00Z",
            "destination_url": "https://www.insightsassociation.org/join",
            "scan_url": "http://127.0.0.1:8000/api/qr/scan/IAW-SARAHAI24",
            "scan_count": 15,
            "membership_interest_count": 5,
            "conversion_rate": 0.3333,
            "last_scanned_at": "2026-03-24T18:05:00Z",
            "qr_data_url": None,
        },
        {
            "referral_code": "IAW-MARCUSITC",
            "speaker_name": "Marcus Webb",
            "speaker_title": "Startup Advisor",
            "speaker_company": "West Coast Ventures",
            "event_name": "ITC Conference",
            "generated_at": "2026-03-19T10:15:00Z",
            "destination_url": "https://www.insightsassociation.org/join",
            "scan_url": "http://127.0.0.1:8000/api/qr/scan/IAW-MARCUSITC",
            "scan_count": 9,
            "membership_interest_count": 2,
            "conversion_rate": 0.2222,
            "last_scanned_at": "2026-03-24T15:10:00Z",
            "qr_data_url": None,
        },
        {
            "referral_code": "IAW-PRIYABRON",
            "speaker_name": "Priya Nair",
            "speaker_title": "Director of Product Analytics",
            "speaker_company": "Cloud Harbor",
            "event_name": "Bronco Startup Challenge",
            "generated_at": "2026-03-20T08:45:00Z",
            "destination_url": "https://www.insightsassociation.org/join",
            "scan_url": "http://127.0.0.1:8000/api/qr/scan/IAW-PRIYABRON",
            "scan_count": 7,
            "membership_interest_count": 2,
            "conversion_rate": 0.2857,
            "last_scanned_at": "2026-03-23T13:20:00Z",
            "qr_data_url": None,
        },
        {
            "referral_code": "IAW-EMILYSUMM",
            "speaker_name": "Dr. Emily Park",
            "speaker_title": "Principal Research Scientist",
            "speaker_company": "Civic Data Lab",
            "event_name": "IA West Annual Summit",
            "generated_at": "2026-03-21T11:30:00Z",
            "destination_url": "https://www.insightsassociation.org/join",
            "scan_url": "http://127.0.0.1:8000/api/qr/scan/IAW-EMILYSUMM",
            "scan_count": 6,
            "membership_interest_count": 2,
            "conversion_rate": 0.3333,
            "last_scanned_at": "2026-03-23T17:45:00Z",
            "qr_data_url": None,
        },
        {
            "referral_code": "IAW-LISACAREER",
            "speaker_name": "Lisa Chang",
            "speaker_title": "Client Services Director",
            "speaker_company": "North Bay Research",
            "event_name": "Tech Career Fair",
            "generated_at": "2026-03-22T14:10:00Z",
            "destination_url": "https://www.insightsassociation.org/join",
            "scan_url": "http://127.0.0.1:8000/api/qr/scan/IAW-LISACAREER",
            "scan_count": 5,
            "membership_interest_count": 1,
            "conversion_rate": 0.2,
            "last_scanned_at": "2026-03-22T18:55:00Z",
            "qr_data_url": None,
        },
    ],
    "recent_scans": [
        {
            "referral_code": "IAW-SARAHAI24",
            "speaker_name": "Dr. Sarah Chen",
            "event_name": "AI for a Better Future Hackathon",
            "scanned_at": "2026-03-24T18:05:00Z",
            "membership_interest": True,
        },
        {
            "referral_code": "IAW-MARCUSITC",
            "speaker_name": "Marcus Webb",
            "event_name": "ITC Conference",
            "scanned_at": "2026-03-24T15:10:00Z",
            "membership_interest": False,
        },
        {
            "referral_code": "IAW-PRIYABRON",
            "speaker_name": "Priya Nair",
            "event_name": "Bronco Startup Challenge",
            "scanned_at": "2026-03-23T13:20:00Z",
            "membership_interest": True,
        },
    ],
}

MOCK_ROLES = [
    {"role": "student", "email": "student@cal.edu", "name": "Alex Rivera", "id": "student-001"},
    {"role": "event_coordinator", "email": "coordinator@cpp.edu", "name": "Jordan Lee", "id": "coord-001"},
    {"role": "ia_admin", "email": "admin@iawest.org", "name": "IA Admin", "id": "admin-001"},
]

STUDENTS = [
    {"student_id": "stu-001", "name": "Alex Rivera", "email": "alex.rivera@cal.edu", "school": "Cal Poly Pomona", "major": "Computer Science", "year": "Junior", "interests": "AI,machine learning,hackathons", "attendance_streak": 3, "events_attended": 2, "churn_risk": "low", "membership_interest": True, "suggested_connections": "stu-002,stu-003,stu-004,stu-006"},
    {"student_id": "stu-002", "name": "Maria Santos", "email": "maria.santos@uci.edu", "school": "UC Irvine", "major": "Data Science", "year": "Senior", "interests": "data engineering,analytics,Python", "attendance_streak": 1, "events_attended": 2, "churn_risk": "medium", "membership_interest": False, "suggested_connections": "stu-001,stu-004,stu-006,stu-008"},
    {"student_id": "stu-003", "name": "Kevin Park", "email": "kevin.park@ucr.edu", "school": "UC Riverside", "major": "Business Analytics", "year": "Sophomore", "interests": "fintech,product management,startups", "attendance_streak": 0, "events_attended": 1, "churn_risk": "high", "membership_interest": False, "suggested_connections": "stu-001,stu-005"},
    {"student_id": "stu-004", "name": "Priya Mehta", "email": "priya.mehta@csuf.edu", "school": "Cal State Fullerton", "major": "Marketing Analytics", "year": "Senior", "interests": "market research,consumer insights,DEI", "attendance_streak": 5, "events_attended": 7, "churn_risk": "low", "membership_interest": True, "suggested_connections": "stu-001,stu-006"},
    {"student_id": "stu-005", "name": "Tyler Johnson", "email": "tyler.j@cpp.edu", "school": "Cal Poly Pomona", "major": "Information Systems", "year": "Junior", "interests": "cybersecurity,networking,cloud", "attendance_streak": 2, "events_attended": 3, "churn_risk": "medium", "membership_interest": False, "suggested_connections": "stu-003,stu-007"},
    {"student_id": "stu-006", "name": "Sophia Chen", "email": "sophia.chen@usc.edu", "school": "USC", "major": "Computational Social Science", "year": "Freshman", "interests": "AI,ethics,civic tech", "attendance_streak": 2, "events_attended": 2, "churn_risk": "low", "membership_interest": True, "suggested_connections": "stu-004,stu-008"},
    {"student_id": "stu-007", "name": "Marcus Williams", "email": "m.williams@sdsu.edu", "school": "SDSU", "major": "Supply Chain Analytics", "year": "Senior", "interests": "operations,robotics,embedded systems", "attendance_streak": 0, "events_attended": 1, "churn_risk": "high", "membership_interest": False, "suggested_connections": "stu-005,stu-008"},
    {"student_id": "stu-008", "name": "Nia Thompson", "email": "nia.t@ucla.edu", "school": "UCLA", "major": "Statistics", "year": "Junior", "interests": "data science,healthcare AI,NLP", "attendance_streak": 4, "events_attended": 5, "churn_risk": "low", "membership_interest": True, "suggested_connections": "stu-006,stu-007"},
]

EVENT_COORDINATORS = [
    {"coordinator_id": "coord-001", "name": "Jordan Lee", "email": "jordan.lee@cpp.edu", "school": "Cal Poly Pomona", "department": "Innovation Programs", "hosted_events": "demo-event-01,demo-event-03", "contact_status": "active", "last_contact_date": "2026-04-01", "meeting_availability": "Mon,Wed,Fri 10am-3pm"},
    {"coordinator_id": "coord-002", "name": "Samantha Torres", "email": "s.torres@uci.edu", "school": "UC Irvine", "department": "Career Services", "hosted_events": "demo-event-02", "contact_status": "pending", "last_contact_date": "2026-03-25", "meeting_availability": "Tue,Thu 1pm-5pm"},
    {"coordinator_id": "coord-003", "name": "David Kim", "email": "d.kim@csuf.edu", "school": "Cal State Fullerton", "department": "Student Affairs", "hosted_events": "demo-event-05", "contact_status": "active", "last_contact_date": "2026-04-03", "meeting_availability": "Mon,Tue,Thu 9am-12pm"},
    {"coordinator_id": "coord-004", "name": "Lisa Nguyen", "email": "l.nguyen@ucsd.edu", "school": "UC San Diego", "department": "Entrepreneurship Center", "hosted_events": "", "contact_status": "new", "last_contact_date": "", "meeting_availability": "Wed,Fri 2pm-6pm"},
    {"coordinator_id": "coord-005", "name": "Marcus Brown", "email": "m.brown@usc.edu", "school": "USC", "department": "Computing Programs", "hosted_events": "demo-event-04", "contact_status": "active", "last_contact_date": "2026-04-05", "meeting_availability": "Mon-Fri 11am-2pm"},
]

STUDENT_REGISTRATIONS = [
    {"registration_id": "reg-001", "student_id": "stu-001", "event_id": "demo-event-01", "event_name": "AI for a Better Future Hackathon", "registered_at": "2026-03-20T10:00:00Z", "status": "attended", "check_in_time": "2026-04-09T08:30:00Z", "check_out_time": "2026-04-09T17:00:00Z"},
    {"registration_id": "reg-002", "student_id": "stu-001", "event_id": "demo-event-03", "event_name": "Bronco Startup Challenge", "registered_at": "2026-04-01T09:00:00Z", "status": "attended", "check_in_time": "2026-04-24T09:15:00Z", "check_out_time": "2026-04-24T16:45:00Z"},
    {"registration_id": "reg-003", "student_id": "stu-002", "event_id": "demo-event-02", "event_name": "ITC Conference", "registered_at": "2026-03-28T14:00:00Z", "status": "attended", "check_in_time": "2026-04-18T09:00:00Z", "check_out_time": "2026-04-18T16:30:00Z"},
    {"registration_id": "reg-004", "student_id": "stu-004", "event_id": "demo-event-01", "event_name": "AI for a Better Future Hackathon", "registered_at": "2026-03-19T11:00:00Z", "status": "attended", "check_in_time": "2026-04-09T08:45:00Z", "check_out_time": "2026-04-09T18:00:00Z"},
    {"registration_id": "reg-005", "student_id": "stu-004", "event_id": "demo-event-04", "event_name": "IA West Annual Summit", "registered_at": "2026-04-02T10:00:00Z", "status": "registered", "check_in_time": None, "check_out_time": None},
    {"registration_id": "reg-006", "student_id": "stu-005", "event_id": "demo-event-05", "event_name": "Tech Career Fair", "registered_at": "2026-04-10T12:00:00Z", "status": "registered", "check_in_time": None, "check_out_time": None},
    {"registration_id": "reg-007", "student_id": "stu-006", "event_id": "demo-event-01", "event_name": "AI for a Better Future Hackathon", "registered_at": "2026-03-22T15:00:00Z", "status": "attended", "check_in_time": "2026-04-09T09:00:00Z", "check_out_time": "2026-04-09T16:00:00Z"},
    {"registration_id": "reg-008", "student_id": "stu-008", "event_id": "demo-event-02", "event_name": "ITC Conference", "registered_at": "2026-03-30T09:00:00Z", "status": "attended", "check_in_time": "2026-04-18T08:30:00Z", "check_out_time": "2026-04-18T17:00:00Z"},
    {"registration_id": "reg-009", "student_id": "stu-003", "event_id": "demo-event-03", "event_name": "Bronco Startup Challenge", "registered_at": "2026-04-05T11:00:00Z", "status": "attended", "check_in_time": "2026-04-24T09:30:00Z", "check_out_time": "2026-04-24T17:00:00Z"},
    {"registration_id": "reg-010", "student_id": "stu-007", "event_id": "demo-event-05", "event_name": "Tech Career Fair", "registered_at": "2026-04-08T14:00:00Z", "status": "registered", "check_in_time": None, "check_out_time": None},
    {"registration_id": "reg-011", "student_id": "stu-001", "event_id": "demo-event-04", "event_name": "IA West Annual Summit", "registered_at": "2026-04-03T10:00:00Z", "status": "registered", "check_in_time": None, "check_out_time": None},
    {"registration_id": "reg-012", "student_id": "stu-008", "event_id": "demo-event-04", "event_name": "IA West Annual Summit", "registered_at": "2026-04-04T09:00:00Z", "status": "registered", "check_in_time": None, "check_out_time": None},
    # Shared room with stu-001 / stu-004 / stu-006 at the hackathon (Connect tab: co-attendance signal)
    {"registration_id": "reg-013", "student_id": "stu-002", "event_id": "demo-event-01", "event_name": "AI for a Better Future Hackathon", "registered_at": "2026-03-18T12:00:00Z", "status": "attended", "check_in_time": "2026-04-09T08:15:00Z", "check_out_time": "2026-04-09T16:45:00Z"},
]

OUTREACH_THREADS = [
    {"thread_id": "thread-001", "coordinator_id": "coord-001", "event_id": "demo-event-01", "ia_contact": "Dr. Sarah Chen", "subject": "Hackathon Speaker Coordination", "status": "confirmed", "last_message_at": "2026-04-02T10:00:00Z", "message_count": 4, "next_action": "Send ICS invite"},
    {"thread_id": "thread-002", "coordinator_id": "coord-002", "event_id": "demo-event-02", "ia_contact": "Priya Nair", "subject": "ITC Conference Panelist Setup", "status": "in_progress", "last_message_at": "2026-04-05T14:00:00Z", "message_count": 2, "next_action": "Confirm availability"},
    {"thread_id": "thread-003", "coordinator_id": "coord-003", "event_id": "demo-event-05", "ia_contact": "Lisa Chang", "subject": "Tech Career Fair Recruiter Slot", "status": "awaiting_response", "last_message_at": "2026-04-01T11:00:00Z", "message_count": 1, "next_action": "Follow up in 3 days"},
    {"thread_id": "thread-004", "coordinator_id": "coord-001", "event_id": "demo-event-03", "ia_contact": "Marcus Webb", "subject": "Startup Challenge Judge Invitation", "status": "in_progress", "last_message_at": "2026-04-06T09:00:00Z", "message_count": 3, "next_action": "Finalize logistics"},
    {"thread_id": "thread-005", "coordinator_id": "coord-005", "event_id": "demo-event-04", "ia_contact": "Dr. Emily Park", "subject": "Summit Ethics Panel Speaker", "status": "confirmed", "last_message_at": "2026-04-07T16:00:00Z", "message_count": 5, "next_action": "Send final materials"},
    {"thread_id": "thread-006", "coordinator_id": "coord-004", "event_id": "demo-event-05", "ia_contact": "", "subject": "New Partnership Inquiry", "status": "new", "last_message_at": "", "message_count": 0, "next_action": "Assign IA contact"},
]

MEETING_BOOKINGS = [
    {"booking_id": "booking-001", "thread_id": "thread-001", "coordinator_id": "coord-001", "ia_contact": "Dr. Sarah Chen", "event_id": "demo-event-01", "title": "Pre-event speaker briefing", "scheduled_at": "2026-04-07T10:00:00Z", "duration_minutes": 30, "status": "confirmed", "meeting_link": "https://meet.iawest.org/hackathon-brief", "notes": "Review logistics and presentation slots"},
    {"booking_id": "booking-002", "thread_id": "thread-004", "coordinator_id": "coord-001", "ia_contact": "Marcus Webb", "event_id": "demo-event-03", "title": "Judge orientation call", "scheduled_at": "2026-04-12T14:00:00Z", "duration_minutes": 45, "status": "pending_confirmation", "meeting_link": "https://meet.iawest.org/startup-orient", "notes": "Walk through judging criteria"},
    {"booking_id": "booking-003", "thread_id": "thread-002", "coordinator_id": "coord-002", "ia_contact": "Priya Nair", "event_id": "demo-event-02", "title": "Panelist prep session", "scheduled_at": "2026-04-16T11:00:00Z", "duration_minutes": 60, "status": "confirmed", "meeting_link": "https://meet.iawest.org/itc-panel", "notes": "Discuss panel topics and format"},
    {"booking_id": "booking-004", "thread_id": "thread-005", "coordinator_id": "coord-005", "ia_contact": "Dr. Emily Park", "event_id": "demo-event-04", "title": "Ethics panel planning meeting", "scheduled_at": "2026-04-25T15:00:00Z", "duration_minutes": 45, "status": "confirmed", "meeting_link": "https://meet.iawest.org/summit-ethics", "notes": "Finalize discussion questions"},
    {"booking_id": "booking-005", "thread_id": "thread-003", "coordinator_id": "coord-003", "ia_contact": "Lisa Chang", "event_id": "demo-event-05", "title": "Career fair orientation", "scheduled_at": "2026-04-30T10:00:00Z", "duration_minutes": 30, "status": "pending_confirmation", "meeting_link": "https://meet.iawest.org/careerfair-orient", "notes": "Recruiter booth setup instructions"},
]

RETENTION_NUDGES = [
    {"student_id": "stu-001", "nudge_type": "next_event", "message": "The Bronco Startup Challenge is coming up on Apr 24 — you're already registered!", "event_id": "demo-event-03", "cta_label": "View event details", "points_earned": 120},
    {"student_id": "stu-002", "nudge_type": "re_engage", "message": "It's been a while since your last event. The ITC Conference is a great next step for data professionals.", "event_id": "demo-event-02", "cta_label": "Learn more", "points_earned": 50},
    {"student_id": "stu-003", "nudge_type": "re_engage", "message": "You signed up for the Bronco Startup Challenge — don't miss out! It's in 10 days.", "event_id": "demo-event-03", "cta_label": "Add to calendar", "points_earned": 30},
    {"student_id": "stu-004", "nudge_type": "membership", "message": "You've attended 7 IA events! You qualify for IA West student membership. Join to unlock networking, mentorship, and career resources.", "event_id": None, "cta_label": "Explore membership", "points_earned": 300},
    {"student_id": "stu-005", "nudge_type": "next_event", "message": "The Tech Career Fair is your next chance to meet cybersecurity and cloud recruiters on Aug 15.", "event_id": "demo-event-05", "cta_label": "Prepare now", "points_earned": 60},
    {"student_id": "stu-006", "nudge_type": "streak", "message": "You're on a 2-event streak! Attend the IA West Annual Summit to hit 3 and earn bonus recognition.", "event_id": "demo-event-04", "cta_label": "Register now", "points_earned": 180},
    {"student_id": "stu-007", "nudge_type": "re_engage", "message": "No events attended yet this term. The Tech Career Fair has supply chain and operations roles — a perfect fit for your major.", "event_id": "demo-event-05", "cta_label": "Register free", "points_earned": 20},
    {"student_id": "stu-008", "nudge_type": "membership", "message": "You've attended 5 events and flagged membership interest. Complete your profile to apply for IA West student membership.", "event_id": None, "cta_label": "Complete profile", "points_earned": 280},
]

FEEDBACK_STATS = {
    "total_feedback": 8,
    "accepted": 5,
    "declined": 3,
    "acceptance_rate": 0.625,
    "attended_count": 4,
    "membership_interest_count": 3,
    "membership_interest_rate": 0.6,
    "average_coordinator_rating": 4.2,
    "average_match_score_accepted": 0.86,
    "average_match_score_declined": 0.68,
    "pain_score": 18.4,
    "decline_reasons": [
        {"reason": "Schedule conflict", "count": 2},
        {"reason": "Topic mismatch", "count": 1},
    ],
    "event_outcomes": [
        {"outcome": "attended", "count": 4},
        {"outcome": "rescheduled", "count": 1},
    ],
    "trend": [
        {"date": "2026-03-12", "feedback_count": 2, "accepted": 1, "declined": 1, "acceptance_rate": 0.5},
        {"date": "2026-03-16", "feedback_count": 2, "accepted": 1, "declined": 1, "acceptance_rate": 0.5},
        {"date": "2026-03-20", "feedback_count": 2, "accepted": 2, "declined": 0, "acceptance_rate": 1.0},
        {"date": "2026-03-24", "feedback_count": 2, "accepted": 1, "declined": 1, "acceptance_rate": 0.5},
    ],
    "default_weights": {
        "topic_relevance": 0.22,
        "role_fit": 0.18,
        "geographic_proximity": 0.18,
        "calendar_fit": 0.12,
        "volunteer_fatigue": 0.10,
        "event_urgency": 0.05,
        "coverage_diversity": 0.05,
        "historical_conversion": 0.05,
        "student_interest": 0.05,
    },
    "current_weights": {
        "topic_relevance": 0.24,
        "role_fit": 0.17,
        "geographic_proximity": 0.16,
        "calendar_fit": 0.13,
        "volunteer_fatigue": 0.11,
        "event_urgency": 0.05,
        "coverage_diversity": 0.05,
        "historical_conversion": 0.05,
        "student_interest": 0.04,
    },
    "suggested_weights": {
        "topic_relevance": 0.24,
        "role_fit": 0.17,
        "geographic_proximity": 0.16,
        "calendar_fit": 0.13,
        "volunteer_fatigue": 0.11,
        "event_urgency": 0.05,
        "coverage_diversity": 0.05,
        "historical_conversion": 0.05,
        "student_interest": 0.04,
    },
    "recommended_adjustments": [
        {
            "factor": "topic_relevance",
            "from_weight": 0.22,
            "to_weight": 0.24,
            "delta": 0.02,
            "rationale": "Accepted matches consistently aligned to event themes.",
        },
        {
            "factor": "volunteer_fatigue",
            "from_weight": 0.10,
            "to_weight": 0.11,
            "delta": 0.01,
            "rationale": "Recent staffing load should weigh slightly more heavily for follow-up scheduling.",
        },
    ],
    "weight_history": [
        {
            "timestamp": "2026-03-14T08:00:00Z",
            "total_feedback": 3,
            "accepted": 2,
            "declined": 1,
            "acceptance_rate": 0.6667,
            "pain_score": 22.1,
            "weights": {
                "topic_relevance": 0.23,
                "role_fit": 0.18,
                "geographic_proximity": 0.17,
                "calendar_fit": 0.12,
                "volunteer_fatigue": 0.10,
                "event_urgency": 0.05,
                "coverage_diversity": 0.05,
                "historical_conversion": 0.05,
                "student_interest": 0.05,
            },
            "baseline_weights": {
                "topic_relevance": 0.22,
                "role_fit": 0.18,
                "geographic_proximity": 0.18,
                "calendar_fit": 0.12,
                "volunteer_fatigue": 0.10,
                "event_urgency": 0.05,
                "coverage_diversity": 0.05,
                "historical_conversion": 0.05,
                "student_interest": 0.05,
            },
            "adjustments": [
                {
                    "factor": "topic_relevance",
                    "from_weight": 0.22,
                    "to_weight": 0.23,
                    "delta": 0.01,
                    "rationale": "Early wins favored topic-aligned speakers.",
                }
            ],
        },
        {
            "timestamp": "2026-03-24T09:30:00Z",
            "total_feedback": 8,
            "accepted": 5,
            "declined": 3,
            "acceptance_rate": 0.625,
            "pain_score": 18.4,
            "weights": {
                "topic_relevance": 0.24,
                "role_fit": 0.17,
                "geographic_proximity": 0.16,
                "calendar_fit": 0.13,
                "volunteer_fatigue": 0.11,
                "event_urgency": 0.05,
                "coverage_diversity": 0.05,
                "historical_conversion": 0.05,
                "student_interest": 0.04,
            },
            "baseline_weights": {
                "topic_relevance": 0.22,
                "role_fit": 0.18,
                "geographic_proximity": 0.18,
                "calendar_fit": 0.12,
                "volunteer_fatigue": 0.10,
                "event_urgency": 0.05,
                "coverage_diversity": 0.05,
                "historical_conversion": 0.05,
                "student_interest": 0.05,
            },
            "adjustments": [
                {
                    "factor": "topic_relevance",
                    "from_weight": 0.22,
                    "to_weight": 0.24,
                    "delta": 0.02,
                    "rationale": "Accepted matches consistently aligned to event themes.",
                },
                {
                    "factor": "volunteer_fatigue",
                    "from_weight": 0.10,
                    "to_weight": 0.11,
                    "delta": 0.01,
                    "rationale": "Recent staffing load should weigh slightly more heavily for follow-up scheduling.",
                },
            ],
        },
    ],
}


def build_pipeline_rows() -> list[dict[str, str]]:
    speaker_names = [entry["name"] for entry in SPECIALISTS]
    event_names = [entry["Event / Program"] for entry in CPP_EVENTS]
    rows: list[dict[str, str]] = []
    for index, stage in enumerate(PIPELINE_STAGE_SEQUENCE):
        event_name = event_names[index % len(event_names)]
        speaker_name = speaker_names[(index * 3) % len(speaker_names)]
        score = max(0.58, 0.94 - (index * 0.009))
        rows.append(
            {
                "event_name": event_name,
                "speaker_name": speaker_name,
                "match_score": f"{score:.2f}",
                "rank": str((index % 8) + 1),
                "stage": stage,
                "stage_order": PIPELINE_STAGE_ORDER[stage],
            }
        )
    return rows


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE specialists (
            name TEXT,
            board_role TEXT,
            metro_region TEXT,
            company TEXT,
            title TEXT,
            expertise_tags TEXT,
            initials TEXT
        );

        CREATE TABLE cpp_events (
            "Event / Program" TEXT,
            Category TEXT,
            "Recurrence (typical)" TEXT,
            "Host / Unit" TEXT,
            "Volunteer Roles (fit)" TEXT,
            "Primary Audience" TEXT,
            "Public URL" TEXT,
            "Point(s) of Contact (published)" TEXT,
            "Contact Email / Phone (published)" TEXT
        );

        CREATE TABLE pipeline (
            event_name TEXT,
            speaker_name TEXT,
            match_score TEXT,
            rank TEXT,
            stage TEXT,
            stage_order TEXT
        );

        CREATE TABLE event_calendar (
            "IA Event Date" TEXT,
            Region TEXT,
            "Nearby Universities" TEXT,
            "Suggested Lecture Window" TEXT,
            "Course Alignment" TEXT
        );

        CREATE TABLE calendar_events (
            event_id TEXT,
            event_name TEXT,
            event_date TEXT,
            region TEXT,
            nearby_universities TEXT,
            suggested_lecture_window TEXT,
            course_alignment TEXT,
            coverage_status TEXT,
            coverage_label TEXT,
            coverage_ratio REAL,
            assigned_volunteers TEXT,
            assignment_count INTEGER,
            open_slots INTEGER,
            status_color TEXT
        );

        CREATE TABLE calendar_assignments (
            assignment_id TEXT,
            event_id TEXT,
            event_name TEXT,
            event_date TEXT,
            calendar_event_date TEXT,
            region TEXT,
            calendar_region TEXT,
            volunteer_name TEXT,
            speaker_name TEXT,
            volunteer_title TEXT,
            volunteer_company TEXT,
            speaker_region TEXT,
            stage TEXT,
            stage_order INTEGER,
            match_score REAL,
            rank INTEGER,
            travel_burden REAL,
            event_cadence REAL,
            recent_assignment_count INTEGER,
            days_since_last_assignment INTEGER,
            volunteer_fatigue REAL,
            recovery_status TEXT,
            recovery_label TEXT,
            coverage_status TEXT,
            coverage_label TEXT,
            status_color TEXT,
            status_tone TEXT,
            coverage_ratio REAL
        );

        CREATE TABLE qr_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload_json TEXT NOT NULL
        );

        CREATE TABLE feedback_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload_json TEXT NOT NULL
        );

        CREATE TABLE students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            school TEXT,
            major TEXT,
            year TEXT,
            interests TEXT,
            attendance_streak INTEGER,
            events_attended INTEGER,
            churn_risk TEXT,
            membership_interest INTEGER,
            suggested_connections TEXT
        );

        CREATE TABLE mock_roles (
            role TEXT,
            email TEXT PRIMARY KEY,
            name TEXT,
            id TEXT
        );

        CREATE TABLE event_coordinators (
            coordinator_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            school TEXT,
            department TEXT,
            hosted_events TEXT,
            contact_status TEXT,
            last_contact_date TEXT,
            meeting_availability TEXT
        );

        CREATE TABLE student_registrations (
            registration_id TEXT PRIMARY KEY,
            student_id TEXT,
            event_id TEXT,
            event_name TEXT,
            registered_at TEXT,
            status TEXT,
            check_in_time TEXT,
            check_out_time TEXT
        );

        CREATE TABLE outreach_threads (
            thread_id TEXT PRIMARY KEY,
            coordinator_id TEXT,
            event_id TEXT,
            ia_contact TEXT,
            subject TEXT,
            status TEXT,
            last_message_at TEXT,
            message_count INTEGER,
            next_action TEXT
        );

        CREATE TABLE meeting_bookings (
            booking_id TEXT PRIMARY KEY,
            thread_id TEXT,
            coordinator_id TEXT,
            ia_contact TEXT,
            event_id TEXT,
            title TEXT,
            scheduled_at TEXT,
            duration_minutes INTEGER,
            status TEXT,
            meeting_link TEXT,
            notes TEXT
        );

        CREATE TABLE retention_nudges (
            student_id TEXT PRIMARY KEY,
            nudge_type TEXT,
            message TEXT,
            event_id TEXT,
            cta_label TEXT,
            points_earned INTEGER
        );
        """
    )


def insert_seed_data(connection: sqlite3.Connection) -> None:
    connection.executemany(
        """
        INSERT INTO specialists (
            name, board_role, metro_region, company, title, expertise_tags, initials
        ) VALUES (
            :name, :board_role, :metro_region, :company, :title, :expertise_tags, :initials
        )
        """,
        SPECIALISTS,
    )
    connection.executemany(
        """
        INSERT INTO cpp_events (
            "Event / Program", Category, "Recurrence (typical)", "Host / Unit",
            "Volunteer Roles (fit)", "Primary Audience", "Public URL",
            "Point(s) of Contact (published)", "Contact Email / Phone (published)"
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        [
            (
                record["Event / Program"],
                record["Category"],
                record["Recurrence (typical)"],
                record["Host / Unit"],
                record["Volunteer Roles (fit)"],
                record["Primary Audience"],
                record["Public URL"],
                record["Point(s) of Contact (published)"],
                record["Contact Email / Phone (published)"],
            )
            for record in CPP_EVENTS
        ],
    )
    connection.executemany(
        """
        INSERT INTO pipeline (
            event_name, speaker_name, match_score, rank, stage, stage_order
        ) VALUES (
            :event_name, :speaker_name, :match_score, :rank, :stage, :stage_order
        )
        """,
        build_pipeline_rows(),
    )
    connection.executemany(
        """
        INSERT INTO event_calendar (
            "IA Event Date", Region, "Nearby Universities",
            "Suggested Lecture Window", "Course Alignment"
        ) VALUES (
            ?, ?, ?, ?, ?
        )
        """,
        [
            (
                record["IA Event Date"],
                record["Region"],
                record["Nearby Universities"],
                record["Suggested Lecture Window"],
                record["Course Alignment"],
            )
            for record in EVENT_CALENDAR
        ],
    )
    connection.executemany(
        """
        INSERT INTO calendar_events (
            event_id, event_name, event_date, region, nearby_universities,
            suggested_lecture_window, course_alignment, coverage_status,
            coverage_label, coverage_ratio, assigned_volunteers,
            assignment_count, open_slots, status_color
        ) VALUES (
            :event_id, :event_name, :event_date, :region, :nearby_universities,
            :suggested_lecture_window, :course_alignment, :coverage_status,
            :coverage_label, :coverage_ratio, :assigned_volunteers,
            :assignment_count, :open_slots, :status_color
        )
        """,
        [
            {
                **record,
                "nearby_universities": json.dumps(record["nearby_universities"]),
                "assigned_volunteers": json.dumps(record["assigned_volunteers"]),
            }
            for record in CALENDAR_EVENTS
        ],
    )
    connection.executemany(
        """
        INSERT INTO calendar_assignments (
            assignment_id, event_id, event_name, event_date, calendar_event_date,
            region, calendar_region, volunteer_name, speaker_name, volunteer_title,
            volunteer_company, speaker_region, stage, stage_order, match_score, rank,
            travel_burden, event_cadence, recent_assignment_count,
            days_since_last_assignment, volunteer_fatigue, recovery_status,
            recovery_label, coverage_status, coverage_label, status_color,
            status_tone, coverage_ratio
        ) VALUES (
            :assignment_id, :event_id, :event_name, :event_date, :calendar_event_date,
            :region, :calendar_region, :volunteer_name, :speaker_name, :volunteer_title,
            :volunteer_company, :speaker_region, :stage, :stage_order, :match_score, :rank,
            :travel_burden, :event_cadence, :recent_assignment_count,
            :days_since_last_assignment, :volunteer_fatigue, :recovery_status,
            :recovery_label, :coverage_status, :coverage_label, :status_color,
            :status_tone, :coverage_ratio
        )
        """,
        CALENDAR_ASSIGNMENTS,
    )
    connection.execute(
        "INSERT INTO qr_stats (payload_json) VALUES (?)",
        (json.dumps(QR_STATS, sort_keys=True),),
    )
    connection.execute(
        "INSERT INTO feedback_stats (payload_json) VALUES (?)",
        (json.dumps(FEEDBACK_STATS, sort_keys=True),),
    )
    connection.executemany(
        """
        INSERT INTO students (
            student_id, name, email, school, major, year, interests,
            attendance_streak, events_attended, churn_risk, membership_interest,
            suggested_connections
        ) VALUES (
            :student_id, :name, :email, :school, :major, :year, :interests,
            :attendance_streak, :events_attended, :churn_risk, :membership_interest,
            :suggested_connections
        )
        """,
        [
            {**record, "membership_interest": int(record["membership_interest"])}
            for record in STUDENTS
        ],
    )
    connection.executemany(
        "INSERT INTO mock_roles (role, email, name, id) VALUES (:role, :email, :name, :id)",
        MOCK_ROLES,
    )
    connection.executemany(
        """
        INSERT INTO event_coordinators (
            coordinator_id, name, email, school, department, hosted_events,
            contact_status, last_contact_date, meeting_availability
        ) VALUES (
            :coordinator_id, :name, :email, :school, :department, :hosted_events,
            :contact_status, :last_contact_date, :meeting_availability
        )
        """,
        EVENT_COORDINATORS,
    )
    connection.executemany(
        """
        INSERT INTO student_registrations (
            registration_id, student_id, event_id, event_name, registered_at,
            status, check_in_time, check_out_time
        ) VALUES (
            :registration_id, :student_id, :event_id, :event_name, :registered_at,
            :status, :check_in_time, :check_out_time
        )
        """,
        STUDENT_REGISTRATIONS,
    )
    connection.executemany(
        """
        INSERT INTO outreach_threads (
            thread_id, coordinator_id, event_id, ia_contact, subject, status,
            last_message_at, message_count, next_action
        ) VALUES (
            :thread_id, :coordinator_id, :event_id, :ia_contact, :subject, :status,
            :last_message_at, :message_count, :next_action
        )
        """,
        OUTREACH_THREADS,
    )
    connection.executemany(
        """
        INSERT INTO meeting_bookings (
            booking_id, thread_id, coordinator_id, ia_contact, event_id, title,
            scheduled_at, duration_minutes, status, meeting_link, notes
        ) VALUES (
            :booking_id, :thread_id, :coordinator_id, :ia_contact, :event_id, :title,
            :scheduled_at, :duration_minutes, :status, :meeting_link, :notes
        )
        """,
        MEETING_BOOKINGS,
    )
    connection.executemany(
        """
        INSERT INTO retention_nudges (
            student_id, nudge_type, message, event_id, cta_label, points_earned
        ) VALUES (
            :student_id, :nudge_type, :message, :event_id, :cta_label, :points_earned
        )
        """,
        RETENTION_NUDGES,
    )


def main() -> None:
    DEMO_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DEMO_DB_PATH.exists():
        DEMO_DB_PATH.unlink()

    connection = sqlite3.connect(DEMO_DB_PATH)
    try:
        create_schema(connection)
        insert_seed_data(connection)
        connection.commit()
    finally:
        connection.close()

    print(f"Seeded demo database: {DEMO_DB_PATH}")


if __name__ == "__main__":
    main()

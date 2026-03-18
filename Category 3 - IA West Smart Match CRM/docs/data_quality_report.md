# Data Quality Report — IA SmartMatch

**Generated:** 2026-03-18 (Sprint 0, Task A0.2)
**Total records:** 77

---

## data_speaker_profiles.csv

- **Rows:** 18
- **Columns:** 6
- **Encoding:** utf-8

### Null Values

| Column | Null Count |
|--------|-----------|
| Name | 0 |
| Board Role | 0 |
| Metro Region | 0 |
| Company | 0 |
| Title | 0 |
| Expertise Tags | 0 |

### Issues

- Unexpected extra columns: [] *(none)*
- Note: Two speakers have parenthetical company names: Sean McKenna `(prev. Luth, Toluna)` and Calvin Friesth `(consultative client development)`. These are not true NULLs but may produce slightly noisy embeddings. Flagged for Sprint 1.
- Note: Adam Portner has a long company field: `(prev. RealityMine, Prodege, Dynata, Metrixlab, Circana)` — same parenthetical concern.

---

## data_cpp_events_contacts.csv

- **Rows:** 15
- **Columns:** 9
- **Encoding:** utf-8

### Null Values

| Column | Null Count |
|--------|-----------|
| Event / Program | 0 |
| Category | 0 |
| Recurrence (typical) | 0 |
| Host / Unit | 0 |
| Volunteer Roles (fit) | 0 |
| Primary Audience | 0 |
| Public URL | 0 |
| Point(s) of Contact (published) | 0 |
| Contact Email / Phone (published) | 0 |

### Issues

- Note: Some events have multiple rows with different contacts — Bronco Startup Challenge appears twice (SIIL general + director contact), OUR appears three times (RSCA, director contact, CARS). Total: 15 data rows. Deduplication by event name is a Sprint 1 concern.
- Note: `Contact Email / Phone (published)` contains mixed formats: some rows say "See page", some have phone numbers, some have emails. Treat as raw string.

---

## data_cpp_course_schedule.csv

- **Rows:** 35
- **Columns:** 10
- **Encoding:** utf-8

### Null Values

| Column | Null Count |
|--------|-----------|
| Instructor | 0 |
| Course | 0 |
| Section | 0 |
| Title | 0 |
| Days | 0 |
| Start Time | 0 |
| End Time | 0 |
| Enrl Cap | 0 |
| Mode | 0 |
| Guest Lecture Fit | 0 |

### Issues

None detected.

---

## data_event_calendar.csv

- **Rows:** 9
- **Columns:** 5
- **Encoding:** utf-8

### Null Values

| Column | Null Count |
|--------|-----------|
| IA Event Date | 0 |
| Region | 0 |
| Nearby Universities | 0 |
| Suggested Lecture Window | 0 |
| Course Alignment | 0 |

### Issues

- Note: `Suggested Lecture Window` contains en-dash characters (–) instead of hyphens (-) in some rows. No functional impact.

---

## Join Key Alignment

### Speaker Metro Region <-> Calendar Region

| Calendar Region | Speaker Metro Regions Available | Aligned? |
|----------------|--------------------------------|----------|
| Portland | Portland (Katie Nelson) | Yes — exact match |
| San Diego | San Diego (Sean McKenna, Monica Voss) | Yes — exact match |
| Los Angeles | Los Angeles (Donna Flynn, Calvin Friesth, Amber Jawaid), Los Angeles — West (Amanda Keller-Grill), Los Angeles — North (Ashley Le Blanc, Molly Strawn), Los Angeles — East (Dr. Yufan Lin), Los Angeles — Long Beach (Rob Kaiser) | Partial — sub-regions need fuzzy match |
| San Francisco | San Francisco (Katrina Noelle, Liz O'Hara, Adam Portner, Laurie Bae) | Yes — exact match |
| Seattle | Seattle (Greg Carter) | Yes — exact match |
| Ventura / Thousand Oaks | Ventura / Thousand Oaks (Travis Miller, Shana DeMarinis) | Yes — exact match |
| Orange County / Long Beach | Los Angeles — Long Beach (Rob Kaiser) | Partial — need mapping: "Long Beach" in calendar ≠ "Los Angeles — Long Beach" in speakers |

**Action:** Sprint 1 must build a metro region normalization dictionary.

### Course Guest Lecture Fit Distribution

| Fit Level | Count | Percentage |
|-----------|-------|-----------|
| High | 10 | 28.6% |
| Medium | 16 | 45.7% |
| Low | 9 | 25.7% |

**High-Fit Courses (Priority):** IBM 4121, IBM 3302 (×2), GBA 6520, GBA 6830, IBM 3202 (×2), IBM 4112 (×3)

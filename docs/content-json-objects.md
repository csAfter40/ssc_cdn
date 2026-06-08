# Content JSON object shapes

Locale-specific copy lives under `assets/content/<locale>/` (for example `en` and `tr`). Each locale has four top-level JSON **arrays** of objects:

| File | Array of |
|------|----------|
| `categories.json` | Category |
| `subcategories.json` | Subcategory |
| `scripts.json` | Script |
| `situations.json` | Situation |

Objects are identified by `id`. Relationships are by string reference: a subcategory’s `categoryId` must match a category’s `id`; a script’s `subcategoryId` must match a subcategory’s `id`, and its `category` must match that subcategory’s parent category `id`; a situation’s `correctScriptId`, `distractorPrimary`, and `distractorSecondary` must each match a **Script** `id` in the same locale.

---

## Category

**File:** `categories.json`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable identifier (e.g. `greeting`). |
| `title` | string | Display name for the category. |
| `icon` | string | Single emoji or icon character shown in the UI. |
| `sortOrder` | number | Ordering among categories (lower first). |
| `isHidden` | boolean | Whether the category is hidden from normal browsing. |

**Example:**

```json
{
  "id": "greeting",
  "title": "Greetings",
  "icon": "👋",
  "sortOrder": 1,
  "isHidden": false
}
```

---

## Subcategory

**File:** `subcategories.json`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable identifier (e.g. `greet-casual`). |
| `categoryId` | string | Parent category; must equal a **Category** `id`. |
| `title` | string | Display name for the subcategory. |
| `icon` | string | Single emoji or icon character shown in the UI. |
| `sortOrder` | number | Ordering within the parent category (lower first). |

**Example:**

```json
{
  "id": "greet-casual",
  "categoryId": "greeting",
  "title": "Casual Greetings",
  "icon": "😊",
  "sortOrder": 1
}
```

---

## Script

**File:** `scripts.json`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable identifier for the script. |
| `title` | string | Display title for the script. |
| `category` | string | Category key; must match a **Category** `id`. |
| `subcategoryId` | string | Subcategory key; must match a **Subcategory** `id` under that category. |
| `difficulty` | number | Difficulty level (e.g. `1`, `2` in current data). |
| `tone` | string | Tone label (e.g. `casual`, `formal` in current data). |
| `steps` | array | Ordered list of **Step** objects (see below). |
| `isCustom` | boolean | Whether the script is user-created vs bundled content. |

### Step (nested in `steps`)

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Instruction or line shown for this step. |
| `emoji` | string | Emoji associated with the step (optional in principle; present on all bundled steps today). |
| `image` | string \| null | Optional image filename for the step. 

**Example:**

```json
{
  "id": "greet-cas-1",
  "title": "Meeting Someone New",
  "category": "greeting",
  "subcategoryId": "greet-casual",
  "difficulty": 1,
  "tone": "casual",
  "steps": [
    {
      "text": "Look at their face or nose area",
      "emoji": "👀",
      "image": "greet-cas-1_1.png"
    }
  ],
  "isCustom": false
}
```

---

## Situation

**File:** `situations.json`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable identifier (e.g. `sit-greet-cas-1-001`). |
| `title` | string | Short label for the scenario. |
| `text` | string | The scenario description shown to the learner. |
| `correctScriptId` | string | Script that best fits the situation; must equal a **Script** `id`. |
| `distractorPrimary` | string | Plausible wrong answer; must equal a **Script** `id`. |
| `distractorSecondary` | string | Second plausible wrong answer; must equal a **Script** `id`. |
| `explanation` | string | Feedback explaining why the correct script fits. |

**Example:**

```json
{
  "id": "sit-greet-cas-1-001",
  "title": "Birthday party, empty seat beside you",
  "text": "You're at a friend's birthday party and someone you've never met sits down next to you. They smile and seem to be waiting for someone to say hello first.",
  "correctScriptId": "greet-cas-1",
  "distractorPrimary": "greet-for-1",
  "distractorSecondary": "talk-weath-1",
  "explanation": "This is a casual first meeting in a relaxed social setting. A brief, friendly self-introduction is exactly right, and \"Meeting Someone New\" covers each step."
}
```

---

## Consistency checks in this repo

- **`tests/test_content_ids.py`** — Within each JSON file, every top-level object’s `id` must be unique (categories, subcategories, scripts).
- **`tests/test_content_lengths.py`** — Enforced upper bounds for bundled content strings and step counts: script `title` (70), each step `text` (150), at most 12 steps per script; category `title` (40).
- **`tests/test_situations.py`** — Within each `situations.json`, every situation `id` must be unique; `correctScriptId`, `distractorPrimary`, and `distractorSecondary` must reference script ids present in that locale’s `scripts.json`.

When adding locales, keep the same object shapes and `id` values so the app can match records across languages; only localized strings (such as `title` and step `text`) should differ by locale.

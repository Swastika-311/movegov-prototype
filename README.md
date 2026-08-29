# LifeNav

LifeNav is a life-event government service navigator for citizens permanently moving between Indian cities. The prototype turns a relocation into one personalized, step-by-step journey instead of making users figure out which government services apply to them independently.

> **Prototype notice:** LifeNav is not a government website and does not represent or partner with any government department. Citizen, application, and profile data used by the prototype is synthetic. LifeNav does not submit applications, access government databases, or modify government records.

## What LifeNav does

LifeNav asks about a user's relocation and personal context, then builds a tailored list of relevant government-service actions. Each recommendation includes why it is relevant, applicability information, dependencies, requirements, and an official-source link.

The prototype currently covers these address-linked services:

- Aadhaar address update
- Voter residence/address update
- Vehicle RC address update
- Driving Licence address update
- Ration/benefit portability review
- PAN/address review

## Main user journey

```text
Home
  ↓
Relocation setup
  ↓
Personal context
  ↓
Build my plan
  ↓
Personalized LifeNav dashboard
  ↓
Journey tracker
  ↓
Ask LifeNav
```

### 1. Relocation setup

The user provides synthetic relocation information such as:

- Current city
- Destination city
- Move date
- Move type
- Reason for moving

### 2. Personal context

LifeNav uses simple questions to understand which services may apply:

- Vehicle ownership
- Voter registration
- Government benefits
- Student status
- Address-linked records that may need review

### 3. Personalized plan

Selecting **Build my plan** saves the profile and generates recommendations through the backend recommendation engine. Recommendations are deterministic and based on the user's profile and the service knowledge base.

### 4. Personalized dashboard

The dashboard shows:

- The user's relocation summary
- Number of relevant government-service actions
- Overall completion progress
- Personalized service cards
- Priority and applicability
- Why each service is relevant
- Official source links
- Service requirements and dependencies
- Application/tracker status

If no recommendations are available, the dashboard explicitly tells the user to review their personal-context answers instead of silently displaying an empty page.

### 5. Journey tracker checklist

The Journey Tracker converts the personalized recommendations into a simple checklist.

- Each recommended service appears as a checklist item.
- Users can mark an item **Done**.
- The status is persisted through the backend application tracker.
- Dashboard and Journey Tracker use the same stored status, so an item marked Done in one view is shown as Done in the other.
- Progress automatically reflects completed items.
- An item can be returned to **Not Started** if the user unchecks it.

The tracker is local prototype state. It is **not** connected to live government application-status systems.

### 6. Ask LifeNav

The assistant uses a retrieval-first approach and surfaces source information with answers. The default implementation is deterministic and metadata-backed so the prototype can run without an API key. An LLM can be placed behind the assistant interface without changing the rest of the application architecture.

## Architecture

```text
Streamlit UI
    ↓
FastAPI backend
    ↓
User/profile storage
    ↓
Recommendation engine
    ↓
Government service knowledge base
    ↓
Dependency + requirements data
    ↓
Application / checklist tracker
    ↓
Retrieval-first assistant
```

The frontend is implemented in Streamlit and communicates with the FastAPI backend over HTTP. The backend owns user/profile data, recommendations, service information, and application/checklist status.

## Government data and source policy

The prototype uses a structured local government-service dataset rather than accessing live government systems. Service records contain official-source references and metadata used by the recommendation and retrieval flows.

Where an exact current requirement can vary by state, RTO, workflow, portal configuration, or policy changes, LifeNav does not present the prototype's information as a guaranteed legal or administrative requirement. Users are directed to verify details through the linked official source before taking action.

The prototype does **not** scrape restricted government information and does not require access to personal government records.

## Running with Docker

From the repository root:

```bash
docker compose up --build
```

Then open:

- **LifeNav UI:** http://localhost:8501
- **FastAPI:** http://localhost:8000
- **API documentation:** http://localhost:8000/docs

For a clean local prototype database before end-to-end testing:

```bash
docker compose down -v
docker compose up --build
```

> `down -v` removes the Docker volume containing local prototype data. Use it when you intentionally want a fresh demo/test database.

## Local development

Use Python 3.11+.

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Then run the backend:

```bash
uvicorn app.api.main:app --reload
```

In another terminal, run the Streamlit frontend:

```bash
streamlit run frontend/streamlit_app.py
```

On Windows, if `cp` is unavailable, copy `.env.example` to `.env` manually.

## Testing

Run the test suite with:

```bash
pytest -q
```

For a Docker-based test environment, first start the services and then run the backend tests from the appropriate container, for example:

```bash
docker compose exec backend pytest -q
```

Use `docker compose ps` to confirm the backend service name if the Compose configuration uses a different service name.

## End-to-end demo test

A representative synthetic journey is:

1. Open `http://localhost:8501`.
2. Select **Start Relocation Journey**.
3. Enter a current city and destination city, such as `Prayagraj → Lucknow`.
4. Select a permanent move and provide a reason such as employment.
5. Complete Personal Context, for example vehicle = yes, voter = yes, benefits = yes.
6. Select **Build my plan**.
7. Confirm the Personalized Dashboard contains relevant government-service recommendations.
8. Open **Journey tracker**.
9. Mark a recommendation **Done**.
10. Return to the Dashboard and confirm the same service is shown as **Done** and the completion progress has increased.
11. Uncheck the item and confirm both views return it to **Not Started**.
12. Open a service's official-source link and verify the user is directed to the source rather than being told that LifeNav itself is an official government portal.

All test identities and relocation details should remain synthetic.

## Accessibility and low-bandwidth considerations

LifeNav is designed as a lightweight, form-driven prototype:

- Simple question-based navigation rather than complex forms
- Clear action labels such as **Build my plan** and **Mark as Done**
- High-contrast dark UI with light text and readable form controls
- Personalized recommendations instead of requiring users to search a large service catalogue
- Official-source links rather than embedding or scraping government portals
- No live government transaction is required for the core demo flow

The prototype should still be validated with users with limited digital experience before any production deployment.

## Safety and limitations

LifeNav is a navigation and coordination prototype. It:

- Does not submit government applications.
- Does not process payments or OTPs.
- Does not access government databases.
- Does not modify government records.
- Does not independently determine legal or government eligibility.
- Does not claim government affiliation or partnership.
- Does not provide live application status from government systems.
- Uses synthetic prototype data for citizen/profile/application information.

Government-service information and links can change. Users should verify current requirements on the relevant official government source before acting.

## Project status

The prototype demonstrates the complete product concept from relocation context to personalized recommendations and synchronized checklist tracking. Government transactions remain intentionally mocked/local so the hackathon demo does not interact with sensitive personal information or live government systems.

## License

See the repository's license and project files for applicable licensing information.

# Lexora legal dashboard

Phase 7 frontend for the AI Legal Document Analysis & Contract Assistant. This is a React + TypeScript + Vite client with an authenticated workspace shell, contract intake, source-grounded analysis, risk review, version comparison, assistant, obligation tracking, and administration views.

## Run locally

```bash
npm install
npm run dev
```

Set `VITE_API_URL` when the FastAPI API is not available at `http://localhost:8000/api/v1`.

The UI uses the Phase 6 JWT, contracts, legal analysis, risk review, and obligation endpoints. The current backend does not yet expose a document-upload endpoint, so upload intake currently prepares the file and contract metadata in the frontend and marks it ready for the backend processing integration. Analysis and review calls use the real API when authenticated; demo records keep the shell inspectable while the API is offline.
